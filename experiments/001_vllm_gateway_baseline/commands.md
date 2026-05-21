# Commands

Record exact commands for each saved Milestone 1 run here.

Canonical references:

- Backend runbook: `deploy/vllm/README.md`
- Compose gateway and Prometheus runbook: `deploy/compose/README.md`
- Reusable benchmark wrapper usage: `benchmarks/README.md`

Historical provenance: the saved artifacts in this folder were produced with
public alias `qwen3-0.6b` and backend/tokenizer model `Qwen/Qwen3-0.6B`. The
active runbooks may default to a newer phase model, so historical commands pin
these values explicitly. The gateway config used for this run is preserved in
`configs/gateway.compose.yaml`. The Compose command below was run when
`deploy/compose/gateway.yaml` matched that preserved config.

## Compose Smoke Benchmark

Validated Compose path:

```bash
VLLM_MODEL=Qwen/Qwen3-0.6B \
VLLM_SERVED_MODEL_NAME=Qwen/Qwen3-0.6B \
VLLM_HOST=172.17.0.1 ./deploy/vllm/run-openai-server.sh
```

```bash
TOKENKAKI_GATEWAY_PORT=18000 TOKENKAKI_PROMETHEUS_PORT=19090 \
  docker compose -f deploy/compose/compose.yaml up --build
```

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
PUBLIC_MODEL=qwen3-0.6b \
TOKENIZER_MODEL=Qwen/Qwen3-0.6B \
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
PUBLIC_MODEL=qwen3-0.6b \
TOKENIZER_MODEL=Qwen/Qwen3-0.6B \
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
