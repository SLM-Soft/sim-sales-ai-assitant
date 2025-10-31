import json
import logging
from typing import List, Dict, Any

from app.config import settings
from app.services._boto import bedrock_runtime_client

LOG = logging.getLogger("backend-py")
bedrock = bedrock_runtime_client()

def extract_text_from_bedrock_response(response: dict) -> str:
    raw_bytes = b""
    body = response.get("body") if isinstance(response, dict) else None
    try:
        if hasattr(body, "read"):
            raw_bytes = body.read()
        elif isinstance(body, (bytes, bytearray)):
            raw_bytes = bytes(body)
        elif body is None:
            raw_bytes = json.dumps(response).encode("utf-8")
        else:
            raw_bytes = str(body).encode("utf-8")
    except Exception:
        raw_bytes = str(response).encode("utf-8")
    try:
        return raw_bytes.decode("utf-8")
    except Exception:
        return repr(raw_bytes)

def build_prompt(messages: List[Dict[str, Any]]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages) + "\nAssistant:"

def invoke_model_non_stream(messages: List[Dict[str, Any]], max_tokens: int, temperature: float) -> str:
    prompt = build_prompt(messages)
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": int(max_tokens),
            "temperature": float(temperature),
        },
    }
    LOG.info("Invoking Bedrock model: %s (prompt len=%d)", settings.BEDROCK_MODEL_ID, len(prompt))
    response = bedrock.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        contentType="application/json",
        body=json.dumps(body).encode("utf-8"),
    )
    raw_text = extract_text_from_bedrock_response(response)
    # «мягкий» парс как у тебя
    try:
        parsed = json.loads(raw_text)
        if "outputs" in parsed:
            parts: List[str] = []
            for out in parsed["outputs"]:
                for c in out.get("content", []):
                    parts.append(c.get("text") or c.get("body") or "")
            return "".join(parts).strip()
        elif "generatedText" in parsed:
            return parsed["generatedText"]
    except Exception:
        pass
    return raw_text
