# Milestone 2: Routing Policy Comparison

## Goal

Build the first multi-backend routing layer for `tokenkaki.gateway` and compare
simple LLM serving routing policies against real external vLLM replicas.

Milestone 2 should answer one concrete question: how do routing policy choices
change latency, TTFT, TPOT, throughput, queue pressure, and worker balance when
OpenAI-compatible chat traffic can be sent to more than one eligible vLLM
backend?

This document is the canonical Milestone 2 design contract for serving
boundaries, topology assumptions, routing policy scope, observability, failure
policy, benchmark evidence, and expected artifacts. The companion `002_plan.md`
tracks tracer-bullet execution status and should link here instead of duplicating
contract prose.

## Non-Goals

- Do not use mock workers for Milestone 2 planning, implementation, benchmarks,
  docs, or public interpretation.
- Do not present synthetic or simulated routing results as model-serving results.
- Do not introduce worker agents, a fleet control plane, dynamic worker
  registration, or agent-job scheduling.
- Do not introduce Kubernetes unless a separate Kubernetes experiment explicitly
  starts.
- Do not add SGLang before the vLLM routing path is measurable.
- Do not import, embed, or modify vLLM internals.
- Do not add auth, quotas, or public-demo access controls as part of routing
  policy comparison unless a separate public-demo requirement appears.
- Do not add cache-aware, prefix-aware, or KV-locality routing in this milestone;
  that remains a later cache-aware routing milestone.
- Do not hide backend failures behind automatic generation retries in the first
  routing slices.

## Serving Boundary

The Milestone 2 runtime boundary extends the Milestone 1 path from one backend to
a backend set:

```text
client, demo UI, or benchmark runner
  -> tokenkaki.gateway
  -> router policy over eligible backend replicas
  -> selected external vLLM OpenAI-compatible HTTP server
  -> model runtime / GPU execution
```

The gateway remains the only `tokenkaki` runtime service. vLLM workers are
separately managed external HTTP servers. The gateway owns request accounting,
backend eligibility, routing decisions, selected-backend observability, and
OpenAI-compatible response forwarding. vLLM owns model execution.

## Topology Assumptions

Milestone 2 should plan for three real-backend topology modes, while prioritizing
the first two in the initial tracer bullets.

| Topology mode | Backend shape | Purpose | Measurement implication |
| --- | --- | --- | --- |
| One A100, multiple vLLM replicas | Multiple vLLM servers on one GPU where memory allows, usually with a smaller model such as `Qwen/Qwen3-0.6B` or `Qwen/Qwen3-1.7B` | Cheapest real-backend routing development path | Useful for router correctness and policy comparison under constrained capacity, but results must record shared-GPU contention. |
| Multiple A100s, one vLLM replica per GPU | Multiple vLLM servers on the same host, each pinned to a different GPU | First strong real routing comparison | Best early evidence for worker balance and tail-latency policy behavior without multi-node network noise. |
| Multiple nodes | vLLM replicas on separate machines or rented GPU nodes | Later portability and network-awareness evidence | Record network path, placement, cost, startup, teardown, and failure behavior separately. This is not required for the first MS2 acceptance slice. |

Model choice depends on topology. Use the largest model that makes the topology
runnable and repeatable:

- Prefer `Qwen/Qwen3-8B` where each replica has enough GPU memory and the run is
  meant to support public or portfolio interpretation.
- Use `Qwen/Qwen3-0.6B` or `Qwen/Qwen3-1.7B` for one-GPU multi-replica routing
  development when 8B replicas are not practical.
- Record the exact model, vLLM version, GPU placement, served model names,
  backend ports, and any shared-GPU contention in experiment artifacts.

## Request Handling

The gateway should remain a transparent OpenAI-compatible forwarding layer with a
thin parsed envelope. It may parse only the fields required for gateway
responsibilities:

- requested public `model`
- `stream`
- request ID and accounting context
- routing policy and eligible backend set
- approximate request-size signal for context-length-aware routing
- backend selection, status, timeout class, and error class

