# Roadmap

The roadmap is staged around learning objectives, real backends, runnable
artifacts, benchmark evidence, saved results, and writeups.

Canonical source note: this document owns phase model targets and milestone
sequence. Use the README for navigation, [`VISION.md`](VISION.md) for project
purpose, and [`ARCHITECTURE.md`](ARCHITECTURE.md) for repository, serving, and
runtime boundaries.

Real backends are the default for portfolio stages. Mock workers are allowed
only as isolated test and load-generation utilities, especially when validating
gateway behavior under many simulated clients. Synthetic results must be labeled
clearly and must not be presented as real serving results.

Future expansion note: the roadmap may later grow into a heterogeneous
enterprise inference fabric: an OpenAI-compatible internal API backed by a
control plane that understands GPU servers, Kubernetes clusters, workstation
capacity, runtime variants, network locality, and agent workload intent. That is
an end-state direction, not an early milestone rewrite. The original milestone
sequence remains the serving-knowledge path; each stage should collect signals
that would make the future platform credible rather than building a scheduler
before the serving behavior is understood.

## Phase Model Targets

Model targets are phase-dependent. Verify exact model availability, serving
support, license terms, memory needs, and benchmark tooling before starting a
phase, especially for multimodal, FP8, MoE, and disaggregated serving work.

| Phase | Model | Hardware Target | Learning Intention | Demo Purpose |
| --- | --- | --- | --- | --- |
| 0. Dev / CI Model | `Qwen/Qwen3-0.6B` or `Qwen/Qwen3-1.7B` | Local machine or 1 small GPU | Test API compatibility, tokenizer behavior, request lifecycle, streaming, scheduler correctness, and CI workflows cheaply. | Internal dev model for fast iteration. Not the main public demo. |
| 1. Primary Public Demo | `Qwen/Qwen3-8B` | 1x A100 40GB | Learn single-GPU production serving with vLLM/SGLang, streaming, batching, metrics, and thinking vs non-thinking modes. | Main public endpoint. Show fast chat mode vs thinking mode with TTFT, TPOT, output tokens, and cost differences. |
| 2. Industry Baseline | `meta-llama/Llama-3.1-8B-Instruct` | 1x A100 40GB | Learn model registry, model routing, benchmark comparison, and long-context serving behavior. | Credibility baseline: compare Qwen3-8B vs Llama 3.1 8B under the same gateway, GPU, and benchmark. |
| 3. Reasoning Workload | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | 1x A100 40GB | Learn how reasoning models stress inference through long generations, slower decode, higher token usage, and variable latency. | Reasoning benchmark mode. Show why reasoning workloads have different latency and cost profiles. |
| 4. Multimodal Demo | `google/gemma-3-12b-it` | 1x A100 40GB, possibly quantized depending on serving config | Learn multimodal request handling, image upload pipeline, image-to-text inference, and multimodal latency measurement. | Public image-to-text demo with latency, throughput, and cost metrics. |
| 5. Larger Single-Node Model | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | 1x 48GB/80GB GPU, or A100 40GB with quantization if practical | Learn larger model memory planning, quantized serving, batch-size limits, context-length limits, and cost/performance tradeoffs. | Pro-tier endpoint for better quality, agent/tool-use demos, and serving a larger model cost-effectively. |
| 6. Single-Node Multi-GPU | `meta-llama/Llama-3.1-70B-Instruct` or another 70B/72B-class dense model | 4-8x A100/H100 on one node | Learn tensor parallelism, NCCL, GPU topology, per-GPU memory balance, interconnect bottlenecks, and distributed serving within one machine. | Prove multi-GPU serving understanding beyond single-GPU inference. |
| 7. True Multi-Node Model Parallelism | Same 70B/72B dense model | 2+ GPU nodes, ideally 8-16 GPUs total with fast networking | Learn Ray or distributed runtime setup, multi-node tensor/pipeline parallelism, shared model weights, network bottlenecks, failure modes, and cross-node communication. | First true multi-node serving milestone. Demonstrate one model split across machines. |
| 8. Advanced Sparse / MoE Model | `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8` or `Qwen/Qwen3-Next-80B-A3B-Thinking-FP8` | Multi-GPU or multi-node FP8-capable setup | Learn sparse activation economics, FP8 serving, MoE-style routing behavior, long-context serving, and advanced capacity planning. | Advanced infra milestone: show efficient serving of a large total-parameter model with sparse activation. |
| 9. Disaggregated Serving Capstone | 70B/72B dense model or Qwen3-Next MoE model | Kubernetes cluster with multiple GPU nodes, ideally RDMA-capable networking | Learn prefill/decode disaggregation, separate GPU pools, KV-cache transfer, prefix-cache-aware routing, autoscaling, SLOs, and production-style cluster operations. | Final neocloud-style demo with separate prefill/decode workers, intelligent routing, and cluster-level metrics. |

