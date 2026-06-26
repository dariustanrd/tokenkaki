# Milestone 1 vLLM Gateway Baseline

## Summary
Implement Milestone 1 as vertical tracer-bullet slices, not horizontal layer work. Each slice must produce a narrow end-to-end path through config, gateway, backend integration, observability, deployment/docs, and tests so progress is demoable at every step.

Canonical Milestone 1 serving boundaries, topology, request handling,
observability, failure policy, assumptions, and expected artifacts are defined
in `001_vllm_gateway_baseline.md`. This plan intentionally tracks execution
status, completed artifacts, verification history, and acceptance checks instead
of restating the design contract.

Current packaged gateway config uses public alias `qwen3-8b` backed by
`Qwen/Qwen3-8B`. Earlier slice notes and saved experiment artifacts that mention
`qwen3-0.6b` are historical provenance for the first validated run, not the
current default.

Milestone 1 engineering acceptance evidence has been regenerated for the
current `qwen3-8b` default under
`experiments/1_vllm_v0.19.1_Qwen3-8B/`. The saved ladder covers vLLM engine
latency, vLLM engine throughput, direct vLLM serving, gateway serving, gateway
metrics snapshots, Prometheus target snapshots, and gateway timing summaries.
The public writeup is tracked separately from this execution plan.

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

3. **Local GPU vLLM Dev-Lab Setup** - Completed
   - Add `deploy/vllm/` setup docs and scripts for running external vLLM on this Linux NVIDIA GPU machine from the working repo clone.
   - Include environment examples for the default dev model `Qwen/Qwen3-0.6B`, bind host, port, and any model/cache paths needed by the GPU machine.
   - Prefer loopback or private-host binding for Milestone 1 development, with any remote client access documented as optional and explicitly separate from baseline measurement.
   - Add smoke-test commands for direct local vLLM `/v1/models` and `/v1/chat/completions` calls before routing traffic through the gateway.
   - Completed artifacts: `deploy/vllm/README.md`, `deploy/vllm/env.example`, `deploy/vllm/pyproject.toml`, `deploy/vllm/uv.lock`, `deploy/vllm/run-openai-server.sh`, and `deploy/vllm/smoke-openai.sh`.
   - Verified with: `UV_TORCH_BACKEND=cu118 uv lock` in `deploy/vllm/`, `bash -n deploy/vllm/run-openai-server.sh`, `bash -n deploy/vllm/smoke-openai.sh`, executable-bit checks for both scripts, and `CUDA_VISIBLE_DEVICES=4` PyTorch visibility showing one logical A100.
   - Runtime validated on this GPU environment with external vLLM reachable on the Docker-reachable host address used by the Compose gateway.
   - Why: makes the real backend reproducible without turning vLLM into a `tokenkaki` runtime service.
   - Implication: the default dev path removes private-network gateway/backend noise while gateway code still treats vLLM as an external HTTP dependency.

4. **Non-Streaming Chat Forwarding** - Completed
   - Implement `POST /v1/chat/completions` for non-streaming requests.
   - Parse only `model`, `stream`, request ID, and routing/accounting fields.
   - Forward the original OpenAI-compatible body to external vLLM with minimal mutation, changing only backend model name when needed.
   - Add vLLM HTTP backend client; do not import or embed vLLM internals.
   - Completed artifacts: `tokenkaki.backend` vLLM HTTP facade, non-streaming gateway chat route, public alias to backend model rewrite, request ID forwarding, explicit unknown-model/streaming-not-yet-supported/backend-timeout/backend-connection failure responses, and focused gateway/backend tests.
   - Verified with: `uv run pytest tests/test_backend_vllm.py tests/test_gateway_chat.py tests/test_config_registry.py tests/test_gateway_models.py tests/test_gateway_skeleton.py`.
   - Runtime validated on this GPU environment with a non-streaming `POST /v1/chat/completions` through the gateway using public model alias `qwen3-0.6b`.
   - Why: validates the core request path through gateway to real backend.
   - Implication: failures are visible as gateway/backend evidence instead of hidden behind retries.

