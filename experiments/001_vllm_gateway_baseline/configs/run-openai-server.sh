#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

VLLM_MODEL="${VLLM_MODEL:-Qwen/Qwen3-0.6B}"
VLLM_SERVED_MODEL_NAME="${VLLM_SERVED_MODEL_NAME:-$VLLM_MODEL}"
VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
VLLM_PORT="${VLLM_PORT:-8001}"
VLLM_EXTRA_ARGS="${VLLM_EXTRA_ARGS:-}"
VLLM_RUNNER="${VLLM_RUNNER:-uv run}"
CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-4}"
UV_TORCH_BACKEND="${UV_TORCH_BACKEND:-cu118}"
export CUDA_DEVICE_ORDER
export CUDA_VISIBLE_DEVICES
export UV_TORCH_BACKEND

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install uv before running the dedicated vLLM environment." >&2
  exit 127
fi

echo "Starting external vLLM OpenAI server"
echo "  model: ${VLLM_MODEL}"
echo "  served model name: ${VLLM_SERVED_MODEL_NAME}"
echo "  bind: ${VLLM_HOST}:${VLLM_PORT}"
echo "  runner: ${VLLM_RUNNER}"
echo "  cuda device order: ${CUDA_DEVICE_ORDER}"
echo "  cuda visible devices: ${CUDA_VISIBLE_DEVICES}"
echo "  uv torch backend: ${UV_TORCH_BACKEND}"
echo "  extra args: ${VLLM_EXTRA_ARGS:-<none>}"

cd "${SCRIPT_DIR}"

# shellcheck disable=SC2086
exec ${VLLM_RUNNER} vllm serve "${VLLM_MODEL}" \
  --served-model-name "${VLLM_SERVED_MODEL_NAME}" \
  --host "${VLLM_HOST}" \
  --port "${VLLM_PORT}" \
  ${VLLM_EXTRA_ARGS}
