# Experiments

This project is benchmark-first. A stage is not complete until it produces a
runnable artifact, a reproducible benchmark, saved results, and an interpretation
that can be reviewed later.

## Stage Definition Of Done

Each stage must include:

- runnable code or deployment artifact
- benchmark command that can be rerun
- saved raw result artifact such as JSON, CSV, logs, or metrics snapshot
- summary table or plot where useful
- writeup explaining hypothesis, setup, result, and interpretation

## Required Metrics

Track these from the earliest useful stage:

- request count
- success and error count
- status code
- selected backend
- model name
- routing policy
- prompt tokens
- output tokens
- total tokens
- TTFT
- TPOT
- total latency
- throughput in requests/sec
- throughput in tokens/sec
- p50, p90, p95, and p99 latency
- backend latency where available
- GPU utilization and GPU memory where available

Additional metrics should be added when they directly explain a result:

- queue wait time
- outstanding requests
- backend queue depth
- KV cache usage
- prefix cache hit rate
- prefill tokens/sec
- decode tokens/sec
- cost per request or token unit

## Experiment Template

Use this structure for experiment reports:

```markdown
# Experiment: <short title>

## Hypothesis
What do we expect to happen, and why?

## Setup
- Gateway:
- Backend:
- Model:
- Hardware:
- Deployment:
- Routing policy:

## Workload
- Prompt mix:
- Output token target:
- Concurrency:
- Duration:

## Metrics
- TTFT:
- TPOT:
- Total latency:
- Throughput:
- Error rate:
- Backend/GPU metrics:

## Results
Raw artifact paths, summary tables, and plots.

## Interpretation
What changed, what explains it, and what remains uncertain?

## Production Lessons
What would this imply for deployment, scaling, reliability, or cost?
```

## Artifact Rules

- Keep raw benchmark outputs.
- Record model, backend version, hardware, and deployment mode.
- Record command lines used to run benchmarks.
- Label synthetic or mock-worker results clearly.
- Do not compare mock-worker results as if they were real model-serving results.
- Include cost notes for rented GPU experiments.

## Benchmark Tooling

Benchmark tools are chosen by phase and by what layer needs to be measured.
Prefer real backend results. Synthetic or mock-worker results must be labeled as
gateway or scheduler tests, not model-serving results.

| Tool | Purpose | Use it to measure / validate | Intention |
| --- | --- | --- | --- |
| vLLM `benchmark_serving.py` | Primary LLM serving benchmark | TTFT, TPOT/ITL, end-to-end latency, output tokens/sec, request throughput, concurrency behavior | Understand raw model-serving performance and how vLLM features such as continuous batching, KV cache usage, context length, and model choice affect latency and throughput. |
| vLLM `benchmark_latency.py` / `benchmark_throughput.py` | Lower-level engine benchmarks | Single-request latency, offline throughput, model/kernel behavior | Isolate model execution performance from API and product-layer overhead. |
| NVIDIA GenAI-Perf | OpenAI-compatible endpoint benchmark | Streaming latency, TTFT, inter-token latency, tokens/sec, request latency under concurrency | Benchmark the inference endpoint like a production GenAI API and produce credible infra-style performance reports. |
| Locust | Product/API load testing | Concurrent users, request success rate, timeout behavior, gateway overhead, auth/rate-limit behavior, streaming stability | Validate the full inference-as-a-service product layer, not just the model server. |
| Prometheus + Grafana | Metrics and dashboarding | Request latency, queue time, GPU utilization, memory usage, KV cache usage, tokens/sec, error rates | Correlate user-facing performance with system and GPU metrics. |
| NVIDIA DCGM Exporter | GPU observability | GPU utilization, VRAM usage, power draw, temperature, SM occupancy, memory bandwidth | Understand how inference workloads use GPU resources under different traffic patterns. |
| `llm-d-benchmark` | Distributed inference benchmarking | Multi-node serving behavior, routing performance, disaggregated prefill/decode, KV-aware routing, Kubernetes deployment performance | Validate advanced cloud-inference architecture and multi-node serving behavior. |
