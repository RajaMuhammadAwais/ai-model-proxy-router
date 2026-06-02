from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ModelCapabilities(BaseModel):
    context_length: int
    reasoning_strength: float = Field(ge=0, le=1)
    coding_strength: float = Field(ge=0, le=1)
    tool_calling: bool = False
    multimodal: bool = False

class ModelMetadata(BaseModel):
    id: str
    provider: str
    capabilities: ModelCapabilities
    latency_score: float = 0.0  # Dynamic
    cost_per_1k_tokens: float
    health_status: str = "healthy"
    last_updated: Optional[float] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Any] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
