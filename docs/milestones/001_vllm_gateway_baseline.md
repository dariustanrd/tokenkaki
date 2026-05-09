# Milestone 1: vLLM Gateway Baseline

## Goal

Build a minimal OpenAI-compatible gateway that calls an external vLLM server and
produces credible baseline measurements for the public serving path.

Milestone 1 should answer one concrete question: what happens when a client or
benchmark sends OpenAI-compatible chat requests through `tokenkaki.gateway` to a
real vLLM backend?

## Non-Goals

- Do not import, embed, or modify vLLM internals.
- Do not add auth, quotas, or public-demo access controls yet.
- Do not add smart retries or failover for generation requests.
- Do not turn the gateway into a benchmark-results service.
- Do not introduce Kubernetes before the gateway, metrics, and baseline
  benchmark path are working.

## Serving Boundary

The concrete Milestone 1 runtime boundary is:

```text
client, demo UI, or benchmark runner
  -> tokenkaki.gateway
  -> external vLLM OpenAI-compatible HTTP server
  -> model runtime / GPU execution
```

The gateway is the only `tokenkaki` runtime service. vLLM is a separately
managed serving engine reachable over HTTP.

Component placement may change without changing this boundary. Early
development may run the gateway on macOS and vLLM on a remote NVIDIA GPU host
over Tailscale. Later Milestone 1 validation should also support running the
gateway, vLLM, metrics stack, and benchmark tooling on the same remote GPU
machine, and future milestones may move the same roles onto rented GPU VMs or
clusters. These are deployment placements, not different application
architectures.

## Request Handling

The gateway should behave as a transparent OpenAI-compatible forwarding layer
with a thin parsed envelope.

The original request body remains the source of truth and should be forwarded to
vLLM with minimal mutation. The gateway may parse the fields needed for gateway
responsibilities:

- endpoint name
- requested `model`
- `stream`
- request ID and accounting context
- caller identity later, when auth exists
- prompt-size or context-length estimate later, when routing needs it

Milestone 1 endpoints:

- `/v1/models`
- `/v1/chat/completions`
- health endpoint
- Prometheus metrics endpoint

## Model And Backend Config

Milestone 1 uses a small static config-backed registry. Static config is the
bootstrap mechanism, not the long-term control plane.

The config should describe serving intent:

- public model name
- backend engine type, initially `vllm`
- backend base URL
- backend model name when it differs from the public name
- enabled state
- basic configured limits where useful

Observed runtime state should not be manually encoded in config. Health,
availability, backend model lists, load, and later cache locality are runtime
signals.

## Streaming

Streaming is required early.

The gateway should proxy streaming responses as OpenAI-compatible SSE chunks
while preserving enough gateway-level visibility to record:

- selected backend
- stream start and end
- stream duration
- status and error class
- client disconnects where detectable

Benchmark tools, not gateway metrics alone, should measure TTFT and inter-token
latency.

## Observability Contract

Metrics and artifacts must keep provenance clear.

```text
Benchmark or client observed:
  end-to-end latency
  TTFT
  inter-token latency / TPOT
  throughput
  request success and failure

Gateway observed:
  request count
  status code
  selected backend
  routing policy
  gateway-observed latency
  stream duration
  timeout and error class

Backend reported:
  usage tokens when vLLM provides them
  backend status
  engine metrics exposed by vLLM

GPU/system observed:
  GPU utilization
  GPU memory
  power and saturation signals where available
```

Gateway metrics, benchmark measurements, backend usage, and GPU metrics are
related signals, but none of them is the single source of truth for the whole
serving path.

Every saved experiment should record where the benchmark runner, gateway, vLLM
backend, and metrics stack ran, plus the network path between them. A
Mac-to-remote-vLLM run over Tailscale is useful gateway-path evidence, but it is
not the same measurement as a same-host gateway-to-vLLM run or a backend-only
vLLM benchmark.

## Failure Policy

Milestone 1 should fail loudly and preserve evidence.

- Do not retry chat completion generation requests automatically.
- Do not attempt streaming retries after any response bytes have been sent.
- Return a clear OpenAI-compatible error envelope where possible.
- Record request ID, selected backend, HTTP status, timeout class, and error
  class in logs and metrics.
- Preserve backend error details in logs or experiment artifacts, with
  redaction added before public exposure if needed.

Failing loudly does not mean exposing backend stack traces to public clients. It
means errors are visible in metrics, logs, and saved benchmark artifacts.

## Expected Artifacts

- runnable FastAPI gateway
- external vLLM backend config
- remote GPU vLLM setup/run artifacts under `deploy/vllm/`
- Docker Compose deployment for gateway, Prometheus scraping, and benchmark
  support
- configurable local or remote vLLM backend URL
- streaming and non-streaming `/v1/chat/completions`
- `/v1/models` returning gateway public model aliases
- Prometheus metrics for gateway-observed request behavior
- reproducible benchmark command against the gateway endpoint
- saved results under `experiments/001_vllm_gateway_baseline/`
