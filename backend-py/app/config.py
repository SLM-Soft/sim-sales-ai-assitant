from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # === AWS ===
    AWS_REGION: str = "eu-central-1"

    # ⬇️ key from env
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_SESSION_TOKEN: str | None = None

    # optional profile name
    AWS_PROFILE: str | None = None

    # === Bedrock/Agent ===
    BEDROCK_MODEL_ID: str = "amazon.titan-text-express-v1"
    BEDROCK_AGENT_ID: str | None = None
    BEDROCK_AGENT_ALIAS_ID: str | None = None

    USE_MOCK_BEDROCK: bool = False
    PORT: int = 3000
    APP_NAME: str = "Bedrock Proxy (FastAPI)"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
