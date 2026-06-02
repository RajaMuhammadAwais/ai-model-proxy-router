# Enterprise Roadmap

Research baseline verified on 2026-06-02.

## Primary Sources

- NIST AI Risk Management Framework and NIST AI 600-1 Generative AI Profile: governance, risk mapping, measurement, and continuous monitoring for generative AI systems.
- OWASP Top 10 for LLM Applications 2025: prompt injection, sensitive information disclosure, insecure output handling, model denial of service, supply-chain risk, and unbounded consumption.
- OpenTelemetry GenAI semantic conventions: provider/model attributes, operation duration metrics, and guidance not to capture prompts or outputs by default in production telemetry.
- OpenAI production, rate-limit, and evaluation guidance: API key controls, project rate/spend limits, random exponential backoff for rate limits, and production evals.

## Phase 1: Production Baseline

- Enforce API keys with no default development secret.
- Resolve provider credentials from environment variables, not committed config.
- Add request size limits and high-signal prompt-injection blocking.
- Add deterministic router tests for context constraints, reliability, latency, cost, and capability weighting.
- Emit OpenTelemetry GenAI-aligned metric names and attributes while redacting request content.
- Add CI for test execution on every push and pull request.

## Phase 2: Enterprise Controls

- Tenant-aware API keys, quotas, budgets, and audit logs.
- Redis-backed distributed rate limiting by API key, provider, model, RPM, TPM, and daily spend.
- Provider health checks with rolling p50/p95 latency and error-rate windows.
- Circuit-breaker state export through `/ready` and metrics.
- Signed config releases and provider allowlists.
- Structured policy validation for model capabilities, pricing, and fallback chains.

## Phase 3: AI Governance and Evaluation

- Offline and online routing evals with golden datasets for cost, latency, accuracy, refusal behavior, and task fit.
- Prompt-injection and data-exfiltration red-team suites mapped to OWASP LLM risks.
- Human review workflow for high-risk policy changes.
- Model card registry with provenance, supported modalities, pricing source, context length, data residency notes, and owner approval.
- Scheduled drift reports comparing route decisions, quality scores, and provider incidents over time.

## Phase 4: Platform Maturity

- Multi-region deployment with provider-specific failover.
- mTLS or private network support for enterprise clients.
- OpenAPI contract tests and SDK generation.
- SLOs for gateway availability, provider fallback success, p95 latency, and routing-eval pass rate.
- SOC2-ready evidence collection for auth, config changes, CI, deployment, audit logs, and incident response.
