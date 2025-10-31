# app/services/agent_runtime.py
import json
from typing import Generator, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.config import settings

def _bytes_to_text_safe(b: Optional[bytes]) -> str:
    if not b:
        return ""
    try:
        return b.decode("utf-8", errors="ignore")
    except Exception:
        try:
            return b.decode("latin-1", errors="ignore")
        except Exception:
            return ""

def _extract_text_from_json_like(s: str) -> Optional[str]:
    """
    Агент иногда шлёт JSON фрагменты. Пытаемся вытащить текст.
    """
    s = s.strip()
    if not s:
        return None
    try:
        obj = json.loads(s)
        for key in ("text", "content", "message", "output", "outputText"):
            v = obj.get(key)
            if isinstance(v, str) and v.strip():
                return v
        return s
    except Exception:
        return None

def collect_agent_response(input_text: str, session_id: str = "default-session") -> str:
    """
    Синхронная сборка всего EventStream в одну строку.
    """
    if settings.USE_MOCK_BEDROCK:
        return f"[MOCK_AGENT] {input_text[:200]}"

    if not settings.BEDROCK_AGENT_ID or not settings.BEDROCK_AGENT_ALIAS_ID:
        raise ValueError("BEDROCK_AGENT_ID/ALIAS_ID not configured")

    client = boto3.client("bedrock-agent-runtime", region_name=settings.AWS_REGION)

    response = client.invoke_agent(
        agentId=settings.BEDROCK_AGENT_ID,
        agentAliasId=settings.BEDROCK_AGENT_ALIAS_ID,
        sessionId=session_id or "default-session",
        inputText=input_text,
    )

    event_stream = response.get("completion")
    if not event_stream:
        return "[Empty event stream]"

    collected: str = ""
    for event in event_stream:
        event_type = next(iter(event.keys()))
        data = event[event_type]
        b = data.get("bytes") if isinstance(data, dict) else None

        if event_type in ("chunk", "finalResponse"):
            if not b:
                continue
            s = _bytes_to_text_safe(b)
            j = _extract_text_from_json_like(s)
            collected += j if j is not None else s
        # иные типы (trace/metadata/ошибки) игнорим или логируем при необходимости

    return collected.strip() or "[No text content returned by agent]"

def stream_agent_response(input_text: str, session_id: str = "default-session") -> Generator[str, None, None]:
    """
    Генератор для стриминга чанков в реальном времени.
    Возвращает строки (текстовые чанки), готовые к отдаче в StreamingResponse.
    """
    if settings.USE_MOCK_BEDROCK:
        mock = "[MOCK_AGENT_STREAM] " + input_text[:100]
        # имитируем поток по словам
        for w in mock.split():
            yield w + " "
        return

    if not settings.BEDROCK_AGENT_ID or not settings.BEDROCK_AGENT_ALIAS_ID:
        yield "[Agent config error: BEDROCK_AGENT_ID/ALIAS_ID not set]"
        return

    client = boto3.client("bedrock-agent-runtime", region_name=settings.AWS_REGION)

    try:
        response = client.invoke_agent(
            agentId=settings.BEDROCK_AGENT_ID,
            agentAliasId=settings.BEDROCK_AGENT_ALIAS_ID,
            sessionId=session_id or "default-session",
            inputText=input_text,
        )

        event_stream = response.get("completion")
        if not event_stream:
            yield "[Empty event stream]"
            return

        for event in event_stream:
            event_type = next(iter(event.keys()))
            data = event[event_type]
            b = data.get("bytes") if isinstance(data, dict) else None

            if event_type in ("chunk", "finalResponse"):
                if not b:
                    continue
                s = _bytes_to_text_safe(b)
                j = _extract_text_from_json_like(s)
                out = j if j is not None else s
                if out:
                    # отдаём порциями как есть (без буферизации на стороне сервиса)
                    yield out

            # trace/metadata/ошибки — по желанию можно логировать

    except NoCredentialsError:
        yield "[Credentials error: AWS credentials not configured]"
    except (BotoCoreError, ClientError) as e:
        yield f"[Agent error] {str(e)}"
    except Exception as e:
        yield f"[Unexpected error] {str(e)}"
