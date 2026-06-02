from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProviderConfig(BaseModel):
    name: str
    base_url: str
    api_key: str
    models: List[str] = [] # "auto-discovered" if empty or specific list

class RoutingPolicy(BaseModel):
    strategy: str = "adaptive"
    weights: Dict[str, float] = {
        "latency": 0.3,
        "cost": 0.3,
        "capability": 0.4
    }

class AppConfig(BaseModel):
    providers: List[ProviderConfig]
    routing_policy: RoutingPolicy
    cache_enabled: bool = True
    redis_url: Optional[str] = "redis://localhost:6379"
    log_level: str = "INFO"
