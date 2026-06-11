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
UV_TORCH_BACKEND=cu118 uv sync --frozen
uv run vllm serve --help
cd ../..
```

Why: the gateway can stay lightweight and testable while the GPU host still has
a repeatable backend runtime.

`UV_TORCH_BACKEND=cu118` is intentional. This GPU host has A100 GPUs on an
NVIDIA 535.x driver, so the runtime uses a newer vLLM CUDA 11.8 prebuilt wheel
instead of resolving CUDA 12.6/12.8/12.9 wheels that require newer drivers or
may force a source build. `deploy/vllm/pyproject.toml` also pins the PyTorch
family packages to CUDA 11.8 local-version wheels so the vLLM wheel and PyTorch
wheel family stay aligned.

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
uv run python -c "import vllm; print(vllm.__version__)"
```

The dependency range in `deploy/vllm/pyproject.toml` plus `uv.lock` is a
starting point, not a benchmark claim. If CUDA, PyTorch, or vLLM compatibility
requires a different version, update those files and record the reason in the
experiment artifact.

Current runtime target:

```text
vLLM: 0.9.2+cu118 prebuilt wheel
PyTorch: 2.7.0+cu118
TorchVision: 0.22.0+cu118
TorchAudio: 2.7.0+cu118
Transformers: >=4.51.1,<4.54
```

When checking or refreshing the lockfile on this GPU host, keep the same backend
selection:

```bash
cd deploy/vllm
UV_TORCH_BACKEND=cu118 uv lock
```

## Start vLLM

```bash
./deploy/vllm/run-openai-server.sh
```

The script runs `uv run vllm serve` from this folder's dedicated project. If you
need to bypass uv for debugging, set `VLLM_RUNNER` explicitly, for example
`VLLM_RUNNER=""`, but do not use that for saved benchmark evidence unless it is
recorded. The script exports `UV_TORCH_BACKEND=cu118` by default if it is not
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
