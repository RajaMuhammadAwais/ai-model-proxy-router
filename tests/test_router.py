import pytest

from ai_model_proxy.core.router import RouterEngine
from ai_model_proxy.models.llm_metadata import ModelCapabilities, ModelMetadata


def model(model_id, provider, context_length, reasoning, coding, cost, latency=1.0, health_status="healthy"):
    return ModelMetadata(
        id=model_id,
        provider=provider,
        capabilities=ModelCapabilities(
            context_length=context_length,
            reasoning_strength=reasoning,
            coding_strength=coding,
        ),
        cost_per_1k_tokens=cost,
        latency_score=latency,
        health_status=health_status,
    )


@pytest.mark.asyncio
async def test_router_filters_models_that_do_not_fit_context():
    router = RouterEngine({"weights": {"capability": 0.7, "cost": 0.1, "latency": 0.1, "reliability": 0.1}})
    selected = await router.route_request(
        {
            "required_capabilities": {
                "reasoning_strength": 0.8,
                "coding_strength": 0.3,
                "context_length": 16000,
            }
        },
        [
            model("small", "a", 4096, 1.0, 1.0, 0.001),
            model("large", "b", 32768, 0.8, 0.5, 0.01),
        ],
    )

    assert selected.id == "large"


@pytest.mark.asyncio
async def test_router_uses_observed_reliability_when_weighted():
    router = RouterEngine({"weights": {"capability": 0.2, "cost": 0.1, "latency": 0.1, "reliability": 0.6}})
    router.update_metrics("unstable", "a", latency=1.0, success=False)
    selected = await router.route_request(
        {
            "required_capabilities": {
                "reasoning_strength": 0.5,
                "coding_strength": 0.5,
                "context_length": 1000,
            }
        },
        [
            model("unstable", "a", 4096, 1.0, 1.0, 0.001),
            model("steady", "b", 4096, 0.7, 0.7, 0.01),
        ],
    )

    assert selected.id == "steady"
