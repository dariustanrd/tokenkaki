import json
from pathlib import Path

from tokenkaki.demo.benchmarks import load_benchmark_summary, station_reference_metrics


def test_load_benchmark_summary_preserves_metric_provenance(tmp_path: Path) -> None:
    artifact = tmp_path / "vllm-gateway-serving-test.json"
    artifact.write_text(
        json.dumps(
            {
                "date": "20260509-150232",
                "gateway_base_url": "http://127.0.0.1:18000",
                "public_model": "qwen3-8b",
                "model_id": "Qwen/Qwen3-8B",
                "num_prompts": 10,
                "completed": 10,
                "request_rate": 1.0,
                "benchmark_runner": "same-host",
                "mean_ttft_ms": 42.9,
                "median_ttft_ms": 38.6,
                "p99_ttft_ms": 63.8,
                "mean_tpot_ms": 4.5,
                "median_tpot_ms": 4.4,
                "p99_tpot_ms": 4.9,
                "mean_itl_ms": 4.4,
                "median_itl_ms": 4.3,
                "p99_itl_ms": 7.5,
                "request_throughput": 1.03,
                "output_throughput": 63.2,
                "total_token_throughput": 194.7,
                "total_input_tokens": 1280,
                "total_output_tokens": 616,
            }
        )
    )

    summary = load_benchmark_summary(artifact)

    assert summary is not None
    assert summary["source"] == "vllm_bench_serve"
    assert summary["provenance"] == "benchmark_observed"
    assert summary["workload"]["public_model"] == "qwen3-8b"
    assert summary["latency_ms"]["mean_ttft"] == 42.9
    assert summary["throughput"]["output_tokens_per_second"] == 63.2
    assert summary["tokens"]["total_output"] == 616


def test_station_reference_metrics_project_summary_by_station(tmp_path: Path) -> None:
    artifact = tmp_path / "vllm-gateway-serving-test.json"
    artifact.write_text(
        json.dumps(
            {
                "gateway_base_url": "http://127.0.0.1:18000",
                "public_model": "qwen3-8b",
                "model_id": "Qwen/Qwen3-8B",
                "completed": 10,
                "num_prompts": 10,
                "request_rate": 1.0,
                "benchmark_runner": "same-host",
                "mean_ttft_ms": 42.9,
                "p99_ttft_ms": 63.8,
                "mean_tpot_ms": 4.5,
                "p99_tpot_ms": 4.9,
                "mean_itl_ms": 4.4,
                "request_throughput": 1.03,
                "output_throughput": 63.2,
                "total_token_throughput": 194.7,
                "total_output_tokens": 616,
            }
        )
    )
    summary = load_benchmark_summary(artifact)

    prefill = station_reference_metrics(summary, "prefill")
    decode = station_reference_metrics(summary, "decode")
    metrics = station_reference_metrics(summary, "metrics")
    gateway = station_reference_metrics(summary, "gateway")

    assert prefill is not None
    assert prefill["provenance"] == "benchmark_observed"
    assert prefill["mean_ttft_ms"] == 42.9
    assert decode is not None
    assert decode["mean_tpot_ms"] == 4.5
    assert decode["output_tokens_per_second"] == 63.2
    assert metrics is not None
    assert metrics["requests_per_second"] == 1.03
    assert gateway is not None
    assert gateway["benchmark_runner"] == "same-host"
