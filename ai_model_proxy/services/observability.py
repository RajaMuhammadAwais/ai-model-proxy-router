from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

class ObservabilityManager:
    def __init__(self, service_name: str = "ai-model-proxy"):
        self.resource = Resource.create({"service.name": service_name})
        
        # Tracing
        self.tracer_provider = TracerProvider(resource=self.resource)
        self.tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)
        
        # Metrics
        self.metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
        self.meter_provider = MeterProvider(resource=self.resource, metric_readers=[self.metric_reader])
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(__name__)
        
        # Counters
        self.request_counter = self.meter.create_counter(
            "gen_ai.client.operation.duration.count",
            description="Total number of requests processed by the proxy"
        )
        self.latency_histogram = self.meter.create_histogram(
            "gen_ai.client.operation.duration",
            description="Latency of LLM requests",
            unit="s"
        )

    def instrument_app(self, app):
        FastAPIInstrumentor.instrument_app(app)

    def record_request(self, provider: str, model: str, latency: float, status: str):
        attributes = {
            "gen_ai.provider.name": provider,
            "gen_ai.request.model": model,
            "status": status,
        }
        self.request_counter.add(1, attributes)
        self.latency_histogram.record(latency, attributes)
