from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

class ModelCapabilities(BaseModel):
    context_length: int = Field(gt=0)
    reasoning_strength: float = Field(ge=0, le=1)
    coding_strength: float = Field(ge=0, le=1)
    tool_calling: bool = False
    multimodal: bool = False

class ModelMetadata(BaseModel):
    id: str
    provider: str
    capabilities: ModelCapabilities
    latency_score: Optional[float] = Field(default=None, ge=0)
    cost_per_1k_tokens: Optional[float] = Field(default=None, ge=0)
    health_status: Literal["healthy", "degraded", "unhealthy", "disabled"] = "healthy"
    last_updated: Optional[float] = None

class ChatMessage(BaseModel):
    role: str
    content: Any

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
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None