## Milestone 1: Measured vLLM Gateway Baseline

Learning objective: understand the request path from OpenAI-compatible API
gateway to a real vLLM backend and measure baseline serving behavior.

Detailed design:
[`docs/milestones/001_vllm_gateway_baseline.md`](milestones/001_vllm_gateway_baseline.md).

Repository and runtime boundaries:
[`docs/ARCHITECTURE.md`](ARCHITECTURE.md).

Deployment target:

- Gateway development, vLLM, Prometheus, benchmark tooling, and Milestone 1
  experiment artifacts run directly on the NVIDIA GPU machine by default.
- Docker Compose should support gateway and Prometheus on this machine while
  vLLM remains a separately managed external process.
- Grafana is optional in Milestone 1 and becomes required once routing or
  GPU/system correlation is being analyzed.
- vLLM runs as a real GPU-backed service, either on this GPU host or on a rented
  single-GPU node for reproduction.
- The gateway connects to an external vLLM server over its OpenAI-compatible
  HTTP endpoint.
- The gateway uses a small static config-backed registry for public model
  aliases, backend URLs, and backend model names.
- Kubernetes is intentionally deferred until the baseline endpoint, metrics, and
  benchmarks are working.
- Auth and quotas are deferred until there is a concrete public-demo need.
- Generation retries and failover are deferred until multiple-backend routing
  work.

Outputs:

- minimal runnable FastAPI gateway skeleton before deeper endpoint work
- runnable FastAPI gateway
- real vLLM backend integration, using Phase 0 or Phase 1 model targets
- Docker Compose deployment for gateway, Prometheus scraping, and benchmark
  support, with configurable vLLM backend URL
- local GPU setup/run artifacts for vLLM under `deploy/vllm/`
- `/v1/models` and `/v1/chat/completions`
- streaming and non-streaming chat completion support
- Prometheus metrics for request count, errors, latency, selected backend, and
  token counts where available
- reproducible benchmark command
- saved benchmark results
- first blog post in the `Behind the API` series covering motivation, project
  scope, high-level architecture, phase plan, and what the initial baseline will
  measure

## Milestone 2: Routing Policy Comparison

Learning objective: understand why LLM routing is not the same as ordinary HTTP
load balancing.

Detailed design:
[`docs/milestones/002_routing_policy_comparison.md`](milestones/002_routing_policy_comparison.md).

Execution plan:
[`docs/milestones/002_plan.md`](milestones/002_plan.md).

Future-fabric intuition: this is the first step toward fleet routing. Keep the
implementation focused on real backend replicas and simple policies, but avoid
hardcoding assumptions that a model has only one backend URL forever.

Outputs:

- multiple real vLLM workers where infrastructure allows
- isolated mock-worker benchmark path only for controlled multi-client tests
- routing policies such as round-robin, least-outstanding, and
  context-length-aware routing
- mixed workload benchmark
- saved latency, TTFT, TPOT, throughput, queue, and worker-balance results
- writeup comparing policies and explaining tail-latency behavior

## Milestone 3: Batching And Serving Tuning

Learning objective: measure how vLLM serving parameters and workload shape
affect latency and throughput, including the impact of supported vLLM attention
backends such as FlashAttention, FlashInfer, Triton attention, and FlexAttention.

Future-fabric intuition: this stage explains why token profiles matter. A later
agent-aware scheduler can only be meaningful if earlier benchmarks show how
short prompts, long prompts, long generations, concurrency, and queueing change
TTFT, TPOT, throughput, and cost.

Attention-backend experiments belong in this milestone because they compare
runtime/kernel behavior under the same model, GPU, and workload rather than
routing policy or model-format changes. Save these results under a Milestone 3
experiment folder such as `experiments/3_vllm_attention_backends_Qwen3-8B/`,
with one subfolder per backend and a shared environment/configuration record so
the comparison is reproducible.

Outputs:

- batching and concurrency sweep scripts
- attention-backend comparison across supported vLLM kernels where available
- workloads covering short, medium, long-context, and mixed prompts
- saved backend-specific serving configs, compatibility notes, and environment
  artifacts
