import os
import json
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

# ====== Настройка логирования ======
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("backend-py")

# ====== Загрузка .env (локально) ======
load_dotenv()  # загружает переменные окружения из backend-py/.env если есть

# ====== Конфигурация ======
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")
# Опция для разработки: если TRUE — вернёт мок вместо вызова Bedrock
USE_MOCK = os.getenv("USE_MOCK_BEDROCK", "false").lower() in ("1", "true", "yes")
PORT = int(os.getenv("PORT", "3000"))

# ====== Инициализация клиента boto3 (Bedrock Runtime) ======
# boto3 сам использует переменные окружения, ~/.aws/credentials или IAM роль
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Логируем источник кредов (если есть)
_session = boto3.Session()
_creds = _session.get_credentials()
if _creds:
    LOG.info("AWS credentials found (provider: %s)", type(_creds).__name__)
else:
    LOG.warning("AWS credentials NOT found. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or configure AWS CLI.")

# ====== FastAPI app ======
app = FastAPI(title="Bedrock Proxy (FastAPI)")

# Открываем CORS для разработки (в продакшне ограничь origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ====== Pydantic модели ======
class ChatMessage(BaseModel):
    role: str  # 'User' or 'Assistant'
    content: str


class BedrockRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = []
    maxTokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7



class BedrockResponse(BaseModel):
    success: bool
    output: str


# ====== Вспомогательные функции ======
def extract_text_from_bedrock_response(response: dict) -> str:
    """
    Извлекает текст из ответа boto3 invoke_model.
    Ответ может иметь тело в виде stream, bytes или других форм.
    Возвращает строку (пустую, если не удалось извлечь).
    """
    # boto3 response обычно содержит 'body' как StreamingBody или bytes-like
    raw_bytes = b""

    body = response.get("body") if isinstance(response, dict) else None

    # try read StreamingBody
    try:
        if hasattr(body, "read"):
            raw_bytes = body.read()
        elif isinstance(body, (bytes, bytearray)):
            raw_bytes = bytes(body)
        elif body is None:
            # иногда SDK возвращает тело в других полях; смотрим весь ответ
            # как fallback — пытаемся сериализовать response
            raw_bytes = json.dumps(response).encode("utf-8")
        else:
            raw_bytes = str(body).encode("utf-8")
    except Exception as e:
        LOG.exception("Error while reading response body: %s", e)
        # fallback to stringify
        raw_bytes = str(response).encode("utf-8")

    try:
        text = raw_bytes.decode("utf-8")
    except Exception:
        # если текст не декодируется — возвращаем repr
        text = repr(raw_bytes)
    return text


# ====== Endpoints ======
@app.get("/api/health")
def health():
    """
    Простая проверка состояния сервера (не проверяет Bedrock).
    """
    return {"ok": True, "region": AWS_REGION, "model": MODEL_ID, "mock": USE_MOCK}


@app.post("/api/bedrock", response_model=BedrockResponse)
def invoke_bedrock(payload: BedrockRequest):
    """
    Основной endpoint: принимает список сообщений, формирует prompt и вызывает Bedrock.
    Возвращает текстовую строку в поле `output`.
    """
    # DEV: если включён мок — вернём фиктивный ответ (полезно при разработке без кредов)
    if USE_MOCK:
        LOG.info("USE_MOCK_BEDROCK is enabled — returning mock response.")
        prompt_preview = " | ".join(f"{m.role}:{m.content}" for m in (payload.messages or []))
        mock_text = f"[MOCK] Ответ на prompt: {prompt_preview[:300]}"
        return BedrockResponse(success=True, output=mock_text)

    # Формируем prompt: адаптируй под ту модель, которую используешь
    messages = payload.messages or []
    prompt = "\n".join(f"{m.role}: {m.content}" for m in messages) + "\nAssistant:"

    # Тело для invoke_model — подстраивай под требования модели
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": int(payload.maxTokens or 1024),
            "temperature": float(payload.temperature or 0.7),
        },
    }

    try:
        # Убедимся, что креды есть — более дружелюбная ошибка
        session = boto3.Session()
        if not session.get_credentials():
            LOG.warning("No AWS credentials available when calling /api/bedrock")
            raise NoCredentialsError()

        LOG.info("Invoking Bedrock model: %s (prompt len=%d)", MODEL_ID, len(prompt))
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            body=json.dumps(body).encode("utf-8"),
        )

        raw_text = extract_text_from_bedrock_response(response)
        LOG.debug("Raw response text (first 500 chars): %s", raw_text[:500])

        # Попробуем распарсить JSON, если модель вернула JSON-структуру
        output = raw_text
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                # Стандартные варианты: parsed.outputs or parsed.generatedText
                if "outputs" in parsed:
                    parts: List[str] = []
                    for out in parsed.get("outputs", []):
                        for c in out.get("content", []):
                            # content может содержать 'text' или 'body' в зависимости от модели
                            parts.append(c.get("text") or c.get("body") or "")
                    output = "".join(parts).strip()
                elif "generatedText" in parsed:
                    output = str(parsed.get("generatedText"))
                else:
                    # если dict, но нет ожидаемых полей — stringify
                    output = json.dumps(parsed)
        except Exception:
            # если не JSON — оставляем сырой текст
            output = raw_text

        return BedrockResponse(success=True, output=output)

    except NoCredentialsError:
        LOG.exception("Bedrock client error - No AWS credentials")
        raise HTTPException(
            status_code=401,
            detail="AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure AWS CLI."
        )
    except (BotoCoreError, ClientError) as e:
        LOG.exception("Bedrock client error: %s", e)
        # возвращаем 502 Bad Gateway для ошибок взаимодействия с Bedrock
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        LOG.exception("Unexpected error in /api/bedrock: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ====== Запуск (если запускаешь через python app.py) ======
if __name__ == "__main__":
    # Удобный запуск для разработки: `python app.py`
    import uvicorn

    LOG.info("Starting uvicorn on 127.0.0.1:%d (mock=%s)", PORT, USE_MOCK)
    uvicorn.run("app:app", host="127.0.0.1", port=PORT, reload=True)
