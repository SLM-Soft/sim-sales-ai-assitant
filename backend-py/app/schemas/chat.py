from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class Attachment(BaseModel):
    fileName: str = Field(..., description="User-facing file name, e.g. answer.pdf")
    mimeType: str = Field(..., description="Content type of the attachment, e.g. application/pdf")
    base64: str = Field(..., description="Base64-encoded file content")


class ChatRequest(BaseModel):
    userQuestion: str = Field(..., description="Вопрос пользователя")
    optionKey: str = Field(..., description="Ключ промпта (sales, project_analysis и т.п.)")
    sessionId: Optional[str] = Field(None, description="Сессия чата (для фронта)")
    stream: bool = Field(False, description="Нужен ли стриминговый ответ")


class ChatResponse(BaseModel):
    outputText: str
    optionKey: str
    sessionId: Optional[str] = None
    attachment: Optional[Attachment] = Field(
        None,
        description="Optional attachment (e.g. generated PDF) to return along with the answer",
    )
