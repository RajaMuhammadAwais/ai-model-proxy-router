from typing import List, Dict, Any, Optional
from ..models.llm_metadata import ModelMetadata
import logging

logger = logging.getLogger(__name__)

class RouterEngine:
    def __init__(self, policy: Dict[str, float]):
        self.policy = policy
        self.model_metrics: Dict[str, Dict[str, Any]] = {}

    async def route_request(self, analyzed_request: Dict[str, Any], available_models: List[ModelMetadata]) -> ModelMetadata:
        if not available_models:
            raise ValueError("No models available for routing")

        scored_models = []
        for model in available_models:
            score = self._calculate_score(model, analyzed_request)
            scored_models.append((score, model))

        # Sort by score descending
        scored_models.sort(key=lambda x: x[0], reverse=True)
        
        best_model = scored_models[0][1]
        logger.info(f"Routed request to {best_model.provider}/{best_model.id} with score {scored_models[0][0]}")
        return best_model

    def _calculate_score(self, model: ModelMetadata, analyzed_request: Dict[str, Any]) -> float:
        req_caps = analyzed_request["required_capabilities"]
        
        # Capability Match (0-1)
        cap_score = (
            (model.capabilities.reasoning_strength * req_caps["reasoning_strength"]) +
            (model.capabilities.coding_strength * req_caps["coding_strength"])
        ) / 2.0
        
        # Context Length Check (Hard constraint)
        if model.capabilities.context_length < req_caps["context_length"]:
            cap_score = 0
            
        # Cost Score (Lower is better, normalized)
        # Assuming max cost is 0.1 per 1k tokens for normalization
        cost_score = 1.0 - min(model.cost_per_1k_tokens / 0.1, 1.0)
        
        # Latency Score (1.0 - normalized latency)
        # Assuming max latency is 5.0s for normalization
        latency_score = 1.0 - min(model.latency_score / 5.0, 1.0)
        
        # Weighted Sum
        total_score = (
            self.policy["capability"] * cap_score +
            self.policy["cost"] * cost_score +
            self.policy["latency"] * latency_score
        )
        
        return total_score

    def update_metrics(self, model_id: str, provider: str, latency: float, success: bool):
        # In a real system, use moving averages or more complex logic
        key = f"{provider}:{model_id}"
        if key not in self.model_metrics:
            self.model_metrics[key] = {"latency": latency, "success_rate": 1.0 if success else 0.0}
        else:
            # Simple moving average
            self.model_metrics[key]["latency"] = self.model_metrics[key]["latency"] * 0.8 + latency * 0.2
            success_val = 1.0 if success else 0.0
            self.model_metrics[key]["success_rate"] = self.model_metrics[key]["success_rate"] * 0.9 + success_val * 0.1
