#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

BENCHMARK_TARGET="${BENCHMARK_TARGET:-gateway}"
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://127.0.0.1:8000}"
VLLM_BASE_URL="${VLLM_BASE_URL:-http://172.17.0.1:8001}"
PUBLIC_MODEL="${PUBLIC_MODEL:-qwen3-8b}"
BACKEND_MODEL="${BACKEND_MODEL:-Qwen/Qwen3-8B}"
TOKENIZER_MODEL="${TOKENIZER_MODEL:-Qwen/Qwen3-8B}"
NUM_PROMPTS="${NUM_PROMPTS:-10}"
REQUEST_RATE="${REQUEST_RATE:-5}"
RANDOM_INPUT_LEN="${RANDOM_INPUT_LEN:-128}"
RANDOM_OUTPUT_LEN="${RANDOM_OUTPUT_LEN:-64}"
RANDOM_RANGE_RATIO="${RANDOM_RANGE_RATIO:-0.0}"
TEMPERATURE="${TEMPERATURE:-0}"
UV_TORCH_BACKEND="${UV_TORCH_BACKEND:-auto}"
VLLM_PROJECT_DIR="${VLLM_PROJECT_DIR:-${REPO_ROOT}/deploy/vllm}"
EXPERIMENT_ROOT="${EXPERIMENT_ROOT:-${REPO_ROOT}/experiments/001_vllm_gateway_baseline}"
export UV_TORCH_BACKEND

case "${EXPERIMENT_ROOT}" in
  /*) ;;
  *) EXPERIMENT_ROOT="${REPO_ROOT}/${EXPERIMENT_ROOT}" ;;
esac

case "${BENCHMARK_TARGET}" in
  gateway)
    BASE_URL="${BASE_URL:-${GATEWAY_BASE_URL}}"
    SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-${PUBLIC_MODEL}}"
    BENCHMARK_PATH="gateway"
    DEFAULT_RESULT_DIR="${EXPERIMENT_ROOT}/4_gateway_serve"
    DEFAULT_RESULT_FILENAME="vllm-gateway-serving.json"
    ;;
  vllm)
    BASE_URL="${BASE_URL:-${VLLM_BASE_URL}}"
    SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-${BACKEND_MODEL}}"
    BENCHMARK_PATH="direct_vllm"
    DEFAULT_RESULT_DIR="${EXPERIMENT_ROOT}/3_direct_vllm_serve"
    DEFAULT_RESULT_FILENAME="vllm-direct-serving.json"
    ;;
  *)
    echo "BENCHMARK_TARGET must be either 'gateway' or 'vllm', got: ${BENCHMARK_TARGET}" >&2
    exit 2
    ;;
esac

RESULT_DIR="${RESULT_DIR:-${DEFAULT_RESULT_DIR}}"
RESULT_FILENAME="${RESULT_FILENAME:-${DEFAULT_RESULT_FILENAME}}"

case "${RESULT_DIR}" in
  /*) ;;
  *) RESULT_DIR="${REPO_ROOT}/${RESULT_DIR}" ;;
esac

mkdir -p "${RESULT_DIR}"

echo "Running vLLM serving benchmark"
echo "  target: ${BENCHMARK_TARGET}"
echo "  benchmark path: ${BENCHMARK_PATH}"
echo "  base URL: ${BASE_URL}"
echo "  served model name: ${SERVED_MODEL_NAME}"
echo "  public model: ${PUBLIC_MODEL}"
echo "  backend model: ${BACKEND_MODEL}"
echo "  tokenizer model: ${TOKENIZER_MODEL}"
echo "  experiment root: ${EXPERIMENT_ROOT}"
echo "  num prompts: ${NUM_PROMPTS}"
echo "  request rate: ${REQUEST_RATE}"
echo "  random input/output tokens: ${RANDOM_INPUT_LEN}/${RANDOM_OUTPUT_LEN}"
echo "  uv torch backend: ${UV_TORCH_BACKEND}"
echo "  result: ${RESULT_DIR}/${RESULT_FILENAME}"

cd "${VLLM_PROJECT_DIR}"

uv run vllm bench serve \
  --backend openai-chat \
  --endpoint-type openai-chat \
  --endpoint /v1/chat/completions \
  --base-url "${BASE_URL}" \
  --model "${TOKENIZER_MODEL}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
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
  benchmark_target="${BENCHMARK_TARGET}" \
  benchmark_path="${BENCHMARK_PATH}" \
  base_url="${BASE_URL}" \
  gateway_base_url="${GATEWAY_BASE_URL}" \
  vllm_base_url="${VLLM_BASE_URL}" \
  public_model="${PUBLIC_MODEL}" \
  backend_model="${BACKEND_MODEL}" \
  served_model_name="${SERVED_MODEL_NAME}" \
  tokenizer_model="${TOKENIZER_MODEL}" \
  experiment_root="${EXPERIMENT_ROOT}" \
  uv_torch_backend="${UV_TORCH_BACKEND}" \
  benchmark_runner="same-host"
