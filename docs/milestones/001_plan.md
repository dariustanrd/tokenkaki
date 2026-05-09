# Milestone 1 vLLM Gateway Baseline

## Summary
Implement Milestone 1 as vertical tracer-bullet slices, not horizontal layer work. Each slice must produce a narrow end-to-end path through config, gateway, backend integration, observability, deployment/docs, and tests so progress is demoable at every step.

This aligns with `AGENTS.md` by keeping `tokenkaki.gateway` as the only runtime service, using `uv`, placing code under `src/tokenkaki/`, using real external vLLM over HTTP, preserving metric provenance, and saving benchmark artifacts under `experiments/001_vllm_gateway_baseline/`.

Milestone 1 development now happens directly on the NVIDIA GPU machine. This
single working clone owns gateway development, setup/run artifacts for the
external vLLM backend, local smoke tests, benchmark clients, and experiment
artifacts. vLLM remains a separately managed backend process, not code imported
by or embedded inside `tokenkaki.gateway`.

## Tracer-Bullet Slices
1. **Runnable Gateway Skeleton** - Completed
   - Add `uv` Python project scaffold and `src/tokenkaki/`.
   - Implement `tokenkaki.gateway` FastAPI app with `/healthz` and `/metrics`.
   - Add basic Prometheus request metrics and structured request IDs.
   - Completed artifacts: `pyproject.toml`, `uv.lock`, `src/tokenkaki/`, `tokenkaki.gateway` app factory and runtime entrypoint, and gateway skeleton tests.
   - Verified with: `uv run pytest`, `uv run uvicorn tokenkaki.gateway:app --host 127.0.0.1 --port 8000`, `curl /healthz`, and `curl /metrics`.
   - Why: proves the runtime service, packaging, and observability base work early.
   - Implication: later slices extend the same service instead of introducing new top-level services.

2. **Static Registry To `/v1/models`** - Completed
   - Add static YAML config for public model alias `qwen3-0.6b`, backend type `vllm`, backend URL, backend model `Qwen/Qwen3-0.6B`, and enabled state.
   - Implement config and registry functional facades.
   - Expose `/v1/models` from enabled public aliases only.
   - Completed artifacts: packaged default gateway YAML config, config loader facade, static registry facade, model route resolution, and `/v1/models` endpoint.
   - Verified with: `uv run pytest`, `uv run uvicorn tokenkaki.gateway:app --host 127.0.0.1 --port 8000`, `curl /v1/models`, and `curl /metrics`.
   - Why: establishes the bootstrap registry without pretending config is long-term runtime state.
   - Implication: health/load/backend model lists stay runtime signals for later milestones.

3. **Local GPU vLLM Dev-Lab Setup** - Pending
   - Add `deploy/vllm/` setup docs and scripts for running external vLLM on this Linux NVIDIA GPU machine from the working repo clone.
   - Include environment examples for the default dev model `Qwen/Qwen3-0.6B`, bind host, port, and any model/cache paths needed by the GPU machine.
   - Prefer loopback or private-host binding for Milestone 1 development, with any remote client access documented as optional and explicitly separate from baseline measurement.
   - Add smoke-test commands for direct local vLLM `/v1/models` and `/v1/chat/completions` calls before routing traffic through the gateway.
   - Why: makes the real backend reproducible without turning vLLM into a `tokenkaki` runtime service.
   - Implication: the default dev path removes private-network gateway/backend noise while gateway code still treats vLLM as an external HTTP dependency.

4. **Non-Streaming Chat Forwarding** - Pending
   - Implement `POST /v1/chat/completions` for non-streaming requests.
   - Parse only `model`, `stream`, request ID, and routing/accounting fields.
   - Forward the original OpenAI-compatible body to external vLLM with minimal mutation, changing only backend model name when needed.
   - Add vLLM HTTP backend client; do not import or embed vLLM internals.
   - Why: validates the core request path through gateway to real backend.
   - Implication: failures are visible as gateway/backend evidence instead of hidden behind retries.

5. **Streaming Chat Forwarding** - Pending
   - Add streaming SSE proxy support for `stream: true`.
   - Preserve vLLM chunks as OpenAI-compatible SSE.
   - Record stream start, end, duration, selected backend, status, timeout class, error class, and detectable client disconnects.
   - Do not retry after response bytes are sent.
   - Why: streaming is an early serving-path requirement, not a later enhancement.
   - Implication: TTFT/TPOT remain benchmark-observed metrics; gateway metrics track stream lifecycle.

6. **Fail-Loud Error And Metrics Contract** - Pending
   - Return clear OpenAI-compatible error envelopes for unknown model, disabled model, backend HTTP error, timeout, connection failure, and unexpected gateway error.
   - Log request ID, selected backend, status, timeout class, and error class.
   - Emit Prometheus metrics for request count, status, selected backend, routing policy, latency, stream duration, backend errors, and token counts when available.
   - Why: Milestone 1 should preserve evidence for learning.
   - Implication: no auth, quotas, smart retries, or failover are added yet.