5. **Streaming Chat Forwarding** - Completed
   - Add streaming SSE proxy support for `stream: true`.
   - Preserve vLLM chunks as OpenAI-compatible SSE.
   - Preserve model-specific request controls such as Qwen3/vLLM `chat_template_kwargs` without translating them into gateway-private flags.
   - Keep thinking and non-thinking behavior explicit in client/backend configuration: normal chat examples should use `chat_template_kwargs: {"enable_thinking": false}`, while reasoning-mode examples should use larger `max_tokens` and Qwen3-recommended sampling settings.
   - Record stream start, end, duration, selected backend, status, timeout class, error class, and detectable client disconnects.
   - Do not retry after response bytes are sent.
   - Completed artifacts: streaming vLLM HTTP facade, gateway `stream: true` SSE proxy path, raw backend SSE chunk preservation, request ID forwarding, public alias to backend model rewrite for streaming requests, stream lifecycle logs, and focused gateway/backend streaming tests.
   - Verified with: `uv run pytest tests/test_backend_vllm.py tests/test_gateway_chat.py tests/test_config_registry.py tests/test_gateway_models.py tests/test_gateway_skeleton.py`.
   - Runtime validated on this GPU environment with `curl -N` `POST /v1/chat/completions` through the gateway using `stream: true`.
   - Why: streaming is an early serving-path requirement, not a later enhancement.
   - Implication: TTFT/TPOT remain benchmark-observed metrics; gateway metrics track stream lifecycle. Truncated Qwen3 thinking outputs are backend/model behavior, so the gateway should not silently strip `<think>` content, raise `max_tokens`, or fabricate an answer.

6. **Fail-Loud Error And Metrics Contract** - Completed
  - Completed metrics scope:
     - Emit Prometheus chat completion request counts labeled by status, selected backend, routing policy, and error class.
     - Emit Prometheus backend error counts labeled by selected backend, routing policy, error class, timeout class, and backend HTTP status when available.
     - Emit Prometheus stream duration histograms for streaming requests labeled by selected backend, routing policy, stream status, and error class.
     - Emit Prometheus backend-reported token counters for prompt, completion, and total tokens when non-streaming responses include OpenAI-compatible `usage`.
     - Preserved existing gateway behavior for unknown/disabled models, backend HTTP responses, timeout envelopes, and connection failure envelopes.
   - Verified with: `uv run pytest tests/test_config_registry.py tests/test_gateway_chat.py tests/test_gateway_skeleton.py`, `uv run pytest`, and a manual non-streaming request through the gateway showing chat completion and token metrics in `/metrics`.
  - Accepted follow-up items outside Milestone 1 closure:
     - Do not yet split unknown model vs disabled model error envelopes.
     - Do not yet remap backend HTTP 4xx/5xx responses into gateway-owned error envelopes.
     - Do not yet add Qwen3 low-`max_tokens` thinking-mode warning or validation.
     - Do not yet add per-request token histograms; use cumulative Prometheus counters and add per-request values later through structured logs or tracing when needed.
  - Why: Milestone 1 should preserve evidence for learning, and metrics are the least invasive first step.
   - Implication: no auth, quotas, smart retries, failover, or broader error-policy changes are added yet.

