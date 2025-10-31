from fastapi import APIRouter, HTTPException
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError
from app.models.schemas import BedrockRequest, BedrockResponse
from app.services.bedrock_runtime import invoke_model_non_stream
from app.config import settings

router = APIRouter(prefix="/api/bedrock", tags=["bedrock"])

@router.post("", response_model=BedrockResponse)
def invoke_bedrock(payload: BedrockRequest):
    if settings.USE_MOCK_BEDROCK:
        prompt_preview = " | ".join(f"{m.role}:{m.content}" for m in (payload.messages or []))
        mock_text = f"[MOCK_MODEL] Ответ на prompt: {prompt_preview[:300]}"
        return BedrockResponse(success=True, output=mock_text)
    try:
        output = invoke_model_non_stream(
            [m.model_dump() for m in (payload.messages or [])],
            int(payload.maxTokens or 1024),
            float(payload.temperature or 0.7),
        )
        return BedrockResponse(success=True, output=output)
    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured.")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
