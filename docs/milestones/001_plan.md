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

6. **Fail-Loud Error And Metrics Contract** - Partial
   - Completed metrics increment:
     - Emit Prometheus chat completion request counts labeled by status, selected backend, routing policy, and error class.
     - Emit Prometheus backend error counts labeled by selected backend, routing policy, error class, timeout class, and backend HTTP status when available.
     - Emit Prometheus stream duration histograms for streaming requests labeled by selected backend, routing policy, stream status, and error class.
     - Emit Prometheus backend-reported token counters for prompt, completion, and total tokens when non-streaming responses include OpenAI-compatible `usage`.
     - Preserved existing gateway behavior for unknown/disabled models, backend HTTP responses, timeout envelopes, and connection failure envelopes.
   - Verified with: `uv run pytest tests/test_config_registry.py tests/test_gateway_chat.py tests/test_gateway_skeleton.py`, `uv run pytest`, and a manual non-streaming request through the gateway showing chat completion and token metrics in `/metrics`.
   - Deferred/skipped for a later Slice 6 increment:
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
   - Added `benchmarks/vllm-gateway-serving.sh` using pinned `vllm bench serve` with OpenAI chat endpoint settings and raw JSON output under `experiments/001_vllm_gateway_baseline/raw/`.
   - Added `benchmarks/README.md` with benchmark wrapper usage, smoke command, and provenance notes.
   - Added `experiments/001_vllm_gateway_baseline/` with `README.md`, `commands.md`, `configs/`, `raw/`, `plots/`, and `report.md`.
   - Documented benchmark wrapper arguments in `experiments/001_vllm_gateway_baseline/commands.md`, including gateway URL, public model alias, tokenizer model, prompt count, request rate, input/output token lengths, result path, and fixed vLLM chat endpoint options.
   - Copied the exact gateway, Compose, Prometheus, vLLM launch, and benchmark wrapper configs used for the saved run into `experiments/001_vllm_gateway_baseline/configs/`.
   - Saved raw benchmark and observability artifacts under `experiments/001_vllm_gateway_baseline/raw/`.
   - Wrote the first benchmark interpretation in `experiments/001_vllm_gateway_baseline/report.md`.
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
     - Verified benchmark command shape with a one-request smoke run: `GATEWAY_BASE_URL=http://127.0.0.1:18000 NUM_PROMPTS=1 REQUEST_RATE=1 RANDOM_INPUT_LEN=16 RANDOM_OUTPUT_LEN=8 RESULT_FILENAME=vllm-gateway-serving-smoke.json ./benchmarks/vllm-gateway-serving.sh`.
     - Saved raw smoke output at `experiments/001_vllm_gateway_baseline/raw/vllm-gateway-serving-smoke.json`.
     - Ran a small non-smoke Compose benchmark: `GATEWAY_BASE_URL=http://127.0.0.1:18000 NUM_PROMPTS=10 REQUEST_RATE=1 RANDOM_INPUT_LEN=128 RANDOM_OUTPUT_LEN=64 RESULT_FILENAME=vllm-gateway-serving-compose-small.json ./benchmarks/vllm-gateway-serving.sh`.
     - Saved `gateway-metrics-after-compose-small.prom` and `prometheus-targets-after-compose-small.json`.
   - Why: every stage must produce runnable/deployable code, a reproducible benchmark command, saved artifacts, and interpretation.
   - Implication: benchmark-observed latency, gateway-observed latency, backend usage, and GPU metrics are kept separate.

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
  - documented vLLM benchmark command runs against the gateway and saves raw output under the milestone experiment folder
