import asyncio
import functools
import json
from typing import Awaitable, Callable, ParamSpec, TypeVar

from opentelemetry import trace

P = ParamSpec("P")
R = TypeVar("R")
AsyncFunc = Callable[P, Awaitable[R]]
SyncFunc = Callable[P, R]


class SyncSpanCtx:
    def __init__(
        self, kind: trace.SpanKind, tracer: trace.Tracer | None = None
    ) -> None:
        self.tracer = tracer or trace.get_tracer(__name__)
        self.kind = kind

    def __call__(self, func: SyncFunc) -> SyncFunc:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self.tracer.start_as_current_span(
                f"func ${func.__qualname__}", kind=self.kind
            ) as parent:
                func_args = {
                    "args": [arg for arg in args],
                    "kwargs": {key: str(value) for key, value in kwargs.items()},
                }
                parent.set_attribute("arg", json.dumps(func_args))
                out = func(*args, **kwargs)
                attr = "null" if out is None else out
                parent.set_attribute("result", attr)
                return out

        return wrapper


class AsyncSpanCtx:
    def __init__(
        self, kind: trace.SpanKind, tracer: trace.Tracer | None = None
    ) -> None:
        self.tracer = tracer or trace.get_tracer(__name__)
        self.kind = kind

    def __call__(self, func: AsyncFunc) -> AsyncFunc:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            func_args = {
                "args": [arg for arg in args],
                "kwargs": {key: str(value) for key, value in kwargs.items()},
            }
            with self.tracer.start_as_current_span(
                f"func ${func.__qualname__}", kind=self.kind
            ) as parent:
                parent.set_attribute("arg", json.dumps(func_args))
                out = await func(*args, **kwargs)
                attr = "null" if out is None else out
                parent.set_attribute("result", attr)
                return out

        return wrapper


class with_span:
    def __init__(
        self, kind: trace.SpanKind, tracer: trace.Tracer | None = None
    ) -> None:
        self.sync_span_ctx = SyncSpanCtx(kind, tracer)
        self.async_span_ctx = AsyncSpanCtx(kind, tracer)

    def __call__(self, func: AsyncFunc | SyncFunc) -> AsyncFunc | SyncFunc:
        if asyncio.iscoroutinefunction(func):
            return self.async_span_ctx(func)
        else:
            return self.sync_span_ctx(func)
