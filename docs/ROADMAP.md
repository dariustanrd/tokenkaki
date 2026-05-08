# Roadmap

The roadmap is staged around learning objectives, real backends, runnable
artifacts, benchmark evidence, saved results, and writeups.

## Milestone 1: Measured vLLM Gateway Baseline

Learning objective: understand the request path from OpenAI-compatible API
gateway to a real vLLM backend and measure baseline serving behavior.

Outputs:

- runnable FastAPI gateway
- real vLLM backend integration
- `/v1/models` and `/v1/chat/completions`
- basic streaming support if feasible in the first pass
- Prometheus metrics for request count, errors, latency, selected backend, and
  token counts where available
- reproducible benchmark command
- saved benchmark results
- writeup covering setup, baseline TTFT/TPOT/latency/throughput, and
  interpretation

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
