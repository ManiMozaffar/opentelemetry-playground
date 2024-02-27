from opentelemetry.trace import SpanKind

from app.setup import setup_otel
from app.telemetry import with_span

TRACES_ENDPOINT: str = "http://localhost:4318/v1/traces"
METRICS_ENDPOINT: str = "http://localhost:4318/v1/metrics"
LOGS_ENDPOINT: str = "http://localhost:4318/v1/logs"


@with_span(SpanKind.CLIENT)
def unit_of_work(foo: int, bar: int):
    _sum(foo, bar)
    multiply(foo, bar)
    return "Bye!"


@with_span(SpanKind.CLIENT)
def _sum(foo: int, bar: int):
    return foo + bar


@with_span(SpanKind.CLIENT)
def multiply(foo: int, bar: int):
    return foo * bar


def main():
    setup_otel(
        otel_name="testing",
        traces_endpoint=TRACES_ENDPOINT,
        metrics_endpoint=METRICS_ENDPOINT,
        logs_endpoint=LOGS_ENDPOINT,
    )
    unit_of_work(3, 4)
    unit_of_work(7, 2)


if __name__ == "__main__":
    main()
