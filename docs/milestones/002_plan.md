# Milestone 2 Routing Policy Comparison Plan

## Summary

Implement Milestone 2 as vertical tracer-bullet slices, not horizontal layer
work. Each slice must produce a narrow end-to-end path through config, registry,
router, gateway integration, observability, deployment/runbooks, benchmarks, and
tests where relevant so progress is demoable and reviewable at every step.

Canonical Milestone 2 serving boundaries, topology assumptions, routing policy
scope, observability, failure policy, benchmark evidence, and expected artifacts
are defined in `002_routing_policy_comparison.md`. This plan tracks execution
status, planned artifacts, verification, dependencies, and acceptance checks
instead of restating the design contract.

Milestone 2 intentionally avoids mock workers. All benchmark and interpretation
paths should use real external vLLM backends. Smaller models such as
`Qwen/Qwen3-0.6B` or `Qwen/Qwen3-1.7B` are acceptable for one-A100 multi-replica
development when `Qwen/Qwen3-8B` replicas are not practical, but the exact model
and topology must be recorded in experiment artifacts.

## Tracer-Bullet Slices

### 1. Real vLLM Replica Topology Runbooks - Implemented; Shared-GPU Startup Validated

- Add or update `deploy/vllm/` docs/scripts for running multiple external vLLM
  OpenAI-compatible workers.
- Cover first-priority topologies:
  - one A100 with multiple smaller-model vLLM replicas where memory allows
  - multiple A100s with one vLLM replica per GPU
- Include later notes for multiple-node replicas without making multi-node a
  first acceptance dependency.
- Document worker IDs, ports, `CUDA_VISIBLE_DEVICES`, served model names, model
  choice, and direct smoke-test commands for each worker.
- Add example backend-worker inventory for
  `experiments/2_routing_policy_comparison/configs/backend-workers.md`.
- Why: routing policy comparison needs real backend replicas before router
  behavior can be interpreted as LLM serving behavior.
- Implication: one-GPU shared-replica results are useful for development but must
  be labeled with shared-GPU contention; multi-A100 results are stronger policy
  evidence.
- Dependencies: none.
- Can parallelize with: slice 2 config design discussion, slice 8 benchmark
  planning.
- Verification:
  - shell syntax checks for added scripts
  - direct `curl /v1/models` against each configured worker
  - direct non-streaming `/v1/chat/completions` smoke against each worker
  - optional direct streaming smoke against each worker

### 2. Backend Set Config And Registry Compatibility - Planned

- Evolve static config from one backend per model to a backend set per model.
- Support single-backend and multi-backend model configs as first-class valid
  operating modes, because some deployments or experiments may truly have only
  one backend target.
- Add fields for model-level routing policy and backend target IDs.
- Keep backend target state config-backed only for static intent, such as enabled
  or disabled; do not encode observed load or health as config truth.
- Update registry facade so resolving a public model returns eligible configured
  backend targets rather than one hardcoded backend URL.
- Add tests for:
  - old or compatibility single-backend config
  - multi-backend config
  - disabled model
  - disabled backend target
  - backend model alias rewriting
- Why: this is the smallest structural change that avoids hardcoding one model to
  one backend URL forever.
- Implication: router policy code can operate over backend sets while existing
  gateway behavior remains testable.
- Dependencies: none.
- Can parallelize with: slice 1 runbooks.
- Verification:
  - `uv run pytest tests/test_config_registry.py`
  - `uv run pytest`

### 3. Router Facade With Static And Round-Robin Policies - Planned

- Add `tokenkaki.router` as a deep module with a small functional facade.
- Implement `static_single_backend` compatibility selection.
- Implement `round_robin` selection over enabled backend targets.
- Keep router state minimal and gateway-owned for now; do not introduce a control
  plane or worker registry service.
- Ensure selected routes still carry public model, backend type, backend base URL,
  backend model, backend ID, and routing policy.
- Add route-decision tests for deterministic selection and no-eligible-backend
  behavior.
- Why: round-robin is the ordinary HTTP load-balancing baseline that later LLM
  policies can beat or fail to beat.
- Implication: the gateway now has an explicit router boundary, but not a broad
  scheduler framework.
- Dependencies: slice 2.
- Can parallelize with: slice 5 health-check design after route target shape is
  stable.
- Verification:
  - `uv run pytest tests/test_router*.py tests/test_config_registry.py`
  - `uv run pytest`

### 4. Gateway Integration For Policy-Selected Backends - Planned

- Replace direct single-route gateway resolution with backend-set resolution plus
  router selection.
- Preserve non-streaming and streaming OpenAI-compatible forwarding behavior.
- Preserve minimal request mutation, including public alias to selected backend
  model rewrite only when needed.
- Ensure selected backend and routing policy labels are emitted for both
  non-streaming and streaming paths.