The original request body remains the source of truth and should be forwarded to
vLLM with minimal mutation. The gateway may rewrite the public model alias to the
selected backend model name. Model-specific generation controls such as Qwen3
`chat_template_kwargs` must be preserved.

## Model, Backend Set, And Policy Config

Milestone 2 should evolve the static config-backed registry from one backend per
model to a small static backend set per model. Static config remains a bootstrap
mechanism, not a long-term control plane.

The config should describe serving intent:

- public model alias
- enabled state
- routing policy for the model or backend group
- backend group of one or more backend targets
- backend target ID
- backend engine type, initially `vllm`
- backend base URL
- backend model name when it differs from the public alias
- configured enabled/disabled state for the backend target
- optional backend metadata useful for experiments, such as GPU label, node label,
  or notes

Observed runtime state should not be manually encoded as truth in config. Health,
availability, outstanding request count, errors, and backend model lists are
runtime signals.

The first implementation should support both single-backend and multi-backend
model configs as first-class valid operating modes. A one-backend model is not
legacy behavior; it is the correct shape when an experiment or deployment truly
has only one backend target. In that case, the gateway should keep using the
`static_single_backend` policy label or an equivalent explicit single-target
policy label.

## Routing Policies

Implement routing policies as small, explicit scheduler choices over eligible
backend targets.

### Static single backend

Compatibility policy for a model with one backend target. This preserves the
Milestone 1 behavior and provides a baseline for regression tests.

### Round-robin

Select the next eligible backend in a stable cycle.

Why it matters: round-robin is the ordinary HTTP-load-balancer baseline. It is
simple and easy to reason about, but it does not know whether an LLM request is
short, long, already streaming, or tying up backend decode capacity.

### Least-outstanding

Select the eligible backend with the fewest gateway-observed outstanding chat
completion requests.

Outstanding count should increment when a backend is selected and decrement when
the request is fully complete:

- non-streaming: after the backend response or failure is handled
- streaming: after stream completion, client disconnect, backend read failure, or
  stream setup failure cleanup

Why it matters: LLM generations can be long-lived, so counting only request
arrival distribution is not enough. This policy teaches how in-flight work affects
queueing and tail latency.

### Context-length-aware routing

Select using a simple gateway-owned request-size heuristic. For Milestone 2, use
a transparent approximation such as message character counts, message count, or
known request fields rather than adding tokenizer integration.

The heuristic must be documented in benchmark artifacts and writeups. It is a
routing signal for policy comparison, not an authoritative token count.

Why it matters: LLM backends experience very different prefill and decode costs
for different prompt and output shapes. Even an approximate request-size signal
can show why LLM routing is not the same as ordinary HTTP load balancing.

## Health And Eligibility

Milestone 2 should start with two eligibility signals:

1. **Configured enabled state**: disabled backend targets are excluded.
2. **Lightweight active health check**: the gateway can determine whether a
   backend target is reachable before selecting it for normal traffic.

Initial health checks may call a simple backend endpoint such as `/v1/models` or
another vLLM-compatible health endpoint if available. Health state should be
observable but should not become a full control plane.

If no backend is eligible for a requested model, the gateway should fail loudly
with a clear OpenAI-compatible error response and metrics that identify the model,
routing policy, and error class.

## Failure Policy

Milestone 2 should continue the Milestone 1 fail-loud policy.

- Do not retry normal generation requests automatically in the first routing
  slices.
- Do not retry streaming requests after any response bytes have been sent.
- Record request ID, requested model, selected backend, routing policy, status,
  timeout class, and error class.
- Preserve backend failures in metrics and logs so routing policy behavior remains
  interpretable.
- A failed selected backend request should not be hidden by silent failover during
  policy-comparison benchmarks.

Failing loudly does not mean exposing backend stack traces to public clients. It
means failures are visible in logs, metrics, and saved benchmark artifacts.

## Observability Contract

Milestone 2 should preserve the Milestone 1 metric-provenance rules and add
routing-specific visibility.

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
  requested model
  selected backend
  routing policy
  routing decision count
  outstanding request count where available
  gateway-observed latency
  stream duration
  timeout and error class

