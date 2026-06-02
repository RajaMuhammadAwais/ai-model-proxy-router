# Routing Signals

Verified on 2026-06-02 from primary sources:

- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OWASP Top 10 for LLM Applications 2025: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework and NIST AI 600-1: https://www.nist.gov/itl/ai-risk-management-framework
- Google SRE cascading failure guidance: https://sre.google/sre-book/addressing-cascading-failures/
- OpenAI production best practices: https://platform.openai.com/docs/guides/production-best-practices

## No-Guess Routing Contract

The router does not invent model context length, capability scores, price, latency, or health. A model is routable only from one of these signal sources:

- Explicit provider configuration in `config.yaml`
- Runtime telemetry collected by this gateway, such as observed latency and success rate
- Request shape, such as context size, tool requirements, multimodal input, and an explicitly requested model

If a provider returns model ids from `/models` but the config has no metadata for them, those ids are not routed. This keeps route decisions auditable and avoids silently depending on placeholder values.

## Hard Constraints

Hard constraints reject a model before scoring:

- The model is `unhealthy` or `disabled`
- The configured context window is smaller than the request estimate
- The request specifies a model id and the candidate is a different model
- The request uses tools and the model does not declare `tool_calling: true`
- The request includes non-text content and the model does not declare `multimodal: true`

These checks map to enterprise risk controls from NIST AI RMF and OWASP LLM guidance: reduce unsafe overreach, prevent avoidable resource pressure, and keep model selection explainable.

## Scored Signals

After hard constraints, the router scores eligible models with available signals:

- `capability`: weighted match between requested reasoning/coding signals and configured model capability scores
- `cost`: lower configured cost wins, normalized only against eligible candidates
- `latency`: lower observed latency wins; configured latency is used only until runtime telemetry exists
- `reliability`: observed success rate wins; before traffic exists, configured health maps to `healthy=1.0` and `degraded=0.5`

Missing optional signals are skipped and the remaining weights are normalized. This prevents a model from being rewarded or punished for data the operator has not provided.

## Decision Audit

`RouterEngine.last_decision` records:

- selected provider, model, and score
- normalized signal values
- effective weights after missing-signal normalization
- raw signal values used in the calculation
- rejected candidates and rejection reasons
- analyzer method used for request signals

Production deployments should export equivalent fields into structured logs or traces while keeping prompt and completion content redacted by default.

## Operational Notes

Use live telemetry to update latency and reliability. Google SRE guidance recommends early rejection and graceful degradation under overload; for this proxy, that means failing unhealthy providers quickly, keeping circuit breakers active, and adding distributed rate limits before high-volume production use.