- Ensure no-eligible-backend returns a clear OpenAI-compatible error envelope and
  fail-loud metrics.
- Add gateway tests for:
  - single-backend compatibility
  - round-robin selected backend labels
  - unknown model
  - no eligible backend
  - non-streaming selected backend forwarding
  - streaming selected backend forwarding
- Why: routing is only meaningful when it is on the real public request path.
- Implication: every later policy can be benchmarked through the same
  `/v1/chat/completions` endpoint used by MS1.
- Dependencies: slices 2 and 3.
- Can parallelize with: slice 8 benchmark wrapper parameterization after endpoint
  behavior is stable.
- Verification:
  - `uv run pytest tests/test_gateway_chat.py tests/test_gateway_models.py tests/test_router*.py`
  - `uv run pytest`
  - local gateway smoke against one real vLLM worker

### 5. Lightweight Active Health And Eligibility - Planned

- Add a lightweight active health check for configured backend targets, using
  `/v1/models` or another vLLM-compatible endpoint where available.
- Exclude configured-disabled and actively-unhealthy backend targets from normal
  router selection.
- Keep health state inside the gateway process; do not introduce service
  discovery, dynamic registration, or a control plane.
- Add health metrics or logs that identify backend ID, backend URL, model, and
  health status.
- Add tests for healthy, unhealthy, disabled, and all-unavailable backend sets.
- Why: routing policies should choose from eligible real workers, not blindly send
  traffic to known-dead URLs.
- Implication: no-eligible-backend becomes an explicit failure mode that can be
  measured instead of hidden behind retries.
- Dependencies: slices 2 and 3.
- Can parallelize with: slice 6 after selected route and backend target data
  structures are stable.
- Verification:
  - focused health/eligibility tests
  - `uv run pytest`
  - manual smoke with one healthy and one intentionally stopped vLLM backend

### 6. Least-Outstanding Policy And Lifecycle Accounting - Planned

- Track gateway-observed outstanding chat completion requests per backend target.
- Increment outstanding count after a backend target is selected.
- Decrement outstanding count after completion or cleanup:
  - non-streaming response success or failure
  - streaming completion
  - streaming client disconnect
  - streaming backend timeout or request error
  - stream setup failure before response bytes are sent
- Implement `least_outstanding` policy using the tracked counts.
- Expose outstanding counts through Prometheus where practical.
- Add tests for non-streaming and streaming decrement behavior, including error
  paths.
- Why: LLM requests are long-lived and uneven; in-flight generation count is a
  more relevant routing signal than arrival distribution alone.
- Implication: streaming lifecycle correctness becomes part of router correctness,
  not just response forwarding.
- Dependencies: slice 4.
- Can parallelize with: slice 7 heuristic design after routing facade exists.
- Verification:
  - focused router/accounting tests
  - gateway streaming tests
  - `uv run pytest`
  - manual mixed request smoke showing outstanding metrics change and return to
    zero after completion

### 7. Context-Length-Aware Policy With Simple Heuristic - Planned

- Implement `context_length_aware` using a simple transparent heuristic, such as
  message character count and message count.
- Do not add tokenizer integration in Milestone 2.
- Document the heuristic in code-facing docs and experiment configs.
- Add metrics or logs for the estimated request size bucket where useful.
- Add tests showing short and long requests are classified consistently and routed
  according to the intended policy behavior.
- Why: even approximate prompt-size awareness demonstrates why LLM routing differs
  from ordinary HTTP request distribution.
- Implication: the policy result must be interpreted as heuristic-based routing,
  not exact token-aware scheduling.
- Dependencies: slices 3 and 4; slice 6 is useful but not strictly required.
- Can parallelize with: slice 8 benchmark mixed-workload design.
- Verification:
  - focused context heuristic tests
  - gateway tests for short/long request selection
  - `uv run pytest`

### 8. Routing Benchmark Commands And Mixed Workload Path - Planned

- Extend the existing serving benchmark path for policy-specific runs where
  possible.
- Add config or environment switches for policy selection and experiment output
  under `experiments/2_routing_policy_comparison/`.
- Keep `vllm bench serve` as the continuity path for comparable serving metrics.
- Add a small custom benchmark driver only if `vllm bench serve` cannot express
  the needed mixed short/long workload.
- Save raw JSON, stdout/stderr logs, gateway metrics snapshots, and Prometheus
  target snapshots for each policy run.
- Avoid Locust and GenAI-Perf unless the mixed workload cannot be adequately
  represented with the simpler path.
- Why: policy comparison needs repeatable workloads, not manual curl evidence.
- Implication: benchmark-observed latency/TTFT/TPOT and gateway-observed routing
  metrics remain separate evidence streams.
