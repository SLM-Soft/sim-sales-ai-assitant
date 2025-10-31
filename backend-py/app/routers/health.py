from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health():
    return {
        "ok": True,
        "region": settings.AWS_REGION,
        "model": settings.BEDROCK_MODEL_ID,
        "mock": settings.USE_MOCK_BEDROCK,
        "agent_id": settings.BEDROCK_AGENT_ID,
        "agent_alias_id": settings.BEDROCK_AGENT_ALIAS_ID,
    }