- result tables and plots
- writeup explaining throughput/latency tradeoffs and saturation behavior

## Milestone 4: Quantization Comparison

Learning objective: compare memory, latency, throughput, and quality tradeoffs
across model formats.

Future-fabric intuition: heterogeneous fleets need model/runtime placement
judgment. Quantization and model variants teach when weaker or smaller hardware
can serve useful traffic, and what quality or latency tradeoff that introduces.

Outputs:

- at least one baseline model and one quantized variant
- memory and throughput measurements
- latency and token-rate comparisons
- cost estimate per successful request or token batch
- writeup explaining when quantization helps and what it costs

## Milestone 5: Kubernetes Deployment

Learning objective: move from a local service layout to a realistic orchestrated
serving environment.

Future-fabric intuition: Kubernetes is one managed substrate for the later
platform, not the whole platform. This milestone should teach service discovery,
GPU scheduling, rollout, scrape configuration, and cluster networking without
assuming all future enterprise capacity will live in Kubernetes.

Outputs:

- Kubernetes deployment for gateway and backend path
- GPU scheduling notes using the NVIDIA device plugin
- Prometheus/Grafana integration
- reproducible deployment and teardown instructions
- benchmark comparison against the non-Kubernetes baseline
- writeup explaining operational and measurement differences

## Milestone 6: Multi-GPU And Topology Experiments

Learning objective: understand what changes when one serving setup spans
multiple GPUs.

Future-fabric intuition: this separates routing across replicas from splitting
one model across GPUs. A future control plane needs to know when a workload can
run on one warm replica versus when model execution itself requires topology,
NCCL, and interconnect-aware placement.

Outputs:

- tensor-parallel vLLM experiment where hardware allows
- `nvidia-smi topo -m` artifact
- NCCL or equivalent communication test artifact
- benchmark comparison against single-GPU serving
- writeup covering topology, communication overhead, and scaling limits

## Milestone 7: Multi-Node Experiment

Learning objective: measure the operational and networking issues that appear
when serving crosses node boundaries.

Future-fabric intuition: this is the evidence base for network-aware routing.
It should record when a remote idle GPU is worse than a local busier backend,
and when cross-node or cross-site placement is acceptable for batch or
non-latency-sensitive work.

Outputs:

- short-lived multi-node setup
- network benchmark such as `iperf3`
- distributed runtime notes if Ray or Kubernetes is used
- failure and restart observations
- saved costs and teardown confirmation
- writeup explaining what changed from single-node serving

## Milestone 8: Cache-Aware Routing

Learning objective: treat prefix and KV cache locality as scheduling inputs.

Future-fabric intuition: this is where inference routing becomes clearly
different from ordinary service load balancing. The best backend may be the one
with useful context/cache locality, not simply the least-loaded one.

Outputs:

- prefix hash extraction
- worker-local cache metadata
- cache-aware routing policy
- repeated-prefix workload
- comparison against non-cache-aware routing
- writeup explaining cache locality, TTFT impact, and limitations

## Milestone 9: Disaggregated Prefill / Decode Study

Learning objective: understand the resource split between prefill and decode
and the cost of moving state between them.

Future-fabric intuition: this is the advanced serving capstone before any
enterprise-fleet expansion. It combines workload shape, topology, cache state,
separate queues, and network cost into one scheduling problem.

Outputs:

- simulation or deployment comparison depending on available infrastructure
- prefill/decode workload model
- KV transfer or handoff cost model
- benchmark against colocated serving
- writeup mapping the experiment to production-style disaggregated serving

## Future Expansion: Heterogeneous Fleet And Agent-Aware Scheduling

This expansion should start only after the original roadmap has produced enough
serving evidence to make scheduler decisions defensible. It should not change
Milestone 1, and it should not pull worker agents or fleet control-plane work
into early routing and tuning stages.

Likely future milestones:

- fleet registry and worker-agent prototype for node capabilities, warm models,
  runtime type, reliability tier, queue/load, and owner policy
- network-aware routing across local, Tailscale, private WAN/VPC, and
  Kubernetes service paths
- runtime diversity experiments such as vLLM for production NVIDIA servers and
  llama.cpp or other runtimes for weaker or opportunistic nodes
- agent-job API for goal, budget, deadline, quality, urgency, and estimated
  token profile once workload-shape benchmarks exist
- policy and accounting work for team quotas, priority, and safe use of
  opportunistic workstation capacity
