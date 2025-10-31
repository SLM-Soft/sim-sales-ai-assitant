from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError
from app.models.schemas import AgentRequest, BedrockResponse
from app.services.agent_runtime import collect_agent_response, stream_agent_response
from app.config import settings

router = APIRouter(prefix="/api/agent", tags=["agent"])

@router.post("", response_model=BedrockResponse)
def invoke_agent(payload: AgentRequest):
    if settings.USE_MOCK_BEDROCK:
        return BedrockResponse(success=True, output=f"[MOCK_AGENT] Ответ на '{payload.inputText}'")
    if not settings.BEDROCK_AGENT_ID or not settings.BEDROCK_AGENT_ALIAS_ID:
        raise HTTPException(status_code=400, detail="AGENT_ID или AGENT_ALIAS_ID не заданы в .env")
    try:
        out = collect_agent_response(payload.inputText, payload.sessionId or "default-session")
        return BedrockResponse(success=True, output=out)
    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
def invoke_agent_stream(payload: AgentRequest):
    if not settings.BEDROCK_AGENT_ID or not settings.BEDROCK_AGENT_ALIAS_ID:
        raise HTTPException(status_code=400, detail="AGENT_ID или AGENT_ALIAS_ID не заданы в .env")
    gen = stream_agent_response(payload.inputText, payload.sessionId)
    return StreamingResponse(
        gen,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
