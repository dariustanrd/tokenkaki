# Architecture

`tokenkaki` is organized around an OpenAI-compatible inference endpoint backed
by real model serving engines.

## Serving Path

The serving architecture is stable across milestones: clients call an
OpenAI-compatible gateway, the gateway makes routing and accounting decisions,
real backend engines execute the model work, and benchmarks measure the public
path. Later milestones make individual parts of this path richer without
changing the basic contract.

```text
Client, demo UI, or benchmark runner
  -> OpenAI-compatible HTTP endpoint
     - /v1/models
     - /v1/chat/completions
  -> gateway request lifecycle
     - authentication and quota checks when enabled
     - OpenAI-compatible validation
     - request ID and accounting context
     - streaming or non-streaming response setup
  -> model registry lookup
     - requested model
     - compatible backend engine
     - backend address and health state
     - capacity and configured limits
  -> router / scheduler
     - eligible backend set
     - routing policy
     - load, queue, and cache-locality signals where available
  -> backend client
     - OpenAI-compatible HTTP call to vLLM
     - SGLang client after the vLLM path is measurable (low priority, only consider after all milestones are complete / near completion)
  -> backend serving engine
     - tokenizer and request admission
     - prefill
     - decode
     - batching, KV cache, and engine scheduling
  -> model runtime / GPU execution
  -> backend response stream or completion
  -> gateway response adaptation
     - OpenAI-compatible chunks or JSON response
     - usage extraction where available
     - final accounting
  -> client, demo UI, or benchmark runner
```

The gateway owns API compatibility, request accounting, routing decisions, and
observability. Backend workers own model execution. Benchmarks exercise the same
public serving path used by demos.

The gateway should not become a model engine wrapper. It forwards
OpenAI-compatible requests to real backend engines with minimal mutation and
parses only the envelope needed for gateway responsibilities: endpoint, model,
streaming mode, request context, routing inputs, and accounting data.

Telemetry is emitted alongside the serving path rather than after it:

```text
Benchmark or client observed
  -> end-to-end latency
  -> TTFT, TPOT / inter-token latency, throughput
  -> request success and failure

Gateway, router, and backend clients
  -> request, route, error, latency, token, and selected-backend metrics
  -> logs and traces with request IDs
  -> Prometheus scrape endpoint

Backend serving engines and GPU hosts
  -> engine metrics
  -> GPU utilization, memory, power, and saturation signals
  -> Prometheus / DCGM Exporter where available

Benchmark runners
  -> public endpoint requests
  -> raw benchmark output
  -> saved experiment artifacts
  -> writeup-ready analysis
```

Metrics and artifacts must preserve provenance. Gateway-observed latency,
benchmark-observed latency, backend-reported token usage, and GPU utilization
are related signals, but they are not interchangeable.

The initial concrete path is documented in
[`docs/milestones/001_vllm_gateway_baseline.md`](milestones/001_vllm_gateway_baseline.md):
a single gateway process calls a real external vLLM OpenAI-compatible HTTP
server. The gateway is not the model server, and vLLM is not hidden behind a
mock worker in the production path.

As the project grows, the same logical path expands rather than changing shape:

- multiple backend replicas add registry state, health, load, and routing-policy
  comparisons
- batching and tuning experiments mostly change backend-engine configuration and
  workload shape
- Kubernetes changes deployment and discovery mechanics, not the public API
  contract
- multi-GPU and multi-node serving change the backend engine's execution
  topology
- cache-aware routing adds prefix/KV locality signals to the scheduler
- disaggregated prefill/decode splits backend execution into separate pools, but
  the gateway still receives an OpenAI-compatible request and returns an
  OpenAI-compatible response

## Milestone Evolution

The architecture should stay milestone-specific where the details are still
learning questions.

| Milestone | Architectural focus | What changes |
| --- | --- | --- |
| 1. vLLM gateway baseline | External vLLM behind an OpenAI-compatible gateway | Establish transparent forwarding, streaming, config-backed registry, basic metrics, and fail-loud errors. |
| 2. Routing policy comparison | Multiple backend replicas | Add backend sets, health state, outstanding-request tracking, and routing-policy comparison. |
| 3. Batching and serving tuning | Backend engine configuration | Vary vLLM serving parameters and workload shape while keeping the public gateway path stable. |
| 4. Quantization comparison | Model variants | Add explicit model/backend variants for baseline and quantized serving paths. |
| 5. Kubernetes deployment | Orchestration and discovery | Move deployment mechanics toward Kubernetes services, endpoints, and scrape configuration. |
| 6. Multi-GPU topology | Backend execution topology | Use backend engine tensor-parallel or equivalent features; gateway contract stays stable. |
| 7. Multi-node serving | Cross-node runtime behavior | Add network, distributed runtime, and failure-mode evidence around backend execution. |
| 8. Cache-aware routing | Scheduler input quality | Add prefix or cache-locality signals while accepting that true KV state may only be available if backend engines expose it. |
| 9. Disaggregated prefill/decode | Split backend execution pools | Route to or measure prefill/decode-aware serving without making the gateway own model execution. |

## Repository Architecture

`tokenkaki` should start as a Python-first, service-ready codebase rather than a
multi-service repository. Use `uv` for package and dependency management. The
initial implementation has one runtime service: the OpenAI-compatible gateway.
Other capabilities stay as modules, scripts, benchmarks, or test fixtures until
they need independent deployment.

Planned package layout:

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
```

The supporting top-level directories should make deployment and experiments
first-class without mixing them into serving code:

```text
benchmarks/
deploy/
  compose/
experiments/
scripts/
tests/
```

`deploy/compose/` is the initial deployment surface. Kubernetes-family manifests
should be deferred until the first kind, k3s, k3d, or cloud Kubernetes
experiment, and should then live under `deploy/kubernetes/`.

The package should use deep modules: small public interfaces with implementation
details hidden inside each module. Use functional facades by default, Protocols
only for interchangeable boundaries such as backend clients, and stateful
service objects only when a component owns lifecycle or mutable state.

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

## Initial Runtime Boundary

The gateway is the only first-class runtime service at the start. It owns the
FastAPI application, OpenAI-compatible endpoints, request validation, routing
handoff, metrics emission, and calls to backend clients.

Do not make benchmark runners or mock workers initial runtime services. They may
be executable tools or test fixtures, but service extraction should happen only
after there is a concrete deployment, scaling, or lifecycle reason.

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
