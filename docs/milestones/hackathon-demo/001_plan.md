# Updated Plan: TokenKaki Inference Railway Demo

## Summary
The current repo already has the Milestone 1 serving baseline: FastAPI gateway, `/v1/models`, streaming and non-streaming `/v1/chat/completions`, external vLLM forwarding, Prometheus metrics, Compose deployment, benchmark wrapper, and saved experiment artifacts. Tests pass with `uv run pytest`: 19 passed.

So the railway demo should start from the existing real gateway path, not rebuild it. The next work is a demo layer that records request traces, turns each trace into station facts, enriches stations with benchmark reference evidence, and drives a shared map plus phone UI.

Out of scope remains: Adaption, Unsloth, LoRA, fine-tuning, Kubernetes, auth/quotas, and deeper scheduler internals.

## Key Changes From Previous Plan
- **Remove completed work from future scope:** chat forwarding, streaming proxy, vLLM backend client, Compose, Prometheus baseline, and first benchmark artifact already exist.
- **Keep `tokenkaki.gateway` as the only backend runtime service:** demo APIs should live inside the gateway for now.
- **Add a separate React demo app:** acceptable for hackathon UI, but it should call the gateway and not become a new backend service.
- **Use existing metrics as backing evidence:** current gateway metrics cover request count, latency, selected backend, errors, stream duration, and non-streaming token usage.
- **Add trace storage because the UI needs replay:** live train motion and slowed learning mode both require per-run timestamped events.
- **Split live trace facts from benchmark evidence:** per-user station cards should show the user’s live gateway-observed trace, while benchmark summaries provide reference context such as TTFT, TPOT/ITL, throughput, latency percentiles, and success rate from reproducible artifacts.

## Tracer-Bullet Slices
1. **TB1: Trace Ticket For One Real Request**
   - Status: Completed.
   - Dependency: existing Milestone 1 gateway.
   - Added a demo trace path around `/v1/chat/completions` without changing OpenAI compatibility.
   - Captures `request_id`, optional session/user IDs from `x-tokenkaki-session-id` and `x-tokenkaki-user-id`, public model, backend model, selected backend, routing policy, stream mode, first chunk timing for streaming requests, completion timing, status code, error class, and active in-flight request count at start.
   - Added `GET /demo/runs/{request_id}` to fetch the saved trace ticket.
   - Current trace storage is in-memory and process-local, intentionally scoped for the hackathon demo.
   - Completed artifacts: `tokenkaki.demo.TraceStore`, gateway trace wiring, request ID response headers for chat completions, and focused trace tests.
   - Verified with: `uv run pytest`.
   - Why: the railway UI needs a saved “journey ticket” for live train movement and slowed learning replay.
   - Implication: this is suitable for one gateway process; multi-replica or restart-surviving traces would need a later external store.

2. **TB2: Five Station Fact Views**
   - Status: done
   - Dependency: TB1.
   - Generates facts for Gateway, Queue, Prefill, Decode, and Metrics from the same trace.
   - Labels each station with `measurement_basis`: `measured`, `gateway_observed`, or `gateway_inferred`.
   - Adds streamed SSE chunk count so Decode has a concrete gateway-observed signal before token-level decode metrics are added later.
   - Adds `GET /demo/runs/{request_id}/stations/{station}` for station inspection.
   - Demoable result: `/demo/runs/{id}/stations/{station}` returns measured or labeled-inferred facts for the selected station.

3. **TB3: Grounded Station Explanation**
   - Status: Implemented in working tree; pending review/commit.
   - Dependency: TB2.
   - Added a demo endpoint that asks the configured base model to explain one station using capped session history plus station facts.
   - Places measured facts and benchmark references in the final user message and instructs the model not to invent missing metrics.
   - Adds `POST /demo/runs/{request_id}/stations/{station}/explain`.
   - Demoable result: phone UI can ask “what happened here?” and receive a short trace-grounded answer.

4. **TB4: Benchmark Reference Layer**
   - Status: Implemented in working tree; pending review/commit.
   - Dependency: TB2; can parallelize with TB3.
   - Parses saved `vllm bench serve` JSON artifacts from `experiments/001_vllm_gateway_baseline/raw/`.
   - Exposes `GET /demo/benchmarks/latest` for benchmark summary data.
   - Attaches benchmark summaries to station facts as `reference_metrics`, never as the user’s live trace metrics.
   - Station mapping:
     - Prefill: benchmark TTFT distribution.
     - Decode: benchmark TPOT/ITL and output throughput.
     - Metrics: request throughput, total latency percentiles, success/error counts.
     - Queue/Gateway: optional gateway benchmark metadata and workload settings.
   - Demoable result: a station card can show “your live first chunk: X ms” beside “benchmark mean TTFT: Y ms” with clear provenance labels.
   - Why: this makes the demo evidence-backed without pretending benchmark statistics belong to one phone user’s request.
   - Implication: benchmark integration improves credibility but adds artifact parsing and provenance UI; live per-user traces remain gateway-observed.

5. **TB5: Live Train Event Stream**
   - Dependency: TB1; can parallelize with TB3 after trace schema is fixed.
   - Add SSE or WebSocket events for train movement: Gateway → Queue → Prefill → Decode → Metrics/Done.
   - Live mode uses real event timing; learning mode replays the saved trace at slowed speed.
   - Demoable result: a simple client can watch a train move in real time, then replay it slowly.

6. **TB6: React Railway UI**
   - Dependency: TB5 for live map; TB2 for station cards; TB4 for benchmark reference panels.
   - Shared display shows the whole Mini Metro / Overcooked-style map, active trains, and all user avatars.
   - Phone UI shows the user’s avatar, nearby stations, station facts, and station conversation.
   - Demoable result: one user submits a prompt, the shared map shows a live train, and the phone inspects all five stations.

7. **TB7: Demo Artifact And Smoke Benchmark**
   - Dependency: TB1 and TB6; can parallelize after backend trace format is stable.
   - Save one demo run artifact under a new experiment folder with trace JSON, command, config, and short interpretation.
   - Reuse `benchmarks/vllm-gateway-serving.sh` for serving evidence; add a small demo smoke command if needed.
   - Demoable result: live demo is backed by saved evidence, not only UI animation.

## Test Plan
- Keep baseline: `uv run pytest`.
- Completed TB1 tests for trace ticket creation, active train count, first chunk timing, and unknown run lookup.
- Completed TB2 tests for station fact generation, measurement labels, streamed chunk count, and unknown station lookup.
- Completed TB3 tests for grounded station explanation prompt construction through the gateway endpoint.
- Completed TB4 parser tests using a minimal saved `vllm bench serve` fixture and station `reference_metrics` provenance checks.
- Add streaming mock tests using the existing HTTPX mock backend pattern.
- Add frontend smoke coverage for prompt submit, live train render, station inspection, and explanation display.
- Acceptance target: one real model request through TokenKaki creates a train, records a trace, supports slowed replay, and explains all five station lenses.

## Assumptions
- Primary demo backend remains external vLLM with `qwen3-8b` currently configured.
- Active train count is measured gateway in-flight request count, not a claim about vLLM’s internal queue.
- Prefill/decode station timings are gateway-derived approximations unless backend metrics are later integrated.
- Benchmark metrics are reference evidence for workload behavior, not exact per-user live trace facts.
- UI copy must label benchmark-observed latency, gateway-observed latency, backend-reported usage, and inferred station timing separately.
- Public demo hardening such as auth, quotas, and rate limits is deferred unless exposure beyond a controlled hackathon room becomes required.
