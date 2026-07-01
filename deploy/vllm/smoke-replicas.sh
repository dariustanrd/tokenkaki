#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

TOPOLOGY="${1:-shared-a100-small}"

usage() {
  cat <<'EOF'
Usage:
  deploy/vllm/smoke-replicas.sh [topology]

Topologies:
  shared-a100-small    Smoke ports 8101 and 8111.
  multi-a100-qwen3-8b  Smoke ports 8201 and 8211.

Environment overrides:
  VLLM_HOST                    Host for all replicas. Default: 127.0.0.1
  VLLM_SHARED_MODEL            Model for shared-a100-small. Default: Qwen/Qwen3-0.6B
  VLLM_SHARED_SERVED_MODEL     Served name for shared-a100-small. Default: model value
  VLLM_MULTI_MODEL             Model for multi-a100-qwen3-8b. Default: Qwen/Qwen3-8B
  VLLM_MULTI_SERVED_MODEL      Served name for multi-a100-qwen3-8b. Default: model value
  VLLM_SMOKE_STREAM            Set to 1 to include streaming smoke checks. Default: 0

This script runs smoke-openai.sh for every replica in parallel, then prints each
worker's captured output.
EOF
}

if [[ "$#" -gt 1 ]]; then
  echo "Unexpected argument: $2" >&2
  usage >&2
  exit 2
fi

TARGET_IDS=()
TARGET_HOSTS=()
TARGET_PORTS=()
TARGET_MODELS=()
TARGET_SERVED_MODELS=()

add_target() {
  TARGET_IDS+=("$1")
  TARGET_HOSTS+=("$2")
  TARGET_PORTS+=("$3")
  TARGET_MODELS+=("$4")
  TARGET_SERVED_MODELS+=("$5")
}

VLLM_HOST="${VLLM_HOST:-127.0.0.1}"

case "${TOPOLOGY}" in
  -h | --help | help)
    usage
    exit 0
    ;;
  shared-a100-small)
    VLLM_SHARED_MODEL="${VLLM_SHARED_MODEL:-Qwen/Qwen3-0.6B}"
    VLLM_SHARED_SERVED_MODEL="${VLLM_SHARED_SERVED_MODEL:-${VLLM_SHARED_MODEL}}"

    add_target \
      "qwen3-0_6b-replica-1" \
      "${VLLM_HOST}" \
      "8101" \
      "${VLLM_SHARED_MODEL}" \
      "${VLLM_SHARED_SERVED_MODEL}"
    add_target \
      "qwen3-0_6b-replica-2" \
      "${VLLM_HOST}" \
      "8111" \
      "${VLLM_SHARED_MODEL}" \
      "${VLLM_SHARED_SERVED_MODEL}"
    ;;
  multi-a100-qwen3-8b)
    VLLM_MULTI_MODEL="${VLLM_MULTI_MODEL:-Qwen/Qwen3-8B}"
    VLLM_MULTI_SERVED_MODEL="${VLLM_MULTI_SERVED_MODEL:-${VLLM_MULTI_MODEL}}"

    add_target \
      "qwen3-8b-replica-1" \
      "${VLLM_HOST}" \
      "8201" \
      "${VLLM_MULTI_MODEL}" \
      "${VLLM_MULTI_SERVED_MODEL}"
    add_target \
      "qwen3-8b-replica-2" \
      "${VLLM_HOST}" \
      "8211" \
      "${VLLM_MULTI_MODEL}" \
      "${VLLM_MULTI_SERVED_MODEL}"
    ;;
  *)
    echo "Unknown topology: ${TOPOLOGY}" >&2
    usage >&2
    exit 2
    ;;
esac

TMP_DIR="$(mktemp -d)"
PIDS=()
LOGS=()

cleanup() {
  local pid

  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done

  rm -rf "${TMP_DIR}"
}

trap cleanup EXIT

echo "Smoking ${#TARGET_IDS[@]} vLLM replicas for topology ${TOPOLOGY}"

for index in "${!TARGET_IDS[@]}"; do
  log_file="${TMP_DIR}/${TARGET_IDS[$index]}.log"
  LOGS+=("${log_file}")

  echo "Starting smoke check for ${TARGET_IDS[$index]} at http://${TARGET_HOSTS[$index]}:${TARGET_PORTS[$index]}"

  env -u VLLM_API_BASE \
    "VLLM_MODEL=${TARGET_MODELS[$index]}" \
    "VLLM_SERVED_MODEL_NAME=${TARGET_SERVED_MODELS[$index]}" \
    "VLLM_HOST=${TARGET_HOSTS[$index]}" \
    "VLLM_PORT=${TARGET_PORTS[$index]}" \
    "VLLM_SMOKE_STREAM=${VLLM_SMOKE_STREAM:-0}" \
    "${SCRIPT_DIR}/smoke-openai.sh" >"${log_file}" 2>&1 &

  PIDS+=("$!")
done

FAILED=0

for index in "${!PIDS[@]}"; do
  if wait "${PIDS[$index]}"; then
    echo "PASS ${TARGET_IDS[$index]}"
  else
    echo "FAIL ${TARGET_IDS[$index]}" >&2
    FAILED=1
  fi
done

PIDS=()

echo

for index in "${!TARGET_IDS[@]}"; do
  echo "===== ${TARGET_IDS[$index]} http://${TARGET_HOSTS[$index]}:${TARGET_PORTS[$index]} ====="
  cat "${LOGS[$index]}"
  echo
done

if [[ "${FAILED}" -ne 0 ]]; then
  echo "One or more replica smoke checks failed" >&2
  exit 1
fi

echo "All replica smoke checks passed"
