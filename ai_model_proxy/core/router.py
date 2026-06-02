import logging
from typing import Any, Dict, List, Optional, Tuple

from ..models.llm_metadata import ModelMetadata

logger = logging.getLogger(__name__)


class RouterEngine:
    health_reliability = {
        "healthy": 1.0,
        "degraded": 0.5,
        "unhealthy": 0.0,
        "disabled": 0.0,
    }

    def __init__(self, policy: Dict[str, float]):
        self.policy = policy.get("weights", policy)
        self.model_metrics: Dict[str, Dict[str, Any]] = {}
        self.last_decision: Optional[Dict[str, Any]] = None

    async def route_request(
        self,
        analyzed_request: Dict[str, Any],
        available_models: List[ModelMetadata],
    ) -> ModelMetadata:
        if not available_models:
            raise ValueError("No models available for routing")

        req_caps = analyzed_request["required_capabilities"]
        candidates: List[ModelMetadata] = []
        rejected: List[Dict[str, str]] = []

        for model in available_models:
            eligible, reason = self._is_eligible(model, analyzed_request)
            if eligible:
                candidates.append(model)
            else:
                rejected.append({"provider": model.provider, "model": model.id, "reason": reason})

        if not candidates:
            raise ValueError(f"No eligible models match the request constraints: {rejected}")

        raw_rows = {self._model_key(model): self._raw_signals(model, req_caps) for model in candidates}
        normalized_rows = self._normalize_signals(raw_rows)
        scored = [self._score_candidate(model, raw_rows, normalized_rows) for model in candidates]
        best = min(scored, key=self._sort_key)

        self.last_decision = {
            "selected": {
                "provider": best["model"].provider,
                "model": best["model"].id,
                "score": best["score"],
            },
            "signals": best["signals"],
            "effective_weights": best["effective_weights"],
            "raw_signals": best["raw_signals"],
            "rejected": rejected,
            "analysis_method": analyzed_request.get("analysis_method"),
        }

        selected = best["model"]
        logger.info(
            "Routed request to %s/%s with score %.4f using weights %s",
            selected.provider,
            selected.id,
            best["score"],
            best["effective_weights"],
        )
        return selected

    def _is_eligible(self, model: ModelMetadata, analyzed_request: Dict[str, Any]) -> Tuple[bool, str]:
        req_caps = analyzed_request["required_capabilities"]
        requested_model = analyzed_request.get("requested_model")

        if requested_model and model.id != requested_model:
            return False, "request specified a different model"
        if model.health_status in {"unhealthy", "disabled"}:
            return False, f"model health is {model.health_status}"
        if model.capabilities.context_length < req_caps["context_length"]:
            return False, "context length is below request requirement"
        if req_caps.get("tool_calling") and not model.capabilities.tool_calling:
            return False, "request requires tool calling"
        if req_caps.get("multimodal") and not model.capabilities.multimodal:
            return False, "request requires multimodal input"
        return True, "eligible"

    def _raw_signals(self, model: ModelMetadata, req_caps: Dict[str, Any]) -> Dict[str, float]:
        signals: Dict[str, float] = {}
        capability = self._capability_score(model, req_caps)
        if capability is not None:
            signals["capability"] = capability

        if model.cost_per_1k_tokens is not None:
            signals["cost"] = model.cost_per_1k_tokens

        observed = self.model_metrics.get(self._model_key(model), {})
        observed_latency = observed.get("latency")
        if observed_latency is not None:
            signals["latency"] = observed_latency
        elif model.latency_score is not None:
            signals["latency"] = model.latency_score

        if observed.get("attempts", 0) > 0:
            signals["reliability"] = observed["success_rate"]
        else:
            signals["reliability"] = self.health_reliability[model.health_status]

        return signals

    def _capability_score(self, model: ModelMetadata, req_caps: Dict[str, Any]) -> Optional[float]:
        required_reasoning = req_caps.get("reasoning_strength", 0.0)
        required_coding = req_caps.get("coding_strength", 0.0)
        total_requirement = required_reasoning + required_coding
        if total_requirement <= 0:
            return None

        return (
            model.capabilities.reasoning_strength * required_reasoning
            + model.capabilities.coding_strength * required_coding
        ) / total_requirement

    def _normalize_signals(self, raw_rows: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        normalized = {key: {} for key in raw_rows}

        for key, signals in raw_rows.items():
            for bounded_signal in ("capability", "reliability"):
                if bounded_signal in signals:
                    normalized[key][bounded_signal] = signals[bounded_signal]

        for lower_is_better in ("cost", "latency"):
            values = [signals[lower_is_better] for signals in raw_rows.values() if lower_is_better in signals]
            if not values:
                continue

            minimum = min(values)
            maximum = max(values)
            for key, signals in raw_rows.items():
                if lower_is_better not in signals:
                    continue
                value = signals[lower_is_better]
                normalized[key][lower_is_better] = 1.0 if maximum == minimum else 1.0 - ((value - minimum) / (maximum - minimum))

        return normalized

    def _score_candidate(
        self,
        model: ModelMetadata,
        raw_rows: Dict[str, Dict[str, float]],
        normalized_rows: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        key = self._model_key(model)
        signals = normalized_rows[key]
        available_weights = {name: weight for name, weight in self.policy.items() if name in signals and weight > 0}
        weight_total = sum(available_weights.values())
        if weight_total <= 0:
            raise ValueError("No configured routing signals are available for eligible models")

        effective_weights = {name: weight / weight_total for name, weight in available_weights.items()}
        score = sum(signals[name] * weight for name, weight in effective_weights.items())
        return {
            "model": model,
            "score": score,
            "signals": signals,
            "raw_signals": raw_rows[key],
            "effective_weights": effective_weights,
        }

    def _sort_key(self, scored: Dict[str, Any]) -> Tuple[Any, ...]:
        raw = scored["raw_signals"]
        signals = scored["signals"]
        model = scored["model"]
        cost = raw.get("cost")
        latency = raw.get("latency")

        return (
            -scored["score"],
            -signals.get("reliability", 0.0),
            cost is None,
            cost if cost is not None else 0.0,
            latency is None,
            latency if latency is not None else 0.0,
            model.provider,
            model.id,
        )

    def update_metrics(self, model_id: str, provider: str, latency: float, success: bool):
        key = f"{provider}:{model_id}"
        metrics = self.model_metrics.setdefault(
            key,
            {
                "latency": None,
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.0,
            },
        )

        metrics["attempts"] += 1
        if success:
            metrics["successes"] += 1
        else:
            metrics["failures"] += 1
        metrics["success_rate"] = metrics["successes"] / metrics["attempts"]
        metrics["latency"] = latency if metrics["latency"] is None else metrics["latency"] * 0.8 + latency * 0.2

    def _model_key(self, model: ModelMetadata) -> str:
        return f"{model.provider}:{model.id}"
