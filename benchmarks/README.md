# Benchmarks

Benchmark commands live here, while saved raw outputs live under milestone
folders in `experiments/`.

## Milestone 1 Gateway Serving Benchmark

Use `vllm bench serve` from the pinned `deploy/vllm/` runtime environment to
send OpenAI-compatible chat requests through the gateway.

The wrapper sets both `--backend openai-chat` and
`--endpoint-type openai-chat`. vLLM `0.9.2` needs both options for the chat
completion request shape; setting only the backend leaves the endpoint type at
the CLI default.

Default command:

```bash
./benchmarks/vllm-gateway-serving.sh
```

Useful overrides:

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=10 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=128 \
RANDOM_OUTPUT_LEN=64 \
RESULT_FILENAME=vllm-gateway-serving-compose-smoke.json \
./benchmarks/vllm-gateway-serving.sh
```

Tiny smoke run used to validate the command path:

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=1 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=16 \
RANDOM_OUTPUT_LEN=8 \
RESULT_FILENAME=vllm-gateway-serving-smoke.json \
./benchmarks/vllm-gateway-serving.sh
```

The default output path is:

```text
experiments/001_vllm_gateway_baseline/raw/vllm-gateway-serving.json
```

Keep result interpretation separate from the raw benchmark output. Gateway
metrics, benchmark-observed latency, backend-reported token usage, and GPU
metrics are related evidence streams, not interchangeable measurements.
