from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    userQuestion: str = Field(..., description="Вопрос пользователя")
    optionKey: str = Field(..., description="Ключ промпта (sales, project_analysis и т.п.)")
    sessionId: Optional[str] = Field(None, description="Сессия чата (для фронта)")
    stream: bool = Field(False, description="Нужен ли стриминговый ответ")


class ChatResponse(BaseModel):
    outputText: str
    optionKey: str
    sessionId: Optional[str] = None