Backend reported:
  usage tokens when vLLM provides them
  backend status
  backend model list / health response
  vLLM metrics where scraped

GPU/system observed:
  GPU utilization
  GPU memory
  power and saturation signals where available
```

Gateway-observed latency, benchmark-observed latency, backend-reported usage,
routing state, and GPU metrics are related signals, but none of them is the single
source of truth for the whole serving path.

Grafana and GPU/system correlation become important in this milestone. The first
routing slices may validate with Prometheus metrics only, but policy-comparison
experiments should plan to save Prometheus snapshots and add Grafana/DCGM evidence
where the environment supports it.

## Benchmark Evidence Ladder

Milestone 2 should produce a layered benchmark set so policy differences can be
interpreted instead of reduced to one number.

Run the evidence ladder in this order:

1. **Direct backend smoke checks**: verify each vLLM worker responds directly on
   its own `/v1/models` and `/v1/chat/completions` path before gateway routing.
2. **Single-backend gateway compatibility**: run the existing Milestone 1-style
   gateway benchmark against one backend target to ensure no routing refactor
   regresses the baseline path.
3. **Multi-backend gateway smoke**: send a small number of requests through the
   gateway and confirm selected-backend metrics show traffic reaching more than
   one real backend.
4. **Policy-specific serving benchmarks**: run the same workload against the same
   backend set under `round_robin`, `least_outstanding`, and
   `context_length_aware`.
5. **Mixed workload benchmark**: use a workload with short and long prompt/output
   shapes to expose tail-latency and worker-balance differences.
6. **Comparison and interpretation**: compare policy results under the same
   topology, model, request rate, prompt/output mix, backend flags, GPU placement,
   and gateway deployment.

The current `vllm bench serve` wrapper should remain the continuity path for
serving benchmarks. Add a small custom benchmark driver only if `vllm bench serve`
cannot express the mixed workload needed for routing comparison.

Suggested artifact layout:

```text
experiments/2_routing_policy_comparison/
  README.md
  configs/
    gateway-round-robin.yaml
    gateway-least-outstanding.yaml
    gateway-context-length-aware.yaml
    backend-workers.md
  1_backend_smoke/
    worker-a.json
    worker-b.json
    log.out
  2_single_backend_compatibility/
    vllm-gateway-single-backend.json
    gateway-metrics-after-benchmark.prom
    log.out
  3_round_robin/
    vllm-gateway-round-robin.json
    gateway-metrics-after-benchmark.prom
    log.out
  4_least_outstanding/
    vllm-gateway-least-outstanding.json
    gateway-metrics-after-benchmark.prom
    log.out
  5_context_length_aware/
    vllm-gateway-context-length-aware.json
    gateway-metrics-after-benchmark.prom
    log.out
  6_mixed_workload_comparison/
    round-robin.json
    least-outstanding.json
    context-length-aware.json
    summary.json
    log.out
  plots/
```

The report should separate:

- direct backend readiness checks
- single-backend compatibility evidence
- per-policy gateway benchmark results
- mixed-workload comparison results
- gateway-observed routing and selected-backend metrics
- backend/GPU/system observations where available
- topology and model limitations

## Expected Artifacts

- static config shape supporting backend sets per public model
- compatibility path for the existing single-backend gateway setup
- router policy facade with `static_single_backend`, `round_robin`,
  `least_outstanding`, and `context_length_aware`
- gateway integration for policy-selected backend routes
- outstanding-request tracking that handles non-streaming and streaming lifecycles
- lightweight active backend health checks and no-eligible-backend failure path
- Prometheus metrics for routing decisions, selected backend, routing policy,
  errors, and outstanding requests where practical
- runbook updates for launching one-A100 and multi-A100 real vLLM replica layouts
- benchmark commands for policy comparison
- saved real-backend artifacts under `experiments/2_routing_policy_comparison/`
- writeup comparing routing policies and explaining tail-latency behavior
