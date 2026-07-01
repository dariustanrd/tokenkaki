#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." >/dev/null 2>&1 && pwd)"

TOPOLOGY="${1:-shared-a100-small}"

usage() {
  cat <<'EOF'
Usage:
  deploy/vllm/run-replica-set.sh [topology]

Topologies:
  shared-a100-small    Two smaller-model replicas on one A100 for development.
  multi-a100-qwen3-8b  Two Qwen3-8B replicas, one per A100.

Environment overrides:
  VLLM_SHARED_GPU              Physical GPU for shared-a100-small. Default: 4
  VLLM_MULTI_GPU_1             First GPU for multi-a100-qwen3-8b. Default: 4
  VLLM_MULTI_GPU_2             Second GPU for multi-a100-qwen3-8b. Default: 5
  VLLM_HOST                    Bind host for all replicas. Default: 127.0.0.1
  VLLM_SHARED_MODEL            Model for shared-a100-small. Default: Qwen/Qwen3-0.6B
  VLLM_SHARED_SERVED_MODEL     Served name for shared-a100-small. Default: model value
  VLLM_SHARED_EXTRA_ARGS       vLLM flags for shared-a100-small.
  VLLM_MULTI_MODEL             Model for multi-a100-qwen3-8b. Default: Qwen/Qwen3-8B
  VLLM_MULTI_SERVED_MODEL      Served name for multi-a100-qwen3-8b. Default: model value
  VLLM_MULTI_EXTRA_ARGS        vLLM flags for multi-a100-qwen3-8b.
  VLLM_REPLICA_READY_TIMEOUT_SECONDS
                               Per-replica readiness timeout. Default: 600
  VLLM_REPLICA_READY_INTERVAL_SECONDS
                               Readiness polling interval. Default: 5

Each replica runs as a background child process. Stop this launcher with Ctrl-C
to stop all replicas it started.
EOF
}

if [[ "$#" -gt 1 ]]; then
  echo "Unexpected argument: $2" >&2
  usage >&2
  exit 2
fi

cleanup_workers() {
  if [[ "${#WORKER_PIDS[@]}" -eq 0 ]]; then
    return 0
  fi

  echo "Stopping vLLM replicas"
  kill "${WORKER_PIDS[@]}" >/dev/null 2>&1 || true
  wait "${WORKER_PIDS[@]}" 2>/dev/null || true
}

wait_for_worker_ready() {
  local worker_id="$1"
  local host="$2"
  local port="$3"
  local pid="$4"
  local url="http://${host}:${port}/v1/models"
  local deadline=$((SECONDS + VLLM_REPLICA_READY_TIMEOUT_SECONDS))

  echo "Waiting for ${worker_id} to become ready at ${url}"

  while (( SECONDS < deadline )); do
    if ! kill -0 "${pid}" >/dev/null 2>&1; then
      echo "Replica ${worker_id} exited before readiness" >&2
      return 1
    fi

    if curl -fsS "${url}" >/dev/null 2>&1; then
      echo "Replica ${worker_id} is ready"
      return 0
    fi

    sleep "${VLLM_REPLICA_READY_INTERVAL_SECONDS}"
  done

  echo "Timed out waiting for ${worker_id} readiness after ${VLLM_REPLICA_READY_TIMEOUT_SECONDS}s" >&2
  return 1
}

start_worker() {
  local worker_id="$1"
  local model="$2"
  local served_model="$3"
  local host="$4"
  local port="$5"
  local cuda_devices="$6"
  local extra_args="$7"

  local cmd=(
    env
    "VLLM_WORKER_ID=${worker_id}"
    "VLLM_MODEL=${model}"
    "VLLM_SERVED_MODEL_NAME=${served_model}"
    "VLLM_HOST=${host}"
    "VLLM_PORT=${port}"
    "CUDA_VISIBLE_DEVICES=${cuda_devices}"
    "VLLM_EXTRA_ARGS=${extra_args}"
    "${REPO_ROOT}/deploy/vllm/run-openai-server.sh"
  )

  echo "Replica ${worker_id}:"
  echo "  backend url: http://${host}:${port}"
  echo "  model: ${model}"
  echo "  served model name: ${served_model}"
  echo "  CUDA_VISIBLE_DEVICES: ${cuda_devices}"
  echo "  extra args: ${extra_args:-<none>}"

  "${cmd[@]}" &
  WORKER_PIDS+=("$!")
  wait_for_worker_ready "${worker_id}" "${host}" "${port}" "$!"
  WORKERS_STARTED=$((WORKERS_STARTED + 1))
}

