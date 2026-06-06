# tokenkaki Vision

`tokenkaki` is a staged, runnable LLM inference platform for learning, building,
and measuring realistic OpenAI-compatible serving systems.

Canonical source note: this document owns the project purpose, learning goals,
principles, and non-goals. Use the README for navigation,
[`ARCHITECTURE.md`](ARCHITECTURE.md) for serving/runtime boundaries, and
[`ROADMAP.md`](ROADMAP.md) for phase and milestone sequencing.

The project focuses on real serving behavior: requests enter through an
OpenAI-compatible gateway, move through routing and scheduling decisions, reach
real vLLM or SGLang backends, and produce metrics that can be benchmarked,
interpreted, and improved.

A possible later expansion is a heterogeneous enterprise inference fabric, but
the project should earn that platform arc by first measuring the serving
fundamentals in the original roadmap.

## Learning Objective

The main learning objective is to understand the full inference serving path:

```text
client request
  -> OpenAI-compatible gateway
  -> router / scheduler
  -> real backend client
  -> vLLM / SGLang worker
  -> GPU execution
  -> observability
  -> benchmark result
  -> deployment or tuning decision
```

Each stage should make one part of that path more concrete. The project should
help answer questions such as:

- How do TTFT, TPOT, total latency, and throughput change under different
  workloads?
- How do routing policies affect tail latency and backend utilization?
- How do batching, context length, output length, and KV cache behavior affect
  real serving performance?
- What changes when serving moves from one backend to multiple replicas,
  Kubernetes, multi-GPU, or multi-node deployments?
- How do benchmark results translate into deployment, scaling, and cost
  tradeoffs?
- Which signals would a future fleet scheduler need before it can make credible
  placement decisions across heterogeneous machines?

Each stage should be explainable as a concrete systems artifact: working
endpoint or deployment, benchmark evidence, saved results, and a
blog-post-ready interpretation.

## Project Principles

- Real backends are the normal serving path.
- Mock workers are only for tests, synthetic load generation, and controlled
  benchmark scenarios. Synthetic results must be labeled clearly and must not
  be presented as real serving results.
- Model targets depend on the phase and must be verified before implementation;
  the current phase index lives in [`ROADMAP.md`](ROADMAP.md).
- Every stage must be runnable.
- Every stage must produce benchmark evidence.
- Every result should be written up with enough detail to reproduce and explain.
- Deployment realism matters, but expensive infrastructure should be controlled
  with quotas, teardown scripts, replay modes, and clear operating limits.

## Non-Goals

- Building a general-purpose model hosting product before the serving path is
  understood.
- Treating a single vLLM endpoint as the final system.
- Entangling mock workers with production serving code.
- Adding dashboards, schedulers, or orchestration layers before they are tied to
  measurable serving behavior.
- Building worker agents, fleet registration, network policy, or
  deadline-aware agent-job scheduling before the original serving roadmap has
  produced routing, tuning, topology, and cache-locality evidence.
