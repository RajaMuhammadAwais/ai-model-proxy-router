from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class ProviderConfig(BaseModel):
    name: str
    base_url: str
    api_key: str
    models: List[str] = Field(default_factory=list) # "auto-discovered" if empty or specific list

class RoutingPolicy(BaseModel):
    strategy: str = "adaptive"
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "latency": 0.3,
        "cost": 0.3,
        "capability": 0.4,
        "reliability": 0.0
    })

    @field_validator("weights")
    @classmethod
    def weights_must_be_valid(cls, value):
        required = {"latency", "cost", "capability"}
        missing = required - set(value)
        if missing:
            raise ValueError(f"missing routing weights: {', '.join(sorted(missing))}")
        if any(weight < 0 for weight in value.values()):
            raise ValueError("routing weights must be non-negative")
        if abs(sum(value.values()) - 1.0) > 0.001:
            raise ValueError("routing weights must sum to 1.0")
        return value


class SecurityConfig(BaseModel):
    max_prompt_chars: int = Field(default=200_000, gt=0)
    block_prompt_injection_signals: bool = True
    redact_request_content_in_logs: bool = True


class AppConfig(BaseModel):
    providers: List[ProviderConfig]
    routing_policy: RoutingPolicy
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    cache_enabled: bool = True
    redis_url: Optional[str] = "redis://localhost:6379"
    log_level: str = "INFO"
