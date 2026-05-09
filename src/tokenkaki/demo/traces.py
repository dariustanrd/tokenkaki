"""In-memory demo trace tickets for request railway visualization."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import perf_counter

from tokenkaki.registry import ModelRoute


@dataclass
class TraceTicket:
    request_id: str
    session_id: str | None
    user_id: str | None
    public_model: str
    backend_model: str
    selected_backend: str
    routing_policy: str
    stream: bool
    started_at: float
    active_requests_at_start: int
    first_chunk_at: float | None = None
    completed_at: float | None = None
    status: str = "running"
    status_code: int | None = None
    error_class: str | None = None


class TraceStore:
    """Store recent demo request traces in memory.

    This is intentionally process-local for the hackathon demo. A later public
    deployment can replace it with a bounded external store if traces need to
    survive restarts or span multiple gateway replicas.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._traces: dict[str, TraceTicket] = {}
        self._active_requests = 0

    def start(
        self,
        *,
        request_id: str,
        session_id: str | None,
        user_id: str | None,
        route: ModelRoute,
        stream: bool,
    ) -> TraceTicket:
        with self._lock:
            self._active_requests += 1
            ticket = TraceTicket(
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                public_model=route.public_model,
                backend_model=route.backend_model,
                selected_backend=route.backend_base_url,
                routing_policy=route.routing_policy,
                stream=stream,
                started_at=perf_counter(),
                active_requests_at_start=self._active_requests,
            )
            self._traces[request_id] = ticket
            return ticket

    def mark_first_chunk(self, request_id: str) -> None:
        with self._lock:
            ticket = self._traces.get(request_id)
            if ticket is not None and ticket.first_chunk_at is None:
                ticket.first_chunk_at = perf_counter()

    def complete(self, request_id: str, *, status_code: int) -> None:
        self._finish(request_id, status="completed", status_code=status_code, error_class=None)

    def fail(self, request_id: str, *, status_code: int, error_class: str) -> None:
        self._finish(request_id, status="failed", status_code=status_code, error_class=error_class)

    def get(self, request_id: str) -> dict[str, object] | None:
        with self._lock:
            ticket = self._traces.get(request_id)
            if ticket is None:
                return None
            return _serialize(ticket)

    def _finish(
        self,
        request_id: str,
        *,
        status: str,
        status_code: int,
        error_class: str | None,
    ) -> None:
        with self._lock:
            ticket = self._traces.get(request_id)
            if ticket is None:
                return
            if ticket.completed_at is None:
                self._active_requests = max(0, self._active_requests - 1)
            ticket.completed_at = perf_counter()
            ticket.status = status
            ticket.status_code = status_code
            ticket.error_class = error_class


def _serialize(ticket: TraceTicket) -> dict[str, object]:
    first_chunk_ms = _elapsed_ms(ticket.started_at, ticket.first_chunk_at)
    total_latency_ms = _elapsed_ms(ticket.started_at, ticket.completed_at)
    return {
        "request_id": ticket.request_id,
        "session_id": ticket.session_id,
        "user_id": ticket.user_id,
        "model": ticket.public_model,
        "backend_model": ticket.backend_model,
        "selected_backend": ticket.selected_backend,
        "routing_policy": ticket.routing_policy,
        "stream": ticket.stream,
        "status": ticket.status,
        "status_code": ticket.status_code,
        "error_class": ticket.error_class,
        "active_requests_at_start": ticket.active_requests_at_start,
        "timings_ms": {
            "first_chunk": first_chunk_ms,
            "total": total_latency_ms,
        },
    }


def _elapsed_ms(started_at: float, ended_at: float | None) -> float | None:
    if ended_at is None:
        return None
    return round((ended_at - started_at) * 1000, 3)