7. **Compose, Benchmark, And Experiment Artifact Path** - Pending
   - Add `deploy/compose/` for gateway and Prometheus scraping only; vLLM remains a separately managed GPU-backed server on this machine for Milestone 1.
   - Add benchmark commands under `benchmarks/` using vLLM benchmark tooling against the gateway OpenAI chat endpoint.
   - Add `experiments/001_vllm_gateway_baseline/` with `README.md`, `commands.md`, `configs/`, `raw/`, `plots/`, and `report.md`.
   - Why: every stage must produce runnable/deployable code, a reproducible benchmark command, saved artifacts, and interpretation.
   - Implication: benchmark-observed latency, gateway-observed latency, backend usage, and GPU metrics are kept separate.

## Direct GPU Development Topology
- NVIDIA GPU machine: runs gateway development, unit tests, local smoke tests, docs, benchmark clients, vLLM, and the Milestone 1 metrics stack from this working repo clone.
- Default network path: benchmark/client -> `tokenkaki.gateway` -> external vLLM over loopback or a private host interface on the same machine.
- Optional remote client path: another machine may call the gateway or vLLM over Tailscale or an equivalent private network for convenience, but that path must be labeled separately from same-host baseline results.
- Security posture: keep vLLM private to loopback, the host network, Tailscale, or an equivalent private network for Milestone 1; public exposure, auth, quotas, and rate limits are later milestone work.
- Provenance rule: record where the benchmark runner, gateway, and vLLM backend were running for every saved experiment.

Machine placement is deployment configuration, not application architecture. The
same logical serving path should work as components move from direct development
on this GPU host to rented GPU or cluster environments.

| Placement mode | Gateway | vLLM backend | Benchmark runner | Purpose |
| --- | --- | --- | --- | --- |
| Direct GPU dev baseline | NVIDIA GPU machine | Same NVIDIA GPU machine | Same NVIDIA GPU machine | Default Milestone 1 path for code, smoke tests, and baseline measurements without gateway/backend network noise. |
| Cloud single-node | Rented GPU VM | Same rented GPU VM or private peer VM | Local or cloud runner | Reproduce the baseline on rented infrastructure with explicit cost notes. |
| Cluster milestone | Kubernetes or cluster control plane | GPU node pool | Dedicated benchmark runner | Study orchestration, multi-node serving, and distributed observability later. |

Implication: same-host measurements are now the default Milestone 1 baseline.
Cloud runs should use the same config fields with different backend URLs 
so the code path stays comparable.

## Public Interfaces And Boundaries
- Runtime service: only `tokenkaki.gateway`.
- Public endpoints: `GET /healthz`, `GET /metrics`, `GET /v1/models`, `POST /v1/chat/completions`.
- Static config fields: public model name, backend engine type `vllm`, backend base URL, optional backend model name, enabled state, and basic limits where useful.
- Routing policy label: `static_single_backend`.
- vLLM setup artifacts may live under `deploy/vllm/`, but vLLM is not imported, embedded, or managed inside `tokenkaki.gateway`.
- No top-level `services/`, no Kubernetes manifests, no Rust, no SGLang, no mock worker in the serving path.

## Test Plan
- Unit tests for config loading, registry alias resolution, router selection, and error envelope shape.
- Gateway tests for health, metrics, `/v1/models`, unknown model rejection, non-streaming forwarding, streaming SSE proxying, backend 4xx/5xx, timeout, and connection failure.
- Acceptance checks:
  - `uv run pytest`
  - local gateway startup with `uv run uvicorn`
  - local vLLM startup from `deploy/vllm/` docs or scripts on the NVIDIA GPU machine
  - direct local vLLM `/v1/models` and non-streaming `/v1/chat/completions` smoke tests pass before gateway routing
  - gateway runs on the same GPU machine with a loopback vLLM backend URL for single-node validation
  - Compose starts gateway and Prometheus with configurable vLLM URL
  - `curl` verifies health, models, non-streaming chat, and streaming chat against real vLLM
  - documented vLLM benchmark command runs against the gateway and saves raw output under the milestone experiment folder

## Assumptions
- Default dev model alias is `qwen3-0.6b`, mapped to `Qwen/Qwen3-0.6B`.
- vLLM is external and OpenAI-compatible over HTTP for Milestone 1.
- The primary dev environment is this NVIDIA GPU machine.
- The same repo clone owns gateway development, vLLM setup artifacts, benchmark commands, and saved experiment artifacts for Milestone 1.
- vLLM benchmark tooling is the first reproducible benchmark path; GenAI-Perf can be added later for richer OpenAI-compatible endpoint behavior.
- Mocked HTTP backends may be used only in tests, clearly separate from real serving code.
- Public docs and experiment writeups must avoid presenting synthetic or mocked results as real model-serving results.
