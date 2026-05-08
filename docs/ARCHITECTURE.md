# Architecture

`tokenkaki` is organized around an OpenAI-compatible inference endpoint backed
by real model serving engines.

## Serving Path

```text
Client / benchmark
  -> OpenAI-compatible API gateway
  -> router / scheduler
  -> backend client
  -> vLLM worker first, SGLang later
  -> model runtime / GPU execution
  -> metrics, logs, traces, benchmark artifacts
```

The gateway owns API compatibility, request accounting, routing decisions, and
observability. Backend workers own model execution. Benchmarks exercise the same
public serving path used by demos.

## Core Components

- **API gateway**: exposes `/v1/models`, `/v1/chat/completions`, health, and
  metrics endpoints.
- **Router / scheduler**: selects a backend using policy and backend state.
- **Backend clients**: call real serving engines through their HTTP APIs.
- **Worker registry**: tracks backend address, model metadata, health, load, and
  capacity information.
- **Observability**: records request, routing, backend, latency, token, and GPU
  metrics.
- **Benchmarks**: generate repeatable workloads and save raw results for later
  analysis.

## Backend Rule

Real backends are the production path.

Initial backend order:

1. vLLM
2. SGLang
3. Additional engines only after the first two paths are measurable

Mock workers must remain separate from real serving code. They may be used for:

- load-test scaffolding
- failure simulation
- multi-client Locust scenarios
- deterministic scheduler tests

They must not become the default runtime path or leak test-only behavior into
real backend clients.

## Demo Posture

The public demo should show the real endpoint shape and benchmark artifacts
without allowing uncontrolled GPU spend.

Use a hybrid access model:

- public limited access for cheap live calls or replay mode
- authenticated access for real-model calls
- quotas and rate limits for every live backend
- visible benchmark reports for expensive experiments
- kill switch and teardown path for GPU-backed deployments

This is part of the platform design, not an afterthought: cost controls,
capacity limits, and usage visibility are serving-system concerns.
