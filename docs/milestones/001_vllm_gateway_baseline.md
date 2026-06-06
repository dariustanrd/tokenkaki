# Milestone 1: vLLM Gateway Baseline

## Goal

Build a minimal OpenAI-compatible gateway that calls an external vLLM server and
produces credible baseline measurements for the public serving path.

Milestone 1 should answer one concrete question: what happens when a client or
benchmark sends OpenAI-compatible chat requests through `tokenkaki.gateway` to a
real vLLM backend?

This document is the canonical Milestone 1 design contract for serving
boundaries, topology, request handling, observability, failure policy, and
expected artifacts. The companion `001_plan.md` tracks tracer-bullet execution
status and should link here instead of duplicating contract prose.

## Non-Goals

- Do not import, embed, or modify vLLM internals.
- Do not add auth, quotas, or public-demo access controls yet.
- Do not add smart retries or failover for generation requests.
- Do not turn the gateway into a benchmark-results service.
- Do not introduce Kubernetes before the gateway, metrics, and baseline
  benchmark path are working.
- Do not add top-level `services/`, Rust, SGLang, or mock workers to the
  Milestone 1 serving path.

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

Component placement may change without changing this boundary. Milestone 1 now
defaults to direct development on the NVIDIA GPU machine, with the gateway,
vLLM, metrics stack, benchmark tooling, and experiment artifacts managed from
the same working repo clone. Future milestones may move the same roles onto
rented GPU VMs or clusters. These are deployment placements, not different
application architectures.

| Placement mode | Component placement | Measurement implication |
| --- | --- | --- |
| Direct GPU dev baseline | Benchmark runner, gateway, vLLM, metrics stack, and artifacts on the NVIDIA GPU machine | Default Milestone 1 baseline; minimizes gateway-to-backend network noise. |
| Rented single-node reproduction | Same roles on a rented GPU VM, or benchmark runner on a private client | Useful for cost and portability evidence; record network path and provider details separately. |
| Future cluster milestone | Gateway, backend workers, metrics, and benchmark runner split across cluster roles | Not Milestone 1 baseline; used later to study orchestration, service networking, and distributed observability. |

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

Generation controls are normally backend/model concerns. For Qwen3, thinking
and non-thinking mode should be controlled through vLLM-supported request fields
such as `chat_template_kwargs.enable_thinking` or through vLLM server defaults.
The gateway should preserve those fields when forwarding the request. It should
not silently strip `<think>` content, raise `max_tokens`, or synthesize a final
answer if the backend stops before leaving the thinking block. If this becomes a
common failure mode, the gateway may add explicit fail-loud validation or
warning headers, such as warning when `enable_thinking: true` is paired with a
low `max_tokens`.

Milestone 1 endpoints:

- `GET /healthz`
- `GET /metrics`
- `GET /v1/models`
- `POST /v1/chat/completions`

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

The initial routing policy label is `static_single_backend`.

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
backend, and metrics stack ran, plus the network path between them. Same-host
gateway-to-vLLM runs are the default Milestone 1 baseline.

## Benchmark Evidence Ladder

Milestone 1 should produce a small but layered benchmark set instead of only a
single gateway result. The gateway benchmark remains the milestone acceptance
path, but backend-only baselines make the final result easier to interpret.

Run the evidence ladder in this order:

1. **vLLM engine latency**: use `vllm bench latency` to measure one controlled
   in-process vLLM batch. This is the lower-level latency floor for the selected
   model, GPU, input length, output length, dtype, and vLLM engine flags.
2. **vLLM engine throughput**: use `vllm bench throughput` to measure offline
   engine token throughput without HTTP serving or gateway overhead. This is the
   raw backend capacity reference.
3. **Direct vLLM serving**: use `vllm bench serve` against the running vLLM
   OpenAI-compatible server. This measures online HTTP serving behavior,
   including request scheduling, streaming cadence, TTFT, TPOT/ITL, and server
   overhead.
4. **Gateway serving**: use `vllm bench serve` against `tokenkaki.gateway`.
   This measures the public Milestone 1 path:

   ```text
   benchmark client
     -> tokenkaki.gateway
     -> external vLLM OpenAI-compatible HTTP server
     -> GPU execution
   ```

5. **Comparison**: compare direct vLLM serving with gateway serving under the
   same model, request rate, prompt length, output length, sampling settings,
   GPU, and vLLM server flags. The difference is the first estimate of gateway
   overhead for the public path.

The first two steps are backend baselines, not gateway acceptance checks. They
should not block validating the gateway path, but they should be saved for any
Milestone 1 result that will be interpreted or published.

Suggested raw artifact names:

```text
experiments/001_vllm_gateway_baseline/raw/
  vllm-latency-qwen3-8b-a100.json
  vllm-throughput-qwen3-8b-a100.json
  vllm-direct-serving-qwen3-8b-a100.json
  vllm-gateway-serving-qwen3-8b-a100.json
  gateway-metrics-after-qwen3-8b-a100.prom
  prometheus-targets-after-qwen3-8b-a100.json
```

The report should separate:

- engine-only latency and throughput
- direct vLLM server behavior
- gateway-to-vLLM public-path behavior
- gateway-observed Prometheus metrics
- GPU/system observations where available

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

## Assumptions

- Model aliases are phase-specific. The active packaged gateway config is the
  source of truth for the current runnable alias and backend model, while saved
  experiment folders preserve the exact alias and model used for historical
  runs.
- Qwen3 thinking mode is enabled by default in the model/template path. Low
  `max_tokens` can end generation inside `<think>...</think>` and produce no
  final answer; this should be documented or warned about, not silently
  repaired by the gateway.
- vLLM is external and OpenAI-compatible over HTTP for Milestone 1.
- The primary dev environment is the NVIDIA GPU machine.
- The same repo clone owns gateway development, vLLM setup artifacts, benchmark
  commands, and saved experiment artifacts for Milestone 1.
- vLLM benchmark tooling is the first reproducible benchmark path. Use
  `vllm bench latency` and `vllm bench throughput` for backend engine baselines,
  and `vllm bench serve` for direct vLLM and gateway online serving baselines.
  GenAI-Perf can be added later for richer OpenAI-compatible endpoint behavior.
- Mocked HTTP backends may be used only in tests, clearly separate from real
  serving code.
- Public docs and experiment writeups must avoid presenting synthetic or mocked
  results as real model-serving results.

## Expected Artifacts

- runnable FastAPI gateway
- external vLLM backend config
- local GPU vLLM setup/run artifacts under `deploy/vllm/`
- Docker Compose deployment for gateway, Prometheus scraping, and benchmark
  support
- configurable vLLM backend URL
- streaming and non-streaming `/v1/chat/completions`
- `/v1/models` returning gateway public model aliases
- Prometheus metrics for gateway-observed request behavior
- reproducible benchmark commands for vLLM engine latency, vLLM engine
  throughput, direct vLLM serving, and gateway serving
- saved results under `experiments/001_vllm_gateway_baseline/`
