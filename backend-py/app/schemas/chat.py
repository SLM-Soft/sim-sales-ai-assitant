from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["User", "Assistant", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    userQuestion: str = Field(..., description="User question text")
    optionKey: str = Field(..., description="Scenario key (sales, project_analysis, etc.)")
    sessionId: Optional[str] = Field(None, description="Client-provided session id")
    stream: bool = Field(False, description="Enable streaming response")
    messages: List[ChatMessage] = Field(default_factory=list, description="Conversation history")


class ChatResponse(BaseModel):
    outputText: str
    optionKey: str
    sessionId: Optional[str] = None
