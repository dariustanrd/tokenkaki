"""Station fact views over a demo trace ticket."""

from __future__ import annotations

from typing import Any

STATIONS = {"gateway", "queue", "prefill", "decode", "metrics"}


def station_facts(
    trace: dict[str, object],
    station: str,
    reference_metrics: dict[str, object] | None = None,
) -> dict[str, object] | None:
    """Return UI-ready facts for one inference railway station."""
    normalized = station.lower()
    if normalized not in STATIONS:
        return None

    builders = {
        "gateway": _gateway_facts,
        "queue": _queue_facts,
        "prefill": _prefill_facts,
        "decode": _decode_facts,
        "metrics": _metrics_facts,
    }
    facts = builders[normalized](trace)
    if reference_metrics is not None:
        facts["reference_metrics"] = reference_metrics
    return facts


def _gateway_facts(trace: dict[str, object]) -> dict[str, object]:
    return _station(
        trace,
        station="gateway",
        title="Gateway",
        measurement_basis="measured",
        facts={
            "request_id": trace["request_id"],
            "session_id": trace["session_id"],
            "user_id": trace["user_id"],
            "model": trace["model"],
            "backend_model": trace["backend_model"],
            "selected_backend": trace["selected_backend"],
            "routing_policy": trace["routing_policy"],
            "stream": trace["stream"],
        },
    )


def _queue_facts(trace: dict[str, object]) -> dict[str, object]:
    return _station(
        trace,
        station="queue",
        title="Queue",
        measurement_basis="gateway_observed",
        facts={
            "active_requests_at_start": trace["active_requests_at_start"],
            "note": "This is the gateway in-flight request count, not vLLM internal queue depth.",
        },
    )


def _prefill_facts(trace: dict[str, object]) -> dict[str, object]:
    timings = _timings(trace)
    return _station(
        trace,
        station="prefill",
        title="Prefill",
        measurement_basis="gateway_inferred",
        facts={
            "first_chunk_ms": timings.get("first_chunk"),
            "note": "For streaming requests, first_chunk_ms is a gateway-observed TTFT-like signal. It is not direct backend prefill telemetry.",
        },
    )


def _decode_facts(trace: dict[str, object]) -> dict[str, object]:
    timings = _timings(trace)
    return _station(
        trace,
        station="decode",
        title="Decode",
        measurement_basis="gateway_observed",
        facts={
            "stream": trace["stream"],
            "streamed_chunk_count": trace["streamed_chunk_count"],
            "total_latency_ms": timings.get("total"),
            "note": "Chunk count is an SSE forwarding count, not a token count. Token-level decode metrics come from benchmarks or backend usage when available.",
        },
    )


def _metrics_facts(trace: dict[str, object]) -> dict[str, object]:
    timings = _timings(trace)
    return _station(
        trace,
        station="metrics",
        title="Metrics",
        measurement_basis="measured",
        facts={
            "status": trace["status"],
            "status_code": trace["status_code"],
            "error_class": trace["error_class"],
            "first_chunk_ms": timings.get("first_chunk"),
            "total_latency_ms": timings.get("total"),
        },
    )


def _station(
    trace: dict[str, object],
    *,
    station: str,
    title: str,
    measurement_basis: str,
    facts: dict[str, object],
) -> dict[str, object]:
    return {
        "request_id": trace["request_id"],
        "station": station,
        "title": title,
        "measurement_basis": measurement_basis,
        "facts": facts,
    }


def _timings(trace: dict[str, object]) -> dict[str, Any]:
    timings = trace.get("timings_ms")
    if isinstance(timings, dict):
        return timings
    return {}
