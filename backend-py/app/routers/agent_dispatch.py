# app/routers/agent_dispatch.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError
import re

from app.config import settings
from app.models.schemas import BedrockResponse
from app.services.agent_runtime import collect_agent_response
from app.prompts.project_analysis_agent import (
    build_agent_project_analysis_input,
    SECTION_TITLES,
)
from app.prompts.cost_optimization_agent import (
    build_agent_cost_optimization_input,
    COST_SECTION_TITLES,
)
from app.prompts.executive_report_agent import (
    build_agent_executive_report_input,
    EXEC_SECTION_TITLES,
)
from app.utils.normalize import normalize_markdown_sections
def _extract_refusal(raw_text: str) -> str | None:
    lt = (raw_text or "").lower()
    if "sorry" in lt and ("unable" in lt or "i am unable" in lt or "i’m unable" in lt or "i'm unable" in lt):
        for line in (raw_text.splitlines() or []):
            if "sorry" in line.lower():
                return line.strip()
        return raw_text.strip()
    return None

router = APIRouter(prefix="/api/agent/dispatch", tags=["Agent Dispatch"])

class AgentDispatchRequest(BaseModel):
    userQuestion: str
    optionKey: str = "default"  # 'project_analysis' | 'default' | ...
    sessionId: Optional[str] = "default-session"

    # опционально, когда нужен «умный» промпт
    clientContext: Optional[Dict[str, Any]] = None
    level: Optional[Literal["brief", "detailed"]] = "brief"
    includeBenchmarks: Optional[bool] = True

INTENT_PATTERN = re.compile(
    r'(^|\s)(посчита[йть]|рассчита[йть]|расчет|оценк\w*|оценить|оцени(те)?|анализ\w*|'
    r'проанализируй|смета|смету|бюджет\w*|сроки|стоимост\w*|estimate|cost|price|budget|'
    r'analy[sz]e|analysis|timeline|scope|evaluate|estimat(e|ion))($|\s)', re.I
)
GREET_PATTERN = re.compile(
    r'^\s*(hi|hello|hey|привет|здравствуй|добрый\s+(день|вечер|утро))[\s!.,]*$',
    re.I
)

def is_analysis_intent(text: str) -> bool:
    if not text:
        return False
    if GREET_PATTERN.search(text):
        return False
    return bool(INTENT_PATTERN.search(text))

@router.post("", response_model=BedrockResponse)
def dispatch_agent(payload: AgentDispatchRequest):
    if settings.USE_MOCK_BEDROCK:
        return BedrockResponse(
            success=True,
            output=f"[MOCK_DISPATCH] key={payload.optionKey} q='{payload.userQuestion}'"
        )

    if not settings.BEDROCK_AGENT_ID or not settings.BEDROCK_AGENT_ALIAS_ID:
        raise HTTPException(status_code=400, detail="AGENT_ID или AGENT_ALIAS_ID не заданы в .env")

    try:
        option = (payload.optionKey or "default").lower()
        user_q = payload.userQuestion or ""
        session_id = payload.sessionId or "default-session"

        # Решение о включении анализа: делаем project_analysis авто по интенту
        if option in ("project_analysis", "auto"):
            use_analysis = is_analysis_intent(user_q)
        else:
            use_analysis = False

        if use_analysis:
            agent_input = build_agent_project_analysis_input(
                user_question=user_q,
                level=payload.level or "brief",
                ctx=payload.clientContext or {},
                include_benchmarks=True if payload.includeBenchmarks is None else payload.includeBenchmarks,
            )
            raw = collect_agent_response(agent_input, session_id)
            refusal = _extract_refusal(raw)
            if refusal:
                return BedrockResponse(success=True, output=f"{refusal} Please clarify your request.")
            normalized = normalize_markdown_sections(raw, SECTION_TITLES, skip_empty=True)
            return BedrockResponse(success=True, output=normalized)

        # Специальные режимы без интент-фильтра (включаются по ключу)
        if option == "cost_optimization":
            agent_input = build_agent_cost_optimization_input(
                user_question=user_q,
                level=payload.level or "brief",
                ctx=payload.clientContext or {},
            )
            raw = collect_agent_response(agent_input, session_id)
            refusal = _extract_refusal(raw)
            if refusal:
                return BedrockResponse(success=True, output=f"{refusal} Please clarify your request.")
            normalized = normalize_markdown_sections(raw, COST_SECTION_TITLES, skip_empty=True)
            return BedrockResponse(success=True, output=normalized)

        if option == "executive_report":
            agent_input = build_agent_executive_report_input(
                user_question=user_q,
                level=payload.level or "brief",
                ctx=payload.clientContext or {},
            )
            raw = collect_agent_response(agent_input, session_id)
            refusal = _extract_refusal(raw)
            if refusal:
                return BedrockResponse(success=True, output=f"{refusal} Please clarify your request.")
            normalized = normalize_markdown_sections(raw, EXEC_SECTION_TITLES, skip_empty=True)
            return BedrockResponse(success=True, output=normalized)

        # Обычный чат напрямую в агента
        raw = collect_agent_response(user_q, session_id)
        return BedrockResponse(success=True, output=raw)

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
