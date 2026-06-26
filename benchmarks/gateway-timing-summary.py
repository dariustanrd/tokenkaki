#!/usr/bin/env python3
"""Summarize gateway first-token timing metrics for saved benchmark artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


BENCHMARK_KEYS = [
    "completed",
    "failed",
    "request_rate",
    "request_throughput",
    "output_throughput",
    "mean_ttft_ms",
    "median_ttft_ms",
    "p99_ttft_ms",
    "mean_tpot_ms",
    "p99_tpot_ms",
    "mean_itl_ms",
    "p99_itl_ms",
]

GATEWAY_STREAM_METRICS = [
    "tokenkaki_gateway_stream_backend_open_seconds",
    "tokenkaki_gateway_stream_first_backend_chunk_seconds",
    "tokenkaki_gateway_stream_first_client_chunk_seconds",
    "tokenkaki_gateway_stream_first_chunk_relay_seconds",
]

LABEL_PATTERN = re.compile(r'le="([^"]+)"')


def main() -> None:
    args = _parse_args()
    summary = summarize_gateway_timing(args.benchmark_json, args.metrics_prom)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {args.output}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a compact JSON summary from a vLLM benchmark result and a "
            "gateway /metrics Prometheus text snapshot."
        )
    )
    parser.add_argument(
        "--benchmark-json",
        type=Path,
        required=True,
        help="Saved vLLM benchmark JSON result.",
    )
    parser.add_argument(
        "--metrics-prom",
        type=Path,
        required=True,
        help="Saved gateway /metrics Prometheus text snapshot.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output summary JSON path.",
    )
    return parser.parse_args()


def summarize_gateway_timing(benchmark_json: Path, metrics_prom: Path) -> dict[str, Any]:
    benchmark = json.loads(benchmark_json.read_text())
    metrics = metrics_prom.read_text().splitlines()

    return {
        "benchmark_file": benchmark_json.name,
        "metrics_snapshot": metrics_prom.name,
        "benchmark": {key: benchmark[key] for key in BENCHMARK_KEYS},
        "gateway_stream_timing_ms": _summarize_stream_metrics(metrics),
    }


def _summarize_stream_metrics(metrics: list[str]) -> dict[str, dict[str, Any]]:
    summary = {}
    for metric_name in GATEWAY_STREAM_METRICS:
        short_name = _short_metric_name(metric_name)
        metric_summary = _summarize_histogram(metrics, metric_name)
        summary[short_name] = metric_summary
    return summary


def _short_metric_name(metric_name: str) -> str:
    prefix = "tokenkaki_gateway_stream_"
    suffix = "_seconds"
    if not metric_name.startswith(prefix) or not metric_name.endswith(suffix):
        raise ValueError(f"unexpected gateway stream metric name: {metric_name}")
    return metric_name[len(prefix) : -len(suffix)]


def _summarize_histogram(metrics: list[str], metric_name: str) -> dict[str, Any]:
    count = None
    total = None
    bucket_counts_s = {}

    for line in metrics:
        if line.startswith(metric_name + "_count"):
            count = float(line.rsplit(" ", 1)[1])
        elif line.startswith(metric_name + "_sum"):
            total = float(line.rsplit(" ", 1)[1])
        elif line.startswith(metric_name + "_bucket"):
            match = LABEL_PATTERN.search(line)
            if match is None:
                raise ValueError(f"missing le label in metric line: {line}")
            bucket_counts_s[match.group(1)] = float(line.rsplit(" ", 1)[1])

    return {
        "count": count,
        "sum_ms": None if total is None else total * 1000,
        "mean_ms": None if total is None or not count else total / count * 1000,
        "bucket_counts_s": bucket_counts_s,
    }


if __name__ == "__main__":
    main()
