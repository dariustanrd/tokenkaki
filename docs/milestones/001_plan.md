# Milestone 1 vLLM Gateway Baseline

## Summary
Implement Milestone 1 as vertical tracer-bullet slices, not horizontal layer work. Each slice must produce a narrow end-to-end path through config, gateway, backend integration, observability, deployment/docs, and tests so progress is demoable at every step.

This aligns with `AGENTS.md` by keeping `tokenkaki.gateway` as the only runtime service, using `uv`, placing code under `src/tokenkaki/`, using real external vLLM over HTTP, preserving metric provenance, and saving benchmark artifacts under `experiments/001_vllm_gateway_baseline/`.

The repo should also be cloneable on the remote NVIDIA GPU machine. That clone owns setup/run artifacts for the external vLLM backend, while the local macOS clone owns gateway development. vLLM remains a separately managed backend process, not code imported by or embedded inside `tokenkaki.gateway`.

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

3. **Remote vLLM Dev-Lab Setup** - Pending
   - Add `deploy/vllm/` setup docs and scripts for running external vLLM on a Linux NVIDIA GPU machine cloned from the same repo.
   - Include environment examples for the default dev model `Qwen/Qwen3-0.6B`, bind host, port, and any model/cache paths needed by the remote machine.
   - Document Tailscale access from the macOS gateway dev environment to the remote vLLM OpenAI-compatible endpoint.
   - Add smoke-test commands for direct remote vLLM `/v1/models` and `/v1/chat/completions` calls before routing traffic through the gateway.
   - Why: makes the real backend reproducible without turning vLLM into a `tokenkaki` runtime service.
   - Implication: the same repo can be used on both machines, but gateway code still treats vLLM as an external HTTP dependency.

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
   - Add `deploy/compose/` for gateway and Prometheus scraping only; vLLM remains a separately managed local or remote GPU-backed server.
   - Add benchmark commands under `benchmarks/` using vLLM benchmark tooling against the gateway OpenAI chat endpoint.
   - Add `experiments/001_vllm_gateway_baseline/` with `README.md`, `commands.md`, `configs/`, `raw/`, `plots/`, and `report.md`.
   - Why: every stage must produce runnable/deployable code, a reproducible benchmark command, saved artifacts, and interpretation.
   - Implication: benchmark-observed latency, gateway-observed latency, backend usage, and GPU metrics are kept separate.

## Local And Remote Development Topology
- Local macOS machine: runs gateway development, unit tests, local smoke tests, docs, and benchmark clients when measuring Mac-to-remote behavior.
- Remote NVIDIA GPU machine: runs vLLM as an external OpenAI-compatible HTTP server from the same cloned repo's `deploy/vllm/` artifacts.
- Network path: macOS gateway reaches vLLM over Tailscale using a private Tailnet hostname or IP.
- Security posture: keep vLLM private to Tailscale or an equivalent private network for Milestone 1; public exposure, auth, quotas, and rate limits are later milestone work.
- Provenance rule: record where the benchmark runner, gateway, and vLLM backend were running for every saved experiment.

Machine placement is deployment configuration, not application architecture. The
same logical serving path should work as components move from local development
to a remote GPU host and later to rented GPU or cluster environments.

| Placement mode | Gateway | vLLM backend | Benchmark runner | Purpose |
| --- | --- | --- | --- | --- |
| Local gateway, remote backend | macOS dev machine | Remote NVIDIA GPU machine over Tailscale | macOS dev machine | Fast gateway iteration against a real GPU backend. |
| Single-node remote | Remote NVIDIA GPU machine | Same remote NVIDIA GPU machine | Remote machine or macOS | Remove gateway-to-backend Tailnet latency and validate one-box deployment. |
| Cloud single-node | Rented GPU VM | Same rented GPU VM or private peer VM | Local or cloud runner | Reproduce the baseline on rented infrastructure with explicit cost notes. |
| Cluster milestone | Kubernetes or cluster control plane | GPU node pool | Dedicated benchmark runner | Study orchestration, multi-node serving, and distributed observability later. |

Implication: early Mac-to-remote measurements are useful gateway-path evidence,
but they should not be described as raw backend performance. Later same-node and
cloud runs should use the same config fields with different backend URLs so the
code path stays comparable.

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
  - remote vLLM startup from `deploy/vllm/` docs or scripts on the NVIDIA GPU machine
  - Mac can reach remote vLLM over Tailscale with direct `/v1/models` and non-streaming `/v1/chat/completions` smoke tests
  - gateway can be run on the remote machine with a loopback vLLM backend URL for single-node validation
  - Compose starts gateway and Prometheus with configurable remote vLLM URL
  - `curl` verifies health, models, non-streaming chat, and streaming chat against real vLLM
  - documented vLLM benchmark command runs against the gateway and saves raw output under the milestone experiment folder

## Assumptions
- Default dev model alias is `qwen3-0.6b`, mapped to `Qwen/Qwen3-0.6B`.
- vLLM is external and OpenAI-compatible over HTTP for Milestone 1.
- The primary dev backend may run on a remote NVIDIA GPU machine reachable from macOS over Tailscale.
- The same repo may be cloned on both machines; role-specific artifacts must stay clearly separated.
- vLLM benchmark tooling is the first reproducible benchmark path; GenAI-Perf can be added later for richer OpenAI-compatible endpoint behavior.
- Mocked HTTP backends may be used only in tests, clearly separate from real serving code.
- Public docs and experiment writeups must avoid presenting synthetic or mocked results as real model-serving results.
