from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError

from app.schemas.chat import ChatRequest, ChatResponse
from app.core.bedrock import (
    retrieve_kb_chunks,
    build_dataset_block,
    call_llm_claude,
    stream_llm_claude,
)
from app.prompts.registry import get_prompt_config, build_system_prompt

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_handler(payload: ChatRequest) -> ChatResponse:
    """
    Обычный (не стриминговый) ответ.
    """
    try:
        cfg = get_prompt_config(payload.optionKey)
        if not cfg:
            raise HTTPException(status_code=400, detail=f"Unknown optionKey: {payload.optionKey}")

        # 1) KB retrieval (если нужно)
        dataset = None
        if cfg.use_kb:
            chunks = retrieve_kb_chunks(payload.userQuestion, k=8)
            dataset = build_dataset_block(
                chunks,
                include_sources=cfg.include_sources,
            )

        # 2) System prompt
        system_prompt = build_system_prompt(cfg, dataset)

        # 3) User prompt
        user_prompt = f"User question:\n\"\"\"{payload.userQuestion}\"\"\""

        # 4) Вызов LLM
        answer = call_llm_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
def chat_stream_handler(payload: ChatRequest):
    """
    Стриминговый ответ (chunk by chunk).
    Возвращает text/plain, можно читать по кусочкам на фронте.
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
        user_prompt = f"User question:\n\"\"\"{payload.userQuestion}\"\"\""

        def _gen():
            for chunk in stream_llm_claude(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=cfg.max_tokens,
                temperature=cfg.temperature,
            ):
                yield chunk

        return StreamingResponse(_gen(), media_type="text/plain; charset=utf-8")

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="AWS credentials not configured")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
