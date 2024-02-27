from opentelemetry import _logs as logs
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_otel(
    otel_name: str, traces_endpoint: str, metrics_endpoint: str, logs_endpoint: str
):
    resource = Resource.create(attributes={SERVICE_NAME: otel_name})
    tracer_provicer = TracerProvider(resource=resource)
    tracer_provicer.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=traces_endpoint),
            export_timeout_millis=1000,
        )
    )
    trace.set_tracer_provider(tracer_provicer)

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=metrics_endpoint)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            exporter=OTLPLogExporter(endpoint=logs_endpoint), export_timeout_millis=1000
        )
    )
    logs.set_logger_provider(logger_provider)
