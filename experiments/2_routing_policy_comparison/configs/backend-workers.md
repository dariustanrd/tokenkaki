# Milestone 2 Backend Worker Inventory

Fill this file before running routing-policy benchmarks. Keep it with the saved
experiment artifacts so each routing result can be traced back to the real vLLM
workers that served traffic.

## Topology Summary

- Date:
- Host or cluster:
- Benchmark runner location:
- Topology:
  - [ ] one A100 with multiple smaller-model replicas
  - [ ] multiple A100s with one replica per GPU
  - [ ] other:
- Shared-GPU contention present:
  - [ ] yes
  - [ ] no
- Notes:

## Runtime Provenance

- vLLM version:
- PyTorch version:
- CUDA runtime selected by PyTorch:
- NVIDIA driver:
- `UV_TORCH_BACKEND`:
- vLLM sync command:
- `deploy/vllm/pyproject.toml` revision:
- `deploy/vllm/uv.lock` revision:
- `HF_HOME`:
- `VLLM_CACHE_ROOT`:

## Worker Inventory

| Worker ID | Backend URL | Public gateway model | vLLM model | Served model name | CUDA_VISIBLE_DEVICES | Port | Enabled | VLLM_EXTRA_ARGS | Smoke status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3-0_6b-a100-gpu4-replica-1 | http://127.0.0.1:8101 | qwen3-0.6b | Qwen/Qwen3-0.6B | Qwen/Qwen3-0.6B | 4 | 8101 | yes | --gpu-memory-utilization 0.4 | pending |
| qwen3-0_6b-a100-gpu4-replica-2 | http://127.0.0.1:8111 | qwen3-0.6b | Qwen/Qwen3-0.6B | Qwen/Qwen3-0.6B | 4 | 8111 | yes | --gpu-memory-utilization 0.4 | pending |

## Direct Smoke Commands

Start the planned replica set first:

```bash
./deploy/vllm/run-replica-set.sh shared-a100-small dry-run
./deploy/vllm/run-replica-set.sh shared-a100-small
```

Run one `/v1/models` and one non-streaming `/v1/chat/completions` smoke per
worker:

```bash
VLLM_HOST="127.0.0.1" \
VLLM_PORT="8101" \
VLLM_SERVED_MODEL_NAME="Qwen/Qwen3-0.6B" \
./deploy/vllm/smoke-openai.sh
```

Optional streaming smoke:

```bash
VLLM_HOST="127.0.0.1" \
VLLM_PORT="8101" \
VLLM_SERVED_MODEL_NAME="Qwen/Qwen3-0.6B" \
VLLM_SMOKE_STREAM="1" \
./deploy/vllm/smoke-openai.sh
```

## Smoke Results

| Worker ID | `/v1/models` | non-streaming chat | streaming chat | Timestamp | Notes |
| --- | --- | --- | --- | --- | --- |
| qwen3-0_6b-a100-gpu4-replica-1 | pending | pending | not run |  |  |
| qwen3-0_6b-a100-gpu4-replica-2 | pending | pending | not run |  |  |

## Interpretation Labels

Use these labels in benchmark notes and writeups:

- `real-vllm-backends`: traffic was served by external vLLM OpenAI-compatible
  workers.
- `shared-gpu-contention`: multiple replicas shared one GPU, so policy results
  include resource contention inside the same device.
- `one-replica-per-gpu`: each worker had a dedicated GPU.
- `direct-backend-smoked`: every worker passed direct backend smoke checks before
  gateway benchmarks started.
