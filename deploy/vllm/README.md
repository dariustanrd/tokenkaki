# vLLM Local GPU Dev Lab

This folder contains Milestone 1 artifacts for running vLLM as an external
OpenAI-compatible backend on the NVIDIA GPU machine.

The gateway must treat vLLM as an HTTP dependency. Do not import vLLM from
`tokenkaki.gateway`, and do not make vLLM a managed child process of the
gateway.

## Default Topology

```text
benchmark or curl on this GPU host
  -> tokenkaki.gateway
  -> http://127.0.0.1:8001/v1
  -> external vLLM process
  -> NVIDIA GPU execution
```

Why this matters: same-host development removes private-network latency between
the gateway and backend. If a remote client calls this host over Tailscale or
another private network, label that result as remote-client API-path evidence,
not as the Milestone 1 same-host baseline.

## Environment

This folder is a dedicated uv project for the external vLLM runtime. Keep it
separate from the repo-root gateway environment because vLLM, PyTorch, CUDA,
and GPU driver compatibility are operational backend concerns.

From this folder, create or refresh the vLLM environment:

```bash
cd deploy/vllm
UV_TORCH_BACKEND=auto uv sync
uv run vllm serve --help
cd ../..
```

Why: the gateway can stay lightweight and testable while the GPU host still has
a repeatable backend runtime.

`UV_TORCH_BACKEND=auto` lets uv choose the PyTorch wheel index from the local GPU
driver and accelerator during sync. This keeps the vLLM runtime on the newest
known-good release for the current CUDA 12 driver constraints without
hard-coding a CUDA wheel family in `pyproject.toml`.

The helper script runs the same sync command and prints the resolved vLLM,
PyTorch, and CUDA runtime versions:

```bash
./deploy/vllm/sync-runtime.sh
```

Create a local environment file from the example:

```bash
cp deploy/vllm/env.example deploy/vllm/.env.local
```

Then edit `deploy/vllm/.env.local` for this machine. Keep cache paths and
serving flags explicit because experiment reports should record the backend
configuration that produced a result.

Load it before running vLLM:

```bash
set -a
. deploy/vllm/.env.local
set +a
```

For the current packaged gateway config, set the backend model values to:

```text
public gateway alias: qwen3-8b
vLLM backend model: Qwen/Qwen3-8B
vLLM base URL: http://127.0.0.1:8001
CUDA_DEVICE_ORDER: PCI_BUS_ID
CUDA_VISIBLE_DEVICES: 4
```

`CUDA_VISIBLE_DEVICES=4` intentionally restricts vLLM to the idle physical A100
shown as GPU 4 in `nvidia-smi`. Inside the vLLM process, that GPU is remapped to
local `cuda:0`, which is expected for a single-GPU run.

## Prerequisites

Check the GPU and active Python environment first:

```bash
nvidia-smi
uv --version
cd deploy/vllm
uv run python --version
uv run python -c "import torch, vllm; print(vllm.__version__); print(torch.__version__, torch.version.cuda)"
```

The `deploy/vllm/pyproject.toml` vLLM pin plus `uv.lock` records the current
runtime target. If CUDA, PyTorch, or vLLM compatibility requires a different
version, update those files and record the reason in the experiment artifact.

Current runtime target:

```text
vLLM: 0.19.1
PyTorch backend: selected by uv from the local GPU driver and accelerator
Sync command: `UV_TORCH_BACKEND=auto uv sync`
```

`vllm 0.20.0` and newer currently require a PyTorch line that resolves to CUDA
13 on this host, which fails against the CUDA 12.2-era NVIDIA driver. The
`0.19.1` pin is the newest tested local runtime that keeps the environment on a
CUDA 12 PyTorch stack.

When refreshing this GPU host's environment, keep the same backend selection:

```bash
cd deploy/vllm
UV_TORCH_BACKEND=auto uv sync
```

## Start vLLM

```bash
./deploy/vllm/run-openai-server.sh
```

The script runs `uv run vllm serve` from this folder's dedicated project. If you
need to bypass uv for debugging, set `VLLM_RUNNER` explicitly, for example
`VLLM_RUNNER=""`, but do not use that for saved benchmark evidence unless it is
recorded. The script exports `UV_TORCH_BACKEND=auto` by default if it is not
already set.

By default this binds to `127.0.0.1:8001`. Prefer loopback for Milestone 1
development. Bind to a private host interface only when a separate private
client needs to call the backend directly for debugging.

The script also defaults to `CUDA_DEVICE_ORDER=PCI_BUS_ID` and
`CUDA_VISIBLE_DEVICES=4`. Override these only when intentionally moving the
backend to a different GPU and record the change in the experiment artifact.

Useful overrides:

```bash
VLLM_MODEL="Qwen/Qwen3-8B" \
VLLM_SERVED_MODEL_NAME="Qwen/Qwen3-8B" \
VLLM_HOST="127.0.0.1" \
VLLM_PORT="8001" \
CUDA_VISIBLE_DEVICES="4" \
VLLM_EXTRA_ARGS="--max-model-len 4096 --gpu-memory-utilization 0.85" \
./deploy/vllm/run-openai-server.sh
```

## Direct Backend Smoke Tests

Run these before routing any traffic through the gateway:

```bash
VLLM_MODEL="Qwen/Qwen3-8B" ./deploy/vllm/smoke-openai.sh
```

The smoke script checks:

- `GET /v1/models`
- `POST /v1/chat/completions` with `stream: false`

These checks prove the external backend is reachable and serving the configured
model. They do not prove gateway forwarding; that belongs to the next tracer
bullet slice.

For gateway and Prometheus validation through Docker Compose, use
`deploy/compose/README.md`. Compose needs vLLM bound to a private
Docker-reachable host address because the gateway container cannot reach a host
process that listens only on `127.0.0.1`.

## Gateway Config Compatibility

The current packaged gateway config expects:

```yaml
models:
  - name: qwen3-8b
    enabled: true
    backend:
      type: vllm
      base_url: http://127.0.0.1:8001
      model: Qwen/Qwen3-8B
```

If you change `VLLM_PORT`, `VLLM_HOST`, or `VLLM_SERVED_MODEL_NAME`, also update
the gateway config used for that run. Keep the public alias stable unless the
experiment intentionally compares model aliases.

## Provenance To Record

For every saved Milestone 1 result, record:

- GPU model and driver from `nvidia-smi`
- `deploy/vllm/pyproject.toml` and `uv.lock` versions used for the vLLM runtime
- `UV_TORCH_BACKEND` value used for lock/sync/run
- vLLM version and install/sync command
- model ID and served model name
- vLLM bind address and backend URL used by the gateway
- `CUDA_DEVICE_ORDER` and `CUDA_VISIBLE_DEVICES`
- cache paths such as `HF_HOME` and `VLLM_CACHE_ROOT`
- `VLLM_EXTRA_ARGS`
- whether the benchmark runner was same-host or a private remote client

Reusable gateway benchmark wrapper usage lives in `benchmarks/README.md`.
Published Milestone 1 benchmark commands and interpretation should live in the
relevant `Behind the API` blogpost or experiment writeup. Keep raw vLLM startup
logs, benchmark JSON, stdout/stderr captures, and metrics snapshots under the
matching `experiments/` milestone folder.
