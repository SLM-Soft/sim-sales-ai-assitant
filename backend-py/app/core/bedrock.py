from __future__ import annotations

import json
from typing import List, Dict, Any, Optional, Generator
from urllib.parse import urlparse

import boto3

from app.config import settings


# ---------- Boto3 session & клиенты ----------


def _make_session() -> boto3.Session:
    """
    Создаём сессию с учётом явных ключей (локально)
    и дефолтных провайдеров (EC2/ECS/SSO и т.п.).
    """
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        return boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION,
        )
    if settings.AWS_PROFILE:
        return boto3.Session(profile_name=settings.AWS_PROFILE, region_name=settings.AWS_REGION)
    return boto3.Session(region_name=settings.AWS_REGION)


def kb_client():
    return _make_session().client("bedrock-agent-runtime", region_name=settings.AWS_REGION)


def llm_client():
    return _make_session().client("bedrock-runtime", region_name=settings.AWS_REGION)


def s3_client():
    return _make_session().client("s3", region_name=settings.AWS_REGION)


# ---------- Presign S3 ----------


def presign_s3(s3_uri: str, expires_in: int = 3600) -> str:
    """
    Делает из s3://bucket/key временный HTTPS URL.
    """
    if not s3_uri:
        return ""

    parsed = urlparse(s3_uri)
    # ожидаем формат s3://bucket/key
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        return ""

    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    client = s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )
    return url


# ---------- Retrieval из Knowledge Base ----------


def retrieve_kb_chunks(
    query: str,
    k: int = 8,
    kb_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Достаём топ-K чанков из Bedrock Knowledge Base.
    Формат каждого чанка: { "text": "...", "score": float, "s3_uri": Optional[str] }
    """
    kb_id = kb_id or settings.BEDROCK_KB_ID
    if not kb_id:
        return []

    client = kb_client()

    resp = client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": k}
        },
    )

    chunks: List[Dict[str, Any]] = []
    for item in resp.get("retrievalResults", []):
        content = item.get("content", {}) or {}
        text = content.get("text", "")
        score = float(item.get("score", 0.0))

        location = item.get("location", {}) or {}
        s3_loc = location.get("s3Location", {}) or {}
        s3_uri = s3_loc.get("uri")

        if text:
            chunks.append({
                "text": text,
                "score": score,
                "s3_uri": s3_uri,
            })

    return chunks


def build_dataset_block(
    chunks: List[Dict[str, Any]],
    *,
    max_chars_per_chunk: int = 1800,
    include_sources: bool = False,
) -> str:
    """
    Превращаем чанки KB в один текстовый блок для system prompt.

    Если include_sources=True, добавляет строки Source: <presigned S3 URL>.
    """
    if not chunks:
        # важно: совпадает с текстом в правилах для sales-промпта
        return "No relevant documents found in the Knowledge Base for this query."

    blocks: List[str] = []
    for i, ch in enumerate(chunks, start=1):
        text = (ch.get("text") or "")[:max_chars_per_chunk]
        s3_uri = ch.get("s3_uri")

        source_line = ""
        if include_sources:
            if s3_uri:
                presigned = presign_s3(s3_uri)
                if presigned:
                    source_line = f"Source: {presigned}\n"
                else:
                    source_line = "Source: (unavailable)\n"

        block = f"[Doc {i}]\n"
        if include_sources:
            block += source_line
        block += f"Excerpt:\n{text}"
        blocks.append(block)

    return "\n\n".join(blocks)


# ---------- Вызов Claude (Anthropic) через Bedrock ----------


def call_llm_claude(
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int = 900,
    temperature: float = 0.0,
) -> str:
    """
    Нестрриминговый вызов Claude 3.x через Bedrock Runtime
    в нативном формате AWS для Anthropic.
    """
    client = llm_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        # system — строка
        "system": system_prompt,
        # messages — массив, content — строка
        "messages": [
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    }

    # debug при необходимости:
    # print("DEBUG MODEL:", settings.BEDROCK_MODEL_ID)
    # print("DEBUG BODY:", json.dumps(body, indent=2, ensure_ascii=False))

    resp = client.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(body),
    )

    raw = resp["body"].read().decode("utf-8")
    data = json.loads(raw)

    parts = [
        c.get("text", "")
        for c in data.get("content", [])
        if c.get("type") == "text"
    ]
    return "".join(parts).strip()


def stream_llm_claude(
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int = 900,
    temperature: float = 0.0,
) -> Generator[str, None, None]:
    """
    Стриминговый вызов Claude 3.x через Bedrock Runtime (chunk by chunk).
    Можно оборачивать в StreamingResponse.
    """
    client = llm_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    }

    resp = client.invoke_model_with_response_stream(
        modelId=settings.BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(body),
    )

    stream = resp.get("body")
    if not stream:
        return

    for event in stream:
        chunk = event.get("chunk")
        if not chunk:
            continue
        raw = chunk.get("bytes")
        if not raw:
            continue

        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            continue

        for c in data.get("content", []):
            if c.get("type") == "text":
                text = c.get("text", "")
                if text:
                    yield text
