from typing import Optional, List, Literal
from pydantic import BaseModel

Role = Literal["User", "Assistant"]

class ChatMessage(BaseModel):
    role: Role
    content: str

class BedrockRequest(BaseModel):
    modelId: Optional[str] = None
    systemPrompt: Optional[str] = None
    messages: Optional[List[ChatMessage]] = []
    maxTokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    topP: Optional[float] = None
    stopSequences: Optional[List[str]] = None

class BedrockResponse(BaseModel):
    success: bool
    output: str

class AgentRequest(BaseModel):
    inputText: str
    sessionId: Optional[str] = "default-session"
 