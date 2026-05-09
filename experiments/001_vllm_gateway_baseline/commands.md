# Commands

Record exact commands for each saved Milestone 1 run here.

## Benchmark Wrapper Arguments

`./benchmarks/vllm-gateway-serving.sh` is configured with environment
variables. The wrapper uses the pinned vLLM runtime in `deploy/vllm/` and calls
`vllm bench serve` against the gateway OpenAI chat endpoint.

| Variable | Default | Meaning |
| --- | --- | --- |
| `GATEWAY_BASE_URL` | `http://127.0.0.1:8000` | Base URL for the gateway being benchmarked. Use `http://127.0.0.1:18000` for the Compose stack when it is published on the alternate port. |
| `PUBLIC_MODEL` | `qwen3-0.6b` | Public model alias sent to the gateway. This should match the gateway registry alias, not necessarily the backend model name. |
| `TOKENIZER_MODEL` | `Qwen/Qwen3-0.6B` | Model/tokenizer identifier used by vLLM benchmark tooling to synthesize token-length-controlled prompts. This should match the backend model family so requested input/output token sizes are meaningful. |
| `NUM_PROMPTS` | `10` | Number of benchmark requests to send after vLLM's initial one-request validation. Larger values produce more stable measurements but take longer and consume more GPU time. |
| `REQUEST_RATE` | `1` | Target request arrival rate in requests per second. `1` sends a light steady workload. Higher values test concurrency/queueing. vLLM also accepts `inf` to send all requests immediately, but that is a burst benchmark and should be labeled separately. |
| `RANDOM_INPUT_LEN` | `128` | Target prompt length in tokens for the random dataset. This controls prefill work. Larger values stress prompt processing and KV cache allocation more. |
| `RANDOM_OUTPUT_LEN` | `64` | Target generated output length in tokens for the random dataset. This controls decode work. Larger values make TPOT/ITL and output throughput more important. |
| `RANDOM_RANGE_RATIO` | `0.0` | Variation around `RANDOM_INPUT_LEN` and `RANDOM_OUTPUT_LEN`. `0.0` keeps request sizes fixed. Values above zero create a distribution of request sizes and should be recorded because they change latency interpretation. |
| `TEMPERATURE` | `0` | Sampling temperature sent through the OpenAI-compatible request. `0` is deterministic/greedy and is useful for baseline repeatability. Higher values may change output behavior, but benchmark token lengths are still controlled by the benchmark request settings. |
| `RESULT_DIR` | `experiments/001_vllm_gateway_baseline/raw` | Directory where raw vLLM benchmark JSON is saved. Keep raw output unmodified. |
| `RESULT_FILENAME` | `vllm-gateway-serving.json` | Raw benchmark JSON filename. Use descriptive names that include path and workload context, such as `vllm-gateway-serving-compose-smoke.json`. |
| `VLLM_PROJECT_DIR` | `deploy/vllm` | Directory containing the pinned vLLM runtime. Override only when intentionally using a different benchmark runtime, and record that as provenance. |

The wrapper also sets fixed vLLM benchmark options:

| vLLM option | Value | Why |
| --- | --- | --- |
| `--backend` | `openai-chat` | Sends OpenAI-compatible chat requests instead of completion requests. |
| `--endpoint-type` | `openai-chat` | Forces vLLM `0.9.2` to build the correct chat request shape. Without this, the CLI can still default endpoint type handling to non-chat behavior. |
| `--endpoint` | `/v1/chat/completions` | Benchmarks the public gateway chat endpoint. |
| `--dataset-name` | `random` | Avoids external dataset setup and makes prompt/output token lengths explicit. |
| `--save-result` | enabled | Saves raw JSON evidence for later interpretation. |
| `--metadata` | gateway/model/runner fields | Preserves provenance in the raw JSON result. |

Interpretation rules:

- `NUM_PROMPTS=1` is only a smoke test for command and endpoint correctness.
- A saved benchmark claim needs enough prompts to reduce noise and should record
  gateway placement, vLLM placement, GPU, model, request rate, and token lengths.
- `REQUEST_RATE`, input length, and output length define the workload. Compare
  runs only when these are intentionally the same or the difference is the
  experiment variable.
- Benchmark-observed TTFT, TPOT, ITL, and throughput come from vLLM benchmark
  output. Gateway `/metrics` reports gateway-observed request latency and
  backend-reported token counters; those are related but not interchangeable.

## Compose Smoke Benchmark

Validated Compose path:

```bash
VLLM_HOST=172.17.0.1 ./deploy/vllm/run-openai-server.sh
```

```bash
TOKENKAKI_GATEWAY_PORT=18000 TOKENKAKI_PROMETHEUS_PORT=19090 \
  docker compose -f deploy/compose/compose.yaml up --build
```

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=1 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=16 \
RANDOM_OUTPUT_LEN=8 \
RESULT_FILENAME=vllm-gateway-serving-smoke.json \
./benchmarks/vllm-gateway-serving.sh
```

## Compose Small Benchmark

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=10 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=128 \
RANDOM_OUTPUT_LEN=64 \
RESULT_FILENAME=vllm-gateway-serving-compose-small.json \
./benchmarks/vllm-gateway-serving.sh
```

## Evidence Snapshots

```bash
curl -sS http://127.0.0.1:18000/metrics \
  > experiments/001_vllm_gateway_baseline/raw/gateway-metrics-after-compose-small.prom
```

```bash
curl -sS 'http://127.0.0.1:19090/api/v1/targets?state=active' \
  > experiments/001_vllm_gateway_baseline/raw/prometheus-targets-after-compose-small.json
```