- Dependencies: slice 4 for gateway policy path; slices 6 and 7 for full policy
  comparison.
- Can parallelize with: slice 1 runbooks and slice 7 heuristic design.
- Verification:
  - tiny benchmark smoke with `NUM_PROMPTS=1` or equivalent
  - policy-specific benchmark command writes artifacts to
    `experiments/2_routing_policy_comparison/`
  - metrics snapshot includes selected backend and routing policy labels

### 9. Policy Comparison Experiment And Writeup Evidence - Planned

- Run the evidence ladder from `002_routing_policy_comparison.md`:
  1. direct backend smoke checks
  2. single-backend gateway compatibility benchmark
  3. multi-backend gateway smoke
  4. round-robin benchmark
  5. least-outstanding benchmark
  6. context-length-aware benchmark
  7. mixed-workload comparison
- Prefer multi-A100 real-worker evidence for the main interpretation if available.
- If using one A100 with multiple smaller-model replicas, label shared-GPU
  contention clearly and avoid overgeneralizing results.
- Save artifacts under `experiments/2_routing_policy_comparison/`.
- Produce a writeup-ready interpretation comparing tail latency, TTFT, TPOT,
  throughput, worker balance, queue/outstanding behavior, errors, and topology
  limitations.
- Why: Milestone 2 is only complete when policy behavior is measured and
  interpreted, not merely implemented.
- Implication: the result becomes the baseline for later batching, Kubernetes,
  multi-node, and cache-aware routing milestones.
- Dependencies: slices 1 through 8.
- Can parallelize with: documentation polish after initial benchmark results are
  saved.
- Verification:
  - saved real-backend benchmark artifacts exist under
    `experiments/2_routing_policy_comparison/`
  - gateway metrics snapshots include selected backend, routing policy, errors,
    and outstanding/request-balance evidence where available
  - writeup or experiment report references exact commands, topology, model,
    backend versions, hardware, and network path

## Dependency Summary

```text
1. vLLM replica runbooks ───────────────┐
                                       ├── 8. benchmark commands ─── 9. experiment/writeup
2. backend-set config ── 3. router ── 4. gateway integration ───────┘
                         │             │
                         │             ├── 6. least-outstanding
                         │             └── 5. health/eligibility
                         └─────────────── 7. context heuristic
```

Parallelizable early work:

- Slice 1 runbooks and slice 2 backend-set config can start independently.
- Slice 8 benchmark planning can start once the desired experiment layout is
  agreed, but executable policy benchmarks depend on gateway integration.
- Slice 5 health and slice 6 least-outstanding can proceed in parallel after the
  route target shape is stable, as long as their write sets stay separate.

## Test Plan

- Unit tests for config loading, backend-set parsing, registry alias resolution,
  disabled models, disabled backend targets, and backward-compatible
  single-backend config.
- Router tests for static single backend, round-robin, least-outstanding,
  context-length-aware selection, tie-breaking, and no eligible backends.
- Gateway tests for `/v1/models`, unknown model rejection, no-eligible-backend
  failure, non-streaming selected-backend forwarding, streaming selected-backend
  forwarding, backend timeout, backend connection failure, and selected-backend
  metrics.
- Lifecycle tests for outstanding-request decrement on non-streaming success,
  non-streaming failure, streaming completion, streaming cancellation, and stream
  setup failure.
- Health tests for reachable, unreachable, disabled, and mixed backend sets.
- Acceptance checks:
  - `uv run pytest`
  - local gateway startup with `uv run uvicorn`
  - direct smoke tests against each external vLLM worker
  - gateway single-backend compatibility smoke
  - gateway multi-backend round-robin smoke showing traffic to multiple backend
    IDs
  - least-outstanding smoke showing outstanding counts change and return to zero
  - context-length-aware smoke using short and long requests
  - policy-specific benchmark smoke writes output under
    `experiments/2_routing_policy_comparison/`
  - saved gateway metrics and Prometheus target snapshots after benchmark runs

## Milestone Acceptance

Milestone 2 is complete when:

- the gateway can route one public model alias across multiple configured real
  vLLM backend targets
- `static_single_backend`, `round_robin`, `least_outstanding`, and
  `context_length_aware` policies are implemented and tested
- no mock-worker benchmark or interpretation path is used
- backend health/eligibility and no-eligible-backend failure behavior are visible
- non-streaming and streaming request lifecycles preserve accurate selected
  backend, routing policy, errors, and outstanding-request accounting
- at least one real-backend routing topology is validated, with one-A100 and
  multi-A100 layouts planned and documented
- policy comparison benchmarks are reproducible and saved under
  `experiments/2_routing_policy_comparison/`
- the interpretation explains latency, TTFT, TPOT, throughput, worker balance,
  queue/outstanding behavior, and topology limitations
