from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import urlparse

import boto3

from app.config import settings


# ---------- Boto3 session & clients ----------


def _make_session() -> boto3.Session:
    """
    Create a boto3 session.
    Prefers explicit AWS keys; falls back to profile or instance role.
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
    Convert s3://bucket/key into a temporary HTTPS URL.
    """
    if not s3_uri:
        return ""

    parsed = urlparse(s3_uri)
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


# ---------- Retrieval from Knowledge Base ----------


def retrieve_kb_chunks(
    query: str,
    k: int = 8,
    kb_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k chunks from Bedrock Knowledge Base.
    Returns [{"text": str, "score": float, "s3_uri": Optional[str]}, ...].
    """
    kb_id = kb_id or settings.BEDROCK_KB_ID
    if not kb_id:
        raise ValueError("Knowledge Base ID is not configured (set BEDROCK_KB_ID).")

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
    Render retrieved KB chunks into a text block for the system prompt.
    """
    if not chunks:
        return "No relevant documents found in the Knowledge Base for this query."

    blocks: List[str] = []
    for i, ch in enumerate(chunks, start=1):
        text = (ch.get("text") or "")[:max_chars_per_chunk]
        s3_uri = ch.get("s3_uri")

        source_line = ""
        if include_sources:
            if s3_uri:
                presigned = presign_s3(s3_uri)
                source_line = f"Source: {presigned}\n" if presigned else "Source: (unavailable)\n"

        block = f"[Doc {i}]\n"
        if include_sources and source_line:
            block += source_line
        block += f"Excerpt:\n{text}"
        blocks.append(block)

    return "\n\n".join(blocks)


def _normalize_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Keep only user/assistant messages with non-empty content and normalize roles.
    """
    formatted: List[Dict[str, str]] = []
    for msg in messages:
        role = (msg.get("role") or "").lower()
        content = (msg.get("content") or "").strip()
        if not content or role not in ("user", "assistant"):
            continue
        formatted.append({"role": role, "content": content})

    if not formatted:
        raise ValueError("At least one user message is required for the model call")
    return formatted


# ---------- Invoke Claude (Anthropic) via Bedrock ----------


def call_llm_claude(
    system_prompt: str,
    messages: List[Dict[str, str]],
    *,
    max_tokens: int = 900,
    temperature: float = 0.0,
) -> str:
    """
    Non-streaming invocation of Claude 3.x on Bedrock Runtime.
    """
    client = llm_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": _normalize_messages(messages),
    }

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
    messages: List[Dict[str, str]],
    *,
    max_tokens: int = 900,
    temperature: float = 0.0,
) -> Generator[str, None, None]:
    """
    Streaming invocation of Claude 3.x on Bedrock Runtime.
    """
    client = llm_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": _normalize_messages(messages),
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
