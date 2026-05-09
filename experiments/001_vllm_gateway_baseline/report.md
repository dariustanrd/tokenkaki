# Report

## Compose Small Benchmark

This run validates the Milestone 1 gateway path through Docker Compose:

```text
vLLM benchmark client
-> tokenkaki gateway on http://127.0.0.1:18000
-> external vLLM on the Docker-reachable host address
```

The external vLLM server was started with:

```bash
VLLM_HOST=172.17.0.1 ./deploy/vllm/run-openai-server.sh
```

The benchmark command was:

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=10 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=128 \
RANDOM_OUTPUT_LEN=64 \
RESULT_FILENAME=vllm-gateway-serving-compose-small.json \
./benchmarks/vllm-gateway-serving.sh
```

Raw benchmark output:

```text
experiments/001_vllm_gateway_baseline/raw/vllm-gateway-serving-compose-small.json
```

Captured observability snapshots:

```text
experiments/001_vllm_gateway_baseline/raw/gateway-metrics-after-compose-small.prom
experiments/001_vllm_gateway_baseline/raw/prometheus-targets-after-compose-small.json
```

## Result

The benchmark completed 10 successful requests with fixed random prompt and
output lengths:

| Metric | Value |
| --- | ---: |
| Requests | 10 |
| Request rate target | 1 req/s |
| Benchmark duration | 9.74 s |
| Request throughput | 1.03 req/s |
| Input tokens | 1,280 |
| Generated tokens | 616 |
| Output throughput | 63.27 tok/s |
| Total token throughput | 194.73 tok/s |
| Mean TTFT | 42.93 ms |
| P99 TTFT | 63.89 ms |
| Mean TPOT | 4.58 ms |
| P99 TPOT | 4.91 ms |
| Mean ITL | 4.50 ms |
| P99 ITL | 7.55 ms |

## Interpretation

This is a real gateway-to-vLLM serving result, not a mock result. It is still a
small validation run, not a publishable performance claim. Its main value is
that the full Slice 7 path is now reproducible: Compose deployment, Prometheus
scraping, benchmark command, raw artifact, and interpretation.

The benchmark client reports TTFT, TPOT, ITL, and token throughput. Those are
benchmark-observed metrics and should remain separate from gateway-observed
latency in `/metrics`.

The Prometheus target snapshot showed the gateway scrape target healthy. The
gateway metrics snapshot also preserved earlier failed backend-connection
attempts from the loopback-only vLLM test, which is useful provenance: the
metrics distinguish successful gateway traffic from backend connection failures.

Current gateway token counters only parse `usage` from non-streaming JSON
responses. The vLLM benchmark reports TTFT/ITL, which implies streaming-style
benchmark behavior, so the benchmark output is the source of truth for generated
token counts in this run.

The benchmark process printed vLLM's CUDA device visibility warning because the
benchmark client imports vLLM locally. That does not mean a second vLLM server
was started. The server path remains the already-running external vLLM process
reached through the gateway.
