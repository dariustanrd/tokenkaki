# Roadmap

The roadmap is staged around learning objectives, real backends, runnable
artifacts, benchmark evidence, saved results, and writeups.

Real backends are the default for portfolio stages. Mock workers are allowed
only as isolated test and load-generation utilities, especially when validating
gateway behavior under many simulated clients.

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

Repository foundation:

- `uv` for Python package and dependency management
- Python-first package under `src/tokenkaki/`
- one initial runtime service: `tokenkaki.gateway`
- deep modules for gateway, router, backends, registry, observability, auth, and
  config
- benchmark tooling under `benchmarks/`
- saved Milestone 1 artifacts under `experiments/001_vllm_gateway_baseline/`
- deployment artifacts under `deploy/compose/`, with Kubernetes-family manifests
  deferred until a kind, k3s, k3d, or cloud Kubernetes milestone starts

Deployment target:

- Gateway, Prometheus, and benchmark tooling run locally via Docker Compose.
- Grafana is optional in Milestone 1 and becomes required once routing or
  GPU/system correlation is being analyzed.
- vLLM runs as a real GPU-backed service, either on the same GPU host or on a
  rented single-GPU node.
- The gateway connects to vLLM over its OpenAI-compatible HTTP endpoint.
- Kubernetes is intentionally deferred until the baseline endpoint, metrics, and
  benchmarks are working.

Outputs:

- minimal runnable FastAPI gateway skeleton before deeper endpoint work
- runnable FastAPI gateway
- real vLLM backend integration, using Phase 0 or Phase 1 model targets
- Docker Compose deployment for gateway, Prometheus scraping, and benchmark
  support, with configurable remote/local vLLM backend URL
- `/v1/models` and `/v1/chat/completions`
- basic streaming support if feasible in the first pass
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
affect latency and throughput.

Outputs:

- batching and concurrency sweep scripts
- workloads covering short, medium, long-context, and mixed prompts
- result tables and plots
- writeup explaining throughput/latency tradeoffs and saturation behavior

## Milestone 4: Quantization Comparison

Learning objective: compare memory, latency, throughput, and quality tradeoffs
across model formats.

Outputs:

- at least one baseline model and one quantized variant
- memory and throughput measurements
- latency and token-rate comparisons
- cost estimate per successful request or token batch
- writeup explaining when quantization helps and what it costs

## Milestone 5: Kubernetes Deployment

Learning objective: move from a local service layout to a realistic orchestrated
serving environment.

Outputs:

- Kubernetes deployment for gateway and worker path
- GPU scheduling notes using the NVIDIA device plugin
- Prometheus/Grafana integration
- reproducible deployment and teardown instructions
- benchmark comparison against the non-Kubernetes baseline
- writeup explaining operational and measurement differences

## Milestone 6: Multi-GPU And Topology Experiments

Learning objective: understand what changes when one serving setup spans
multiple GPUs.

Outputs:

- tensor-parallel vLLM experiment where hardware allows
- `nvidia-smi topo -m` artifact
- NCCL or equivalent communication test artifact
- benchmark comparison against single-GPU serving
- writeup covering topology, communication overhead, and scaling limits

## Milestone 7: Multi-Node Experiment

Learning objective: measure the operational and networking issues that appear
when serving crosses node boundaries.

Outputs:

- short-lived multi-node setup
- network benchmark such as `iperf3`
- distributed runtime notes if Ray or Kubernetes is used
- failure and restart observations
- saved costs and teardown confirmation
- writeup explaining what changed from single-node serving

## Milestone 8: Cache-Aware Routing

Learning objective: treat prefix and KV cache locality as scheduling inputs.

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

Outputs:

- simulation or deployment comparison depending on available infrastructure
- prefill/decode workload model
- KV transfer or handoff cost model
- benchmark against colocated serving
- writeup mapping the experiment to production-style disaggregated serving
