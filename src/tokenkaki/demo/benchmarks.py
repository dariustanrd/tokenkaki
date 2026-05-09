"""Benchmark reference summaries for the inference railway demo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_BENCHMARK_RAW_DIR = Path("experiments/001_vllm_gateway_baseline/raw")


def latest_benchmark_summary(raw_dir: str | Path = DEFAULT_BENCHMARK_RAW_DIR) -> dict[str, object] | None:
    """Load the newest vLLM gateway benchmark summary from a raw artifact dir."""
    directory = Path(raw_dir)
    candidates = sorted(
        directory.glob("vllm-gateway-serving*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        summary = load_benchmark_summary(candidate)
        if summary is not None:
            return summary
    return None


def load_benchmark_summary(path: str | Path) -> dict[str, object] | None:
    """Load a saved `vllm bench serve` summary with provenance labels."""
    try:
        payload = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None

    return {
        "source": "vllm_bench_serve",
        "artifact_path": str(path),
        "provenance": "benchmark_observed",
        "workload": {
            "date": payload.get("date"),
            "gateway_base_url": payload.get("gateway_base_url"),
            "public_model": payload.get("public_model"),
            "model_id": payload.get("model_id"),
            "num_prompts": payload.get("num_prompts"),
            "completed": payload.get("completed"),
            "request_rate": payload.get("request_rate"),
            "benchmark_runner": payload.get("benchmark_runner"),
        },
        "latency_ms": {
            "mean_ttft": payload.get("mean_ttft_ms"),
            "median_ttft": payload.get("median_ttft_ms"),
            "p99_ttft": payload.get("p99_ttft_ms"),
            "mean_tpot": payload.get("mean_tpot_ms"),
            "median_tpot": payload.get("median_tpot_ms"),
            "p99_tpot": payload.get("p99_tpot_ms"),
            "mean_itl": payload.get("mean_itl_ms"),
            "median_itl": payload.get("median_itl_ms"),
            "p99_itl": payload.get("p99_itl_ms"),
        },
        "throughput": {
            "requests_per_second": payload.get("request_throughput"),
            "output_tokens_per_second": payload.get("output_throughput"),
            "total_tokens_per_second": payload.get("total_token_throughput"),
        },
        "tokens": {
            "total_input": payload.get("total_input_tokens"),
            "total_output": payload.get("total_output_tokens"),
        },
    }


def station_reference_metrics(summary: dict[str, object] | None, station: str) -> dict[str, object] | None:
    """Project a benchmark summary onto one station's reference metrics."""
    if summary is None:
        return None

    normalized = station.lower()
    latency = _mapping(summary.get("latency_ms"))
    throughput = _mapping(summary.get("throughput"))
    workload = _mapping(summary.get("workload"))
    tokens = _mapping(summary.get("tokens"))

    common = {
        "source": summary.get("source"),
        "provenance": summary.get("provenance"),
        "artifact_path": summary.get("artifact_path"),
    }

    if normalized == "prefill":
        return common | {
            "mean_ttft_ms": latency.get("mean_ttft"),
            "median_ttft_ms": latency.get("median_ttft"),
            "p99_ttft_ms": latency.get("p99_ttft"),
        }
    if normalized == "decode":
        return common | {
            "mean_tpot_ms": latency.get("mean_tpot"),
            "median_tpot_ms": latency.get("median_tpot"),
            "p99_tpot_ms": latency.get("p99_tpot"),
            "mean_itl_ms": latency.get("mean_itl"),
            "output_tokens_per_second": throughput.get("output_tokens_per_second"),
            "total_output_tokens": tokens.get("total_output"),
        }
    if normalized == "metrics":
        return common | {
            "completed": workload.get("completed"),
            "num_prompts": workload.get("num_prompts"),
            "request_rate": workload.get("request_rate"),
            "requests_per_second": throughput.get("requests_per_second"),
            "total_tokens_per_second": throughput.get("total_tokens_per_second"),
        }
    if normalized in {"gateway", "queue"}:
        return common | {
            "gateway_base_url": workload.get("gateway_base_url"),
            "benchmark_runner": workload.get("benchmark_runner"),
            "public_model": workload.get("public_model"),
            "model_id": workload.get("model_id"),
        }
    return None


def _mapping(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
