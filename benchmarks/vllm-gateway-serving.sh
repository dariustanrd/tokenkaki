#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://127.0.0.1:8000}"
PUBLIC_MODEL="${PUBLIC_MODEL:-qwen3-0.6b}"
TOKENIZER_MODEL="${TOKENIZER_MODEL:-Qwen/Qwen3-0.6B}"
NUM_PROMPTS="${NUM_PROMPTS:-10}"
REQUEST_RATE="${REQUEST_RATE:-5}"
RANDOM_INPUT_LEN="${RANDOM_INPUT_LEN:-128}"
RANDOM_OUTPUT_LEN="${RANDOM_OUTPUT_LEN:-64}"
RANDOM_RANGE_RATIO="${RANDOM_RANGE_RATIO:-0.0}"
TEMPERATURE="${TEMPERATURE:-0}"
RESULT_DIR="${RESULT_DIR:-${REPO_ROOT}/experiments/001_vllm_gateway_baseline/raw}"
RESULT_FILENAME="${RESULT_FILENAME:-vllm-gateway-serving.json}"
VLLM_PROJECT_DIR="${VLLM_PROJECT_DIR:-${REPO_ROOT}/deploy/vllm}"

mkdir -p "${RESULT_DIR}"

echo "Running vLLM serving benchmark against tokenkaki gateway"
echo "  gateway base URL: ${GATEWAY_BASE_URL}"
echo "  public model: ${PUBLIC_MODEL}"
echo "  tokenizer model: ${TOKENIZER_MODEL}"
echo "  num prompts: ${NUM_PROMPTS}"
echo "  request rate: ${REQUEST_RATE}"
echo "  random input/output tokens: ${RANDOM_INPUT_LEN}/${RANDOM_OUTPUT_LEN}"
echo "  result: ${RESULT_DIR}/${RESULT_FILENAME}"

cd "${VLLM_PROJECT_DIR}"

uv run vllm bench serve \
  --backend openai-chat \
  --endpoint-type openai-chat \
  --endpoint /v1/chat/completions \
  --base-url "${GATEWAY_BASE_URL}" \
  --model "${TOKENIZER_MODEL}" \
  --served-model-name "${PUBLIC_MODEL}" \
  --dataset-name random \
  --num-prompts "${NUM_PROMPTS}" \
  --request-rate "${REQUEST_RATE}" \
  --random-input-len "${RANDOM_INPUT_LEN}" \
  --random-output-len "${RANDOM_OUTPUT_LEN}" \
  --random-range-ratio "${RANDOM_RANGE_RATIO}" \
  --temperature "${TEMPERATURE}" \
  --save-result \
  --result-dir "${RESULT_DIR}" \
  --result-filename "${RESULT_FILENAME}" \
  --metadata \
  gateway_base_url="${GATEWAY_BASE_URL}" \
  public_model="${PUBLIC_MODEL}" \
  tokenizer_model="${TOKENIZER_MODEL}" \
  benchmark_runner="same-host"
