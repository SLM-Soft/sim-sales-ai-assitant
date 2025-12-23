from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import base64
import json as _json

from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError

from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.core.bedrock import (
    retrieve_kb_chunks,
    build_dataset_block,
    call_llm_claude,
    stream_llm_claude,
)
from app.prompts.registry import get_prompt_config, build_system_prompt
from app.prompts.pdf_prompt import build_pdf_prompt
from app.core.pdf_builder import build_pdf_from_spec

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _build_messages(payload: ChatRequest) -> List[Dict[str, str]]:
    """
    Merge client-provided history with the current user question so Claude
    receives full conversation context.
    """
    history: List[ChatMessage] = payload.messages or []
    messages: List[Dict[str, str]] = [
        {"role": msg.role, "content": msg.content}
        for msg in history
        if (msg.content or "").strip()
    ]

    final_user = (payload.userQuestion or "").strip()
    if final_user:
        needs_append = (
            not messages
            or messages[-1]["role"].lower() != "user"
            or messages[-1]["content"].strip() != final_user
        )
        if needs_append:
            messages.append({"role": "User", "content": final_user})

    return messages


def _extract_first_json_object(text: str) -> Optional[str]:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


@router.post("", response_model=ChatResponse)
def chat_handler(payload: ChatRequest) -> ChatResponse:
    """
    Обработчик обычного чата (одним ответом).
    """
    try:
        cfg = get_prompt_config(payload.optionKey)
        if not cfg:
            raise HTTPException(status_code=400, detail=f"Unknown optionKey: {payload.optionKey}")

        dataset = None
        if cfg.use_kb:
            chunks = retrieve_kb_chunks(payload.userQuestion, k=8)
            dataset = build_dataset_block(
                chunks,
                include_sources=cfg.include_sources,
            )

        follow_prompt = (
            "Generate up to 3 concise, content-specific follow-up questions that deepen the topic. "
            "Avoid meta questions about the conversation, the PDF, or asking if the user wants more. "
            "Use the same language as the most recent user message. Return only the questions as a JSON array "
            "immediately after the marker FOLLOW_UPS_JSON:, without markdown, links, or extra prose."
        )

        follow_section = (
            "\n- After the main answer, generate up to 3 short follow-up questions based on this instruction: "
            f"\"{follow_prompt}\""
            "\n- Return follow-ups as a JSON array (no markdown, no prose) immediately after the marker FOLLOW_UPS_JSON:"
        )

        system_prompt = build_system_prompt(cfg, dataset)
        system_prompt = (
            f"{system_prompt}\n\n"
            "Conversation rules:\n"
            "- Stay within the shared conversation context.\n"
            "- Keep answers concise and actionable.\n"
            "- Never describe UI actions such as clicking buttons, downloading files, or saving PDFs.\n"
            "- For trivial or common-knowledge questions, answer directly without mentioning the Knowledge Base and do not include follow-ups.\n"
            "\n"
            f"{build_pdf_prompt()}"
            f"{follow_section}"
        )
        messages = _build_messages(payload)

        answer = call_llm_claude(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

        # Lightweight extraction: look for markers and parse trailing JSON blocks.
        followups: Optional[list[str]] = None
        pdf_base64: Optional[str] = None

        marker = "FOLLOW_UPS_JSON:"
        visible_answer = answer
        if marker in answer:
            try:
                visible_answer, json_blob = answer.split(marker, 1)
                json_part = json_blob.strip()
                parsed = _json.loads(json_part)
                if isinstance(parsed, list):
                    followups = [str(x) for x in parsed][:3]
            except Exception:
                visible_answer = answer
                followups = None

        # Parse optional PDF spec from visible_answer (must come before follow‑ups).
        pdf_marker = "PDF_DOC_JSON:"
        if pdf_marker in visible_answer:
            try:
                text_part, pdf_blob = visible_answer.split(pdf_marker, 1)
                pdf_json = pdf_blob.strip()
                # If someone accidentally appended follow‑ups after the JSON in the same block,
                # cut off at the follow‑ups marker defensively.
                if marker in pdf_json:
                    pdf_json, _ = pdf_json.split(marker, 1)
                json_object = _extract_first_json_object(pdf_json) or pdf_json
                spec = _json.loads(json_object)
                pdf_bytes = build_pdf_from_spec(spec)
                pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")
                visible_answer = text_part
            except Exception:
                # On any parsing/build failure, fall back to plain text answer.
                pdf_base64 = None

        return ChatResponse(
            outputText=visible_answer.strip(),
            optionKey=payload.optionKey,
            sessionId=payload.sessionId,
            followUps=followups,
            pdfBase64=pdf_base64,
        )

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
def chat_stream_handler(payload: ChatRequest):
    """
    Обработчик потокового чата (chunk by chunk).
    """
    try:
        cfg = get_prompt_config(payload.optionKey)
        if not cfg:
            raise HTTPException(status_code=400, detail=f"Unknown optionKey: {payload.optionKey}")

        dataset = None
        if cfg.use_kb:
            chunks = retrieve_kb_chunks(payload.userQuestion, k=8)
            dataset = build_dataset_block(
                chunks,
                include_sources=cfg.include_sources,
            )

        system_prompt = build_system_prompt(cfg, dataset)
        system_prompt = (
            f"{system_prompt}\n\n"
            "Conversation rules:\n"
            "- If the user asks for a PDF, provide the full PDF-ready body text. Do not apologize.\n"
            "- Stay within the shared conversation context.\n"
            "- Keep answers concise and actionable."
        )
        messages = _build_messages(payload)

        def _gen():
            for chunk in stream_llm_claude(
                system_prompt=system_prompt,
                messages=messages,
                max_tokens=cfg.max_tokens,
                temperature=cfg.temperature,
            ):
                yield chunk

        return StreamingResponse(_gen(), media_type="text/plain; charset=utf-8")

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