wait_for_workers() {
  if [[ "${#WORKER_PIDS[@]}" -eq 0 ]]; then
    return 0
  fi

  echo
  echo "Started ${#WORKER_PIDS[@]} vLLM replicas. Press Ctrl-C to stop them."
  wait "${WORKER_PIDS[@]}"
}

WORKER_PIDS=()
VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
VLLM_REPLICA_READY_TIMEOUT_SECONDS="${VLLM_REPLICA_READY_TIMEOUT_SECONDS:-600}"
VLLM_REPLICA_READY_INTERVAL_SECONDS="${VLLM_REPLICA_READY_INTERVAL_SECONDS:-5}"
WORKERS_STARTED=0

trap cleanup_workers INT TERM EXIT

case "${TOPOLOGY}" in
  -h | --help | help)
    usage
    exit 0
    ;;
  shared-a100-small)
    VLLM_SHARED_GPU="${VLLM_SHARED_GPU:-4}"
    VLLM_SHARED_MODEL="${VLLM_SHARED_MODEL:-Qwen/Qwen3-0.6B}"
    VLLM_SHARED_SERVED_MODEL="${VLLM_SHARED_SERVED_MODEL:-${VLLM_SHARED_MODEL}}"
    VLLM_SHARED_EXTRA_ARGS="${VLLM_SHARED_EXTRA_ARGS:---gpu-memory-utilization 0.4}"

    start_worker \
      "qwen3-0_6b-a100-gpu${VLLM_SHARED_GPU}-replica-1" \
      "${VLLM_SHARED_MODEL}" \
      "${VLLM_SHARED_SERVED_MODEL}" \
      "${VLLM_HOST}" \
      "8101" \
      "${VLLM_SHARED_GPU}" \
      "${VLLM_SHARED_EXTRA_ARGS}"
    start_worker \
      "qwen3-0_6b-a100-gpu${VLLM_SHARED_GPU}-replica-2" \
      "${VLLM_SHARED_MODEL}" \
      "${VLLM_SHARED_SERVED_MODEL}" \
      "${VLLM_HOST}" \
      "8111" \
      "${VLLM_SHARED_GPU}" \
      "${VLLM_SHARED_EXTRA_ARGS}"
    ;;
  multi-a100-qwen3-8b)
    VLLM_MULTI_GPU_1="${VLLM_MULTI_GPU_1:-4}"
    VLLM_MULTI_GPU_2="${VLLM_MULTI_GPU_2:-5}"
    VLLM_MULTI_MODEL="${VLLM_MULTI_MODEL:-Qwen/Qwen3-8B}"
    VLLM_MULTI_SERVED_MODEL="${VLLM_MULTI_SERVED_MODEL:-${VLLM_MULTI_MODEL}}"
    VLLM_MULTI_EXTRA_ARGS="${VLLM_MULTI_EXTRA_ARGS:---max-model-len 4096 --gpu-memory-utilization 0.85}"

    start_worker \
      "qwen3-8b-a100-gpu${VLLM_MULTI_GPU_1}" \
      "${VLLM_MULTI_MODEL}" \
      "${VLLM_MULTI_SERVED_MODEL}" \
      "${VLLM_HOST}" \
      "8201" \
      "${VLLM_MULTI_GPU_1}" \
      "${VLLM_MULTI_EXTRA_ARGS}"
    start_worker \
      "qwen3-8b-a100-gpu${VLLM_MULTI_GPU_2}" \
      "${VLLM_MULTI_MODEL}" \
      "${VLLM_MULTI_SERVED_MODEL}" \
      "${VLLM_HOST}" \
      "8211" \
      "${VLLM_MULTI_GPU_2}" \
      "${VLLM_MULTI_EXTRA_ARGS}"
    ;;
  *)
    echo "Unknown topology: ${TOPOLOGY}" >&2
    usage >&2
    exit 2
    ;;
esac

wait_for_workers
