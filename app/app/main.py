from opentelemetry import trace

from app.setup import setup_otel

TRACES_ENDPOINT: str = "http://localhost:4318/v1/traces"
METRICS_ENDPOINT: str = "http://localhost:4318/v1/metrics"
LOGS_ENDPOINT: str = "http://localhost:4318/v1/logs"


tracer = trace.get_tracer(__name__)


def frontend():
    with tracer.start_as_current_span("Add image to a product frontend") as span:
        TRACE_ID = span.get_span_context().trace_id
        SPAN_ID = span.get_span_context().span_id
        # send this to backend for next request, and then create SpanContext from it
        # usually it should be sent on HTTP headers
        # but to simplify, we will just return it directly
        return trace.SpanContext(TRACE_ID, SPAN_ID, is_remote=True)


def api_service(front_end_context: trace.SpanContext):
    with tracer.start_as_current_span("/add-image API Call") as span:
        span.add_link(front_end_context)  # this add a link to the frontend span
        # link is used to connect two spans that are related

        # do some work
        span.set_attribute(
            "user.id", 1
        )  # this could even be set on middleware for all requests

        # again return the context to be used on next request
        return trace.SpanContext(
            span.get_span_context().trace_id,
            span.get_span_context().span_id,
            is_remote=True,
        )


def extract_metadata_from_image_ml_service(backend_context: trace.SpanContext):
    with tracer.start_as_current_span("Extract tags from image") as span:
        span.add_link(backend_context)  # this add a link to the frontend span
        # link is used to connect two spans that are related

        # do some work
        span.set_attribute("user.id", 1)
        span.set_attribute("image.id", 1)
        span.set_attribute("image.extracted_tags.count", 10)


def main():
    setup_otel(
        otel_name="testing",
        traces_endpoint=TRACES_ENDPOINT,
        metrics_endpoint=METRICS_ENDPOINT,
        logs_endpoint=LOGS_ENDPOINT,
    )
    frontend_span = frontend()
    api_span = api_service(frontend_span)
    extract_metadata_from_image_ml_service(api_span)


if __name__ == "__main__":
    main()
