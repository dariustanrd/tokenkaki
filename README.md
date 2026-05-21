# tokenkaki

`tokenkaki` is a staged LLM inference platform for learning how realistic
OpenAI-compatible serving systems behave under measurement.

The current runtime path is a Python gateway that forwards OpenAI-compatible
requests to an external vLLM backend, records gateway metrics, and saves
benchmark evidence under milestone experiment folders.

## Goals

- Build a real OpenAI-compatible inference endpoint.
- Use real backend engines as the normal serving path, starting with vLLM.
- Keep mock workers isolated to tests and clearly labeled synthetic benchmarks.
- Measure request latency, TTFT, TPOT/ITL, throughput, errors, token counts,
  backend choice, and GPU/system signals where available.
- Progress from one measured backend to routing, serving tuning, quantization,
  Kubernetes, multi-GPU, multi-node, cache-aware routing, and disaggregated
  serving studies.
- Keep live GPU demos cost-controlled with auth, quotas, rate limits, replay
  modes, and teardown paths.
- Publish stages through the `Behind the API` blog series with runnable artifacts, benchmark evidence, saved results, and
  technical interpretation.

## Current Slice

Milestone 1 measures the path:

```text
benchmark or client
  -> tokenkaki.gateway
  -> external vLLM OpenAI-compatible HTTP server
  -> GPU execution
```

See the Milestone 1 design contract in
[`docs/milestones/001_vllm_gateway_baseline.md`](docs/milestones/001_vllm_gateway_baseline.md)
and the current execution/status plan in
[`docs/milestones/001_plan.md`](docs/milestones/001_plan.md).

## Repository Shape

The durable repository and module rules live in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The short version:

```text
pyproject.toml
uv.lock

src/tokenkaki/
  gateway/
  router/
  backends/
  registry/
  observability/
  auth/
  config/

benchmarks/
deploy/
  compose/

experiments/
scripts/
tests/
docs/
blogposts/
```

## Docs Map

Each doc has one canonical job:

- [Vision](docs/VISION.md): project purpose, learning objectives, principles,
  and non-goals.
- [Architecture](docs/ARCHITECTURE.md): durable serving path, runtime
  boundaries, module rules, and backend rules.
- [Roadmap](docs/ROADMAP.md): phase model targets and milestone sequence.
- [Milestone 1 design](docs/milestones/001_vllm_gateway_baseline.md): stable
  contract for the vLLM gateway baseline.
- [Milestone 1 plan](docs/milestones/001_plan.md): tracer-bullet execution
  status and acceptance checks.
- [Experiments](docs/EXPERIMENTS.md): stage definition of done, metric
  provenance, artifact layout, and report template.
- [Benchmarks](benchmarks/README.md): reusable benchmark wrapper usage.
- [Compose runbook](deploy/compose/README.md): gateway and Prometheus Compose
  operations.
- [vLLM runbook](deploy/vllm/README.md): external vLLM backend setup and smoke
  tests.
- [Demo Strategy](docs/DEMO_STRATEGY.md): public/demo access posture and cost
  controls.
