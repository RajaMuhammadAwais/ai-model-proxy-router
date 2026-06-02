# AI Model Proxy and Intelligent Router

[![CI](https://github.com/RajaMuhammadAwais/ai-model-proxy-intelligent-router/actions/workflows/ci.yml/badge.svg)](https://github.com/RajaMuhammadAwais/ai-model-proxy-intelligent-router/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-OpenAI--compatible-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenTelemetry](https://img.shields.io/badge/observability-OpenTelemetry-4A148C)](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
[![OWASP LLM](https://img.shields.io/badge/security-OWASP%20LLM%20Top%2010%202025-000000)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![NIST AI RMF](https://img.shields.io/badge/governance-NIST%20AI%20RMF-1f6b75)](https://www.nist.gov/itl/ai-risk-management-framework)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Enterprise-oriented OpenAI-compatible gateway for routing LLM traffic across multiple providers. The project focuses on policy-driven routing, provider isolation, reliability controls, API-key authentication, prompt guardrails, and GenAI-aware observability.

## Research Baseline

This roadmap was verified on 2026-06-02 from primary sources:

- [NIST AI RMF and NIST AI 600-1 Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework): AI risk governance, measurement, monitoring, and generative AI risk management.
- [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/): prompt injection, sensitive information disclosure, insecure output handling, denial of service, supply-chain risk, and unbounded consumption.
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/): provider/model attributes and GenAI operation metrics; production telemetry should not capture prompts or outputs by default.
- [OpenAI production best practices](https://platform.openai.com/docs/guides/production-best-practices), [rate limits](https://platform.openai.com/docs/guides/rate-limits), and [evaluation best practices](https://platform.openai.com/docs/guides/evaluation-best-practices): key controls, spend/rate limits, exponential backoff, and production eval discipline.

## Current Capabilities

- OpenAI-compatible `/v1/chat/completions`, `/v1/models`, and placeholder `/v1/embeddings` endpoints.
- Config-driven provider registry for OpenAI-compatible providers such as NVIDIA NIM, OpenRouter, Groq, and Gemini-compatible gateways.
- Routing by capability, cost, latency, context fit, health, and observed reliability.
- No-guess routing contract: model capability, context, price, and latency come from explicit config or observed telemetry, never placeholder inference.
- Retry and circuit-breaker primitives for provider resilience.
- API-key authentication with no default fallback secret.
- Request size limits and high-signal prompt-injection blocking.
- OpenTelemetry GenAI-aligned metrics attributes.
- CI workflow and focused unit tests for routing and guardrails.

## Quick Start

```bash
git clone https://github.com/RajaMuhammadAwais/ai-model-proxy-intelligent-router.git
cd ai-model-proxy-intelligent-router
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
copy config.yaml.example config.yaml
```

Set `PROXY_API_KEYS` and provider API keys in `.env`, then run:

```bash
python -m uvicorn ai_model_proxy.main:app --host 0.0.0.0 --port 8000
```

## Configuration

`config.yaml.example` defines providers, explicit model metadata, routing weights, cache settings, and security guardrails. Provider API keys should be referenced as environment variables and never committed.

Provider `/models` responses usually include model ids, not reliable enterprise routing metadata. This project therefore requires explicit model metadata before a model can receive traffic. See [docs/routing-signals.md](docs/routing-signals.md) for the routing contract, hard constraints, score calculation, and audit fields.

Routing weights must sum to `1.0`. A production policy should include explicit weights for:

- `capability`
- `cost`
- `latency`
- `reliability`

## Enterprise Plan

The enterprise hardening plan is in [docs/enterprise-roadmap.md](docs/enterprise-roadmap.md). It covers production controls, distributed quotas, provider health, evals, governance, auditability, and platform maturity.

## Development

```bash
pytest -q
```

## License

MIT. See [LICENSE](LICENSE).
