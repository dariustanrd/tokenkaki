#!/usr/bin/env bash
set -euo pipefail

VLLM_MODEL="${VLLM_MODEL:-Qwen/Qwen3-8B}"
VLLM_SERVED_MODEL_NAME="${VLLM_SERVED_MODEL_NAME:-$VLLM_MODEL}"
VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
VLLM_PORT="${VLLM_PORT:-8001}"
VLLM_API_BASE="${VLLM_API_BASE:-http://${VLLM_HOST}:${VLLM_PORT}}"
VLLM_SMOKE_STREAM="${VLLM_SMOKE_STREAM:-0}"

echo "Checking vLLM models endpoint at ${VLLM_API_BASE}/v1/models"
curl -fsS "${VLLM_API_BASE}/v1/models"
echo

echo "Checking vLLM non-streaming chat completion for ${VLLM_SERVED_MODEL_NAME}"
curl -fsS "${VLLM_API_BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d @- <<JSON
{
  "model": "${VLLM_SERVED_MODEL_NAME}",
  "messages": [
    {
      "role": "user",
      "content": "Reply with exactly: tokenkaki-vllm-smoke-ok"
    }
  ],
  "temperature": 0,
  "max_tokens": 128,
  "stream": false
}
JSON
echo

if [[ "${VLLM_SMOKE_STREAM}" == "1" ]]; then
  echo "Checking vLLM streaming chat completion for ${VLLM_SERVED_MODEL_NAME}"
  curl -fsS "${VLLM_API_BASE}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d @- <<JSON
{
  "model": "${VLLM_SERVED_MODEL_NAME}",
  "messages": [
    {
      "role": "user",
      "content": "Reply with exactly: tokenkaki-vllm-stream-smoke-ok"
    }
  ],
  "temperature": 0,
  "max_tokens": 128,
  "stream": true
}
JSON
  echo
fi
