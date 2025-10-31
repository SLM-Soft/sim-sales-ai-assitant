import boto3
from app.config import settings

def make_session() -> boto3.Session:
    """
    Создаёт boto3.Session, используя приоритет:
    1) AWS_PROFILE (если задан)
    2) Явные ключи из .env (AWS_ACCESS_KEY_ID/SECRET/SESSION_TOKEN)
    3) Фолбэк: обычная env-конфигурация
    """
    if settings.AWS_PROFILE:
        return boto3.Session(profile_name=settings.AWS_PROFILE, region_name=settings.AWS_REGION)

    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        return boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION,
        )

    # Фолбэк: boto3 сам возьмёт из env/EC2 metadata и т.д.
    return boto3.Session(region_name=settings.AWS_REGION)

def bedrock_runtime_client():
    return make_session().client("bedrock-runtime", region_name=settings.AWS_REGION)

def bedrock_agent_client():
    return make_session().client("bedrock-agent-runtime", region_name=settings.AWS_REGION)
