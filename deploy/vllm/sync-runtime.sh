#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

UV_TORCH_BACKEND="${UV_TORCH_BACKEND:-auto}"
export UV_TORCH_BACKEND

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install uv before syncing the dedicated vLLM environment." >&2
  exit 127
fi

echo "Syncing dedicated vLLM runtime"
echo "  project: ${SCRIPT_DIR}"
echo "  uv torch backend: ${UV_TORCH_BACKEND}"

cd "${SCRIPT_DIR}"
uv sync

uv run python -c "import torch, vllm; print(f'vllm {vllm.__version__}'); print(f'torch {torch.__version__} cuda {torch.version.cuda}')"
