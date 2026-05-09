# Updated Plan: TokenKaki Inference Railway Demo

## Summary
The current repo already has the Milestone 1 serving baseline: FastAPI gateway, `/v1/models`, streaming and non-streaming `/v1/chat/completions`, external vLLM forwarding, Prometheus metrics, Compose deployment, benchmark wrapper, and saved experiment artifacts. Tests pass with `uv run pytest`: 19 passed.

So the railway demo should start from the existing real gateway path, not rebuild it. The next work is a demo layer that records request traces, turns each trace into station facts, and drives a shared map plus phone UI.

Out of scope remains: Adaption, Unsloth, LoRA, fine-tuning, Kubernetes, auth/quotas, and deeper scheduler internals.

## Key Changes From Previous Plan
- **Remove completed work from future scope:** chat forwarding, streaming proxy, vLLM backend client, Compose, Prometheus baseline, and first benchmark artifact already exist.
- **Keep `tokenkaki.gateway` as the only backend runtime service:** demo APIs should live inside the gateway for now.
- **Add a separate React demo app:** acceptable for hackathon UI, but it should call the gateway and not become a new backend service.
- **Use existing metrics as backing evidence:** current gateway metrics cover request count, latency, selected backend, errors, stream duration, and non-streaming token usage.
- **Add trace storage because the UI needs replay:** live train motion and slowed learning mode both require per-run timestamped events.

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
   - Status: Next.
   - Dependency: TB1.
   - Generate facts for Gateway, Queue, Prefill, Decode, and Metrics from the same trace.
   - Label estimates clearly: prefill is inferred from TTFT/first chunk timing, decode from stream progression/output timing.
   - Demoable result: `/demo/runs/{id}/stations/{station}` returns measured facts for the selected station.

3. **TB3: Grounded Station Explanation**
   - Dependency: TB2.
   - Add a demo endpoint that asks the base model to explain one station using capped session history plus station facts.
   - Place measured facts last in the prompt and instruct the model not to invent missing metrics.
   - Demoable result: phone UI can ask “what happened here?” and receive a short trace-grounded answer.

4. **TB4: Live Train Event Stream**
   - Dependency: TB1; can parallelize with TB3 after trace schema is fixed.
   - Add SSE or WebSocket events for train movement: Gateway → Queue → Prefill → Decode → Metrics/Done.
   - Live mode uses real event timing; learning mode replays the saved trace at slowed speed.
   - Demoable result: a simple client can watch a train move in real time, then replay it slowly.

5. **TB5: React Railway UI**
   - Dependency: TB4 for live map; TB2 for station cards.
   - Shared display shows the whole Mini Metro / Overcooked-style map, active trains, and all user avatars.
   - Phone UI shows the user’s avatar, nearby stations, station facts, and station conversation.
   - Demoable result: one user submits a prompt, the shared map shows a live train, and the phone inspects all five stations.

6. **TB6: Demo Artifact And Smoke Benchmark**
   - Dependency: TB1 and TB5; can parallelize after backend trace format is stable.
   - Save one demo run artifact under a new experiment folder with trace JSON, command, config, and short interpretation.
   - Reuse `benchmarks/vllm-gateway-serving.sh` for serving evidence; add a small demo smoke command if needed.
   - Demoable result: live demo is backed by saved evidence, not only UI animation.

## Test Plan
- Keep baseline: `uv run pytest`.
- Completed TB1 tests for trace ticket creation, active train count, first chunk timing, and unknown run lookup.
- Add backend tests for station fact generation and grounded prompt construction.
- Add streaming mock tests using the existing HTTPX mock backend pattern.
- Add frontend smoke coverage for prompt submit, live train render, station inspection, and explanation display.
- Acceptance target: one real model request through TokenKaki creates a train, records a trace, supports slowed replay, and explains all five station lenses.

## Assumptions
- Primary demo backend remains external vLLM with `qwen3-8b` currently configured.
- Active train count is measured gateway in-flight request count, not a claim about vLLM’s internal queue.
- Prefill/decode station timings are gateway-derived approximations unless backend metrics are later integrated.
- Public demo hardening such as auth, quotas, and rate limits is deferred unless exposure beyond a controlled hackathon room becomes required.
