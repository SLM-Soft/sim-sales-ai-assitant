from __future__ import annotations

import base64
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import NoCredentialsError, BotoCoreError, ClientError

from app.schemas.chat import Attachment, ChatRequest, ChatResponse
from app.core.bedrock import (
    retrieve_kb_chunks,
    build_dataset_block,
    call_llm_claude,
    stream_llm_claude,
)
from app.prompts.registry import get_prompt_config, build_system_prompt

router = APIRouter(prefix="/api/chat", tags=["chat"])

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
PDF_FONT_PATH = ASSETS_DIR / "fonts" / "Roboto-Regular.ttf"
PDF_LOGO_PATH = ASSETS_DIR / "logo.png"
PDF_FONT_NAME = "CustomRoboto"
PDF_HEADER_TITLE = "Powered by SLM Assistant"


def _needs_pdf(text: str) -> bool:
    """
    Lightweight heuristic to detect that the user explicitly asks for a PDF file.
    """
    if not text:
        return False

    normalized = text.lower()
    return bool(
        re.search(r"\bpdf\b", normalized)
        or "пдф" in normalized
        or "pdf-файл" in normalized
        or "пдф-файл" in normalized
        or "сгенерируй pdf" in normalized
        or "создай pdf" in normalized
        or "скач" in normalized  # covers "скачай", "скачать"
    )


def _clean_pdf_body(text: str) -> str:
    """
    Remove common preambles and return the likely body for PDF.
    """
    if not text:
        return ""

    lowered = text.lower()
    markers = [
        "текст для pdf:",
        "текст для pdf",
        "для pdf:",
        "вот полный текст",
        "вот текст",
    ]
    for marker in markers:
        idx = lowered.find(marker)
        if idx != -1:
            return text[idx + len(marker) :].lstrip(" :\n\t")

    return text.lstrip()


def _slugify_filename(text: str, default: str = "answer") -> str:
    cleaned = re.sub(r"[^0-9A-Za-zА-Яа-яЁё]+", " ", text or "", flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = cleaned[:60] or default
    return cleaned


def _build_pdf_attachment(title: str, body: str, *, filename_hint: str | None = None) -> Attachment | None:
    """
    Create a PDF (base64) from the provided title/body using a Unicode-capable font.
    """
    try:
        from fpdf import FPDF  # type: ignore
    except Exception:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    if PDF_FONT_PATH.exists():
        pdf.add_font(PDF_FONT_NAME, "", str(PDF_FONT_PATH), uni=True)
        pdf.add_font(PDF_FONT_NAME, "B", str(PDF_FONT_PATH), uni=True)
        pdf.set_font(PDF_FONT_NAME, "B", size=16)
    else:
        pdf.set_font("Arial", "B", size=16)

    # Optional logo
    if PDF_LOGO_PATH.exists():
        try:
            pdf.image(str(PDF_LOGO_PATH), w=28)
            pdf.ln(4)
        except Exception:
            pass

    # Header title
    pdf.cell(0, 10, PDF_HEADER_TITLE, ln=1)
    pdf.ln(4)

    # Body font
    if PDF_FONT_PATH.exists():
        pdf.set_font(PDF_FONT_NAME, "", size=12)
    else:
        pdf.set_font("Arial", size=12)

    cleaned_body = _clean_pdf_body(body)
    content = cleaned_body.strip() or "Ответ пуст."

    try:
        pdf.multi_cell(0, 8, content)
    except UnicodeEncodeError:
        safe = content.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 8, safe)

    output_obj = pdf.output(dest="S")
    if isinstance(output_obj, (bytes, bytearray)):
        raw_bytes = bytes(output_obj)
    else:
        # PyFPDF may return str in some environments; encode as latin-1 per docs
        raw_bytes = str(output_obj).encode("latin-1")
    encoded = base64.b64encode(raw_bytes).decode("ascii")

    base_name = _slugify_filename(filename_hint or title)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{base_name}-{timestamp}.pdf"
    return Attachment(
        fileName=filename,
        mimeType="application/pdf",
        base64=encoded,
    )


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
        user_prompt = (
            "User question is below. If the user asks for PDF, provide the full content for the PDF.\n"
            "Do not say you cannot generate PDFs; the system will create the PDF file from your text.\n"
            "If asked for PDF, reply ONLY with the PDF-ready body (no intro, no apologies).\n"
            f"User question:\n\"\"\"{payload.userQuestion}\"\"\""
        )

        # 4) Вызов LLM
        answer = call_llm_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

        attachment = None
        if _needs_pdf(payload.userQuestion):
            attachment = _build_pdf_attachment(
                title=PDF_HEADER_TITLE,
                body=answer,
                filename_hint=payload.userQuestion,
            )

        return ChatResponse(
            outputText=answer,
            optionKey=payload.optionKey,
            sessionId=payload.sessionId,
            attachment=attachment,
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
        user_prompt = (
            "User question is below. If the user asks for PDF, provide the full content for the PDF.\n"
            "Do not say you cannot generate PDFs; the system will create the PDF file from your text.\n"
            "If asked for PDF, reply ONLY with the PDF-ready body (no intro, no apologies).\n"
            f"User question:\n\"\"\"{payload.userQuestion}\"\"\""
        )

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