7. **Compose, Benchmark, And Experiment Artifact Path** - Completed
   - Added `deploy/compose/` for gateway and Prometheus scraping only.
   - vLLM remains a separately managed external GPU-backed server for Milestone 1.
   - Added Compose-specific gateway config pointing from the gateway container to host vLLM through `http://host.docker.internal:8001`.
   - Added Prometheus scrape config for gateway `/metrics`.
   - Added Compose run and verification docs.
   - Added `.dockerignore` for small Docker build context.
   - Added configurable published Compose ports through `TOKENKAKI_GATEWAY_PORT` and `TOKENKAKI_PROMETHEUS_PORT`.
   - Added `benchmarks/vllm-serving-bench.sh` using pinned `vllm bench serve` with OpenAI chat endpoint settings and JSON output under `experiments/001_vllm_gateway_baseline/4_gateway_serve/`.
   - Added `benchmarks/README.md` with benchmark wrapper usage, smoke command, and provenance notes.
   - Added the experiment artifact layout under `experiments/001_vllm_gateway_baseline/`.
   - Regenerated Qwen3-8B benchmark evidence under
     `experiments/1_vllm_v0.19.1_Qwen3-8B/` with the Milestone 1 ladder:
     - `1_latency/vllm-latency-qwen3-8b-a100.json`
     - `2_throughput/vllm-throughput-qwen3-8b-a100.json`
     - `3_direct_vllm_serve/vllm-direct-serving-qwen3-8b-a100.json`
     - `3_direct_vllm_serve/vllm-direct-serving-qwen3-8b-a100-detailed.json`
     - `4_gateway_serve/vllm-gateway-serving-qwen3-8b-a100.json`
     - `4_gateway_serve/vllm-gateway-serving-qwen3-8b-a100-detailed.json`
     - `5_gateway_serve_gateway-timed/gateway-metrics-after-benchmark.prom`
     - `5_gateway_serve_gateway-timed/prometheus-up-after-benchmark.json`
     - `5_gateway_serve_gateway-timed/gateway-timing-summary.json`
     - `6_gateway_serve_pooled-client/vllm-gateway-serving-qwen3-8b-a100-pooled-client.json`
     - `6_gateway_serve_pooled-client/gateway-timing-summary.json`
   - Verified with:
     - `docker compose -f deploy/compose/compose.yaml config`.
     - `TOKENKAKI_GATEWAY_PORT=18000 TOKENKAKI_PROMETHEUS_PORT=19090 docker compose -f deploy/compose/compose.yaml up --build -d`.
     - `curl http://127.0.0.1:18000/healthz`.
     - `curl http://127.0.0.1:18000/v1/models`.
     - `curl http://127.0.0.1:18000/metrics`.
     - `curl 'http://127.0.0.1:19090/api/v1/targets?state=active'` showing Prometheus target health `up`.
     - Final acceptance checks: `uv run pytest`, direct external vLLM `/v1/models`, Compose gateway non-streaming chat, Compose gateway streaming chat, and Prometheus target health.
     - A Compose chat request while vLLM was bound to host loopback produced the expected gateway `502` and backend connection failure metrics, confirming the failure is visible.
     - Restarted external vLLM with `VLLM_HOST=172.17.0.1 ./deploy/vllm/run-openai-server.sh`, then verified a successful non-streaming `/v1/chat/completions` request through the Compose gateway on `http://127.0.0.1:18000`.
     - `vllm bench latency` saved engine latency output for Qwen3-8B on one A100.
     - `vllm bench throughput` saved offline engine throughput output for Qwen3-8B on one A100.
     - `vllm bench serve` completed direct vLLM serving runs with 100/100 successful requests.
     - `vllm bench serve` completed gateway serving runs with 100/100 successful requests.
     - Gateway metrics, Prometheus target snapshots, and gateway timing summaries were saved after benchmark runs.
     - A pooled-client gateway run showed the gateway path matching the direct vLLM TTFT profile much more closely than the earlier unpooled gateway run, making the client-connection overhead visible as measured evidence.
   - Why: every stage must produce runnable/deployable code, a reproducible benchmark command, saved artifacts, and interpretation.
   - Implication: backend engine latency/throughput, direct vLLM serving,
     gateway serving, gateway metrics, backend usage, and GPU metrics are kept
     separate. This makes gateway overhead and backend capacity visible instead
     of collapsing all evidence into one benchmark number.

## Canonical Design Contract
Use `001_vllm_gateway_baseline.md` as the canonical source for:

- serving boundary and topology
- public interfaces and request-handling rules
- model/backend config shape
- streaming, observability, and failure policy
- milestone assumptions and expected artifacts

Keep this plan focused on tracer-bullet execution status and verification
history. When the contract changes, update `001_vllm_gateway_baseline.md` first
and reference that change from the relevant slice here.

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
  - `vllm bench latency` saves engine latency output under the milestone experiment folder
  - `vllm bench throughput` saves offline engine throughput output under the milestone experiment folder
  - `vllm bench serve` runs directly against vLLM and saves raw output under the milestone experiment folder
  - `vllm bench serve` runs against the gateway and saves raw output under the milestone experiment folder
  - gateway metrics and Prometheus target snapshots are saved after the gateway serving benchmark
