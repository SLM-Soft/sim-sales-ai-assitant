from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError

from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.core.bedrock import (
    retrieve_kb_chunks,
    build_dataset_block,
    call_llm_claude,
    stream_llm_claude,
)
from app.prompts.registry import get_prompt_config, build_system_prompt

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

        system_prompt = build_system_prompt(cfg, dataset)
        system_prompt = (
            f"{system_prompt}\n\n"
            "Conversation rules:\n"
            "- If the user asks for a PDF, provide the full PDF-ready body text. Do not apologize.\n"
            "- Stay within the shared conversation context.\n"
            "- Keep answers concise and actionable."
        )
        messages = _build_messages(payload)

        answer = call_llm_claude(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

        return ChatResponse(
            outputText=answer,
            optionKey=payload.optionKey,
            sessionId=payload.sessionId,
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
