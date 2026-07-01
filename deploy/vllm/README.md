# vLLM Runtime Scripts

This directory contains the local runtime project and helper scripts for running
vLLM as an external OpenAI-compatible backend.

The gateway should treat vLLM as an HTTP dependency. It should not import vLLM,
embed vLLM internals, or manage vLLM worker lifecycles. Keeping vLLM separate
makes the gateway lightweight while still giving experiments a repeatable GPU
serving runtime.

## Files

- `pyproject.toml` and `uv.lock`: dedicated uv project for the vLLM runtime.
- `sync-runtime.sh`: creates or refreshes the vLLM uv environment and prints
  resolved vLLM, PyTorch, and CUDA runtime versions.
- `run-openai-server.sh`: starts one vLLM OpenAI-compatible server.
- `run-replica-set.sh`: starts predefined sets of vLLM replicas for routing and
  multi-backend experiments.
- `smoke-openai.sh`: checks a running vLLM worker through `/v1/models` and
  `/v1/chat/completions`.
- `smoke-replicas.sh`: runs `smoke-openai.sh` against every worker in a replica
  topology at the same time.
- `env.example`: template for local machine-specific runtime settings.

## Dedicated uv Environment

This folder is intentionally its own uv project. vLLM, PyTorch, CUDA wheels,
and GPU driver compatibility are backend runtime concerns, so they should not
be mixed into the repo-root gateway environment.

Create or refresh the runtime with:

```bash
./deploy/vllm/sync-runtime.sh
```

The script runs from `deploy/vllm`, exports `UV_TORCH_BACKEND=auto` by default,
then runs `uv sync`. The `UV_TORCH_BACKEND=auto` setting lets uv choose a
PyTorch wheel backend from the local driver and accelerator instead of
hard-coding a CUDA wheel family in `pyproject.toml`.

Equivalent manual commands:

```bash
cd deploy/vllm
UV_TORCH_BACKEND=auto uv sync
uv run vllm serve --help
cd ../..
```

Check the resolved runtime when debugging environment issues:

```bash
cd deploy/vllm
uv run python -c "import torch, vllm; print(vllm.__version__); print(torch.__version__, torch.version.cuda)"
cd ../..
```

The current runtime target is pinned by `deploy/vllm/pyproject.toml` and
`deploy/vllm/uv.lock`.

```text
vLLM: 0.19.1
PyTorch backend: selected by uv from the local GPU driver and accelerator
Sync command: UV_TORCH_BACKEND=auto uv sync
```

On the current GPU host, `vllm 0.20.0` and newer resolve to a PyTorch line that
expects CUDA 13 and fails against the CUDA 12.2-era NVIDIA driver. The `0.19.1`
pin is the newest tested local runtime that keeps this environment on a CUDA 12
PyTorch stack. If this changes, update the lockfile and record the reason in
the matching experiment artifact.

## Local Environment

Create a machine-local environment file:

```bash
cp deploy/vllm/env.example deploy/vllm/.env.local
```

Edit `.env.local` for the GPU, model, cache paths, and vLLM flags on this host.
Load it before starting a worker:

```bash
set -a
. deploy/vllm/.env.local
set +a
```

Common values for the current local gateway configuration:

```text
public gateway alias: qwen3-8b
vLLM backend model: Qwen/Qwen3-8B
vLLM base URL: http://127.0.0.1:8001
CUDA_DEVICE_ORDER: PCI_BUS_ID
CUDA_VISIBLE_DEVICES: 4
```

`CUDA_VISIBLE_DEVICES=4` restricts vLLM to the physical A100 shown as GPU 4 in
`nvidia-smi`. Inside the vLLM process, that device is remapped to local
`cuda:0`, which is expected for a single-worker run.

Keep cache paths and serving flags explicit. They are part of result
provenance, especially when comparing runs across models, GPUs, or memory
settings.

## Single Worker

Start one OpenAI-compatible vLLM server:

```bash
./deploy/vllm/run-openai-server.sh
```

Defaults:

```text
VLLM_MODEL=Qwen/Qwen3-8B
VLLM_SERVED_MODEL_NAME=$VLLM_MODEL
VLLM_HOST=127.0.0.1
VLLM_PORT=8001
VLLM_WORKER_ID=vllm-$VLLM_PORT
CUDA_DEVICE_ORDER=PCI_BUS_ID
CUDA_VISIBLE_DEVICES=4
UV_TORCH_BACKEND=auto
VLLM_RUNNER="uv run"
```

Use this script when you need one backend for gateway development, direct vLLM
debugging, or benchmark baselines. It is also the primitive used by
`run-replica-set.sh`.

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

The script runs `uv run vllm serve` from this directory. For debugging only,
`VLLM_RUNNER` can be overridden, for example `VLLM_RUNNER=""`. Saved benchmark
evidence should record that override because it changes how the runtime was
launched.

Prefer binding to `127.0.0.1` for same-host development. If the gateway runs in
Docker Compose or another machine needs direct access, bind `VLLM_HOST` to a
private address reachable from that client and update the gateway config for
that run.

## Replica Sets

Start multiple vLLM workers with:

```bash
./deploy/vllm/run-replica-set.sh [topology]
```

Replica sets exist so the gateway can be tested against multiple real
OpenAI-compatible backends. This is needed for routing-policy work, load
distribution checks, and experiments where worker identity, backend URL, and GPU
placement matter.

The launcher starts each worker as a background child process, waits for its
`/v1/models` endpoint to become ready, then starts the next worker. Stop the
launcher with `Ctrl-C` to stop the replicas it started.

Readiness defaults:

```text
VLLM_REPLICA_READY_TIMEOUT_SECONDS=600
VLLM_REPLICA_READY_INTERVAL_SECONDS=5
```

Override them for large models or cold caches:

```bash
VLLM_REPLICA_READY_TIMEOUT_SECONDS="900" \
VLLM_REPLICA_READY_INTERVAL_SECONDS="10" \
./deploy/vllm/run-replica-set.sh shared-a100-small
```

### Shared A100 Small

`shared-a100-small` starts two smaller-model replicas on one physical A100:

```bash
./deploy/vllm/run-replica-set.sh shared-a100-small
```

Defaults:

```text
ports: 8101, 8111
VLLM_SHARED_GPU=4
VLLM_SHARED_MODEL=Qwen/Qwen3-0.6B
VLLM_SHARED_SERVED_MODEL=$VLLM_SHARED_MODEL
VLLM_SHARED_EXTRA_ARGS="--gpu-memory-utilization 0.4"
```

Useful overrides:

```bash
VLLM_SHARED_GPU="4" \
VLLM_SHARED_MODEL="Qwen/Qwen3-1.7B" \
VLLM_SHARED_SERVED_MODEL="Qwen/Qwen3-1.7B" \
VLLM_HOST="127.0.0.1" \
VLLM_SHARED_EXTRA_ARGS="--gpu-memory-utilization 0.4" \
./deploy/vllm/run-replica-set.sh shared-a100-small
```

Implication: both workers contend for the same GPU scheduler, memory bandwidth,
and KV-cache capacity. This topology is useful for validating gateway behavior
and artifact collection, but it should not be interpreted as clean multi-worker
capacity scaling. Record the observed per-worker VRAM split for each run.

### Multi A100 Qwen3 8B

`multi-a100-qwen3-8b` starts two `Qwen/Qwen3-8B` replicas, one per A100:

```bash
./deploy/vllm/run-replica-set.sh multi-a100-qwen3-8b
```

Defaults:

```text
ports: 8201, 8211
VLLM_MULTI_GPU_1=4
VLLM_MULTI_GPU_2=5
VLLM_MULTI_MODEL=Qwen/Qwen3-8B
VLLM_MULTI_SERVED_MODEL=$VLLM_MULTI_MODEL
VLLM_MULTI_EXTRA_ARGS="--max-model-len 4096 --gpu-memory-utilization 0.85"
```

Useful overrides:

```bash
VLLM_MULTI_GPU_1="4" \
VLLM_MULTI_GPU_2="5" \
VLLM_MULTI_MODEL="Qwen/Qwen3-8B" \
VLLM_MULTI_SERVED_MODEL="Qwen/Qwen3-8B" \
VLLM_HOST="127.0.0.1" \
VLLM_MULTI_EXTRA_ARGS="--max-model-len 4096 --gpu-memory-utilization 0.85" \
./deploy/vllm/run-replica-set.sh multi-a100-qwen3-8b
```

This topology gives stronger routing and load-distribution evidence than the
shared-GPU topology because each backend has more independent capacity.

## Direct Smoke Tests

Run direct backend checks before sending gateway traffic to a worker:

```bash
VLLM_MODEL="Qwen/Qwen3-8B" ./deploy/vllm/smoke-openai.sh
```

The smoke script checks:

- `GET /v1/models`
- `POST /v1/chat/completions` with `stream: false`
- `POST /v1/chat/completions` with `stream: true` when `VLLM_SMOKE_STREAM=1`

Example for a replica-set worker:

```bash
VLLM_HOST="127.0.0.1" \
VLLM_PORT="8101" \
VLLM_SERVED_MODEL_NAME="Qwen/Qwen3-0.6B" \
./deploy/vllm/smoke-openai.sh
```

Streaming smoke check:

```bash
VLLM_HOST="127.0.0.1" \
VLLM_PORT="8101" \
VLLM_SERVED_MODEL_NAME="Qwen/Qwen3-0.6B" \
VLLM_SMOKE_STREAM="1" \
./deploy/vllm/smoke-openai.sh
```

Repeat the smoke command for every configured worker port. Direct smoke-test
failures are backend readiness failures, not gateway routing failures.

Run smoke checks for every worker in a running replica topology:

```bash
./deploy/vllm/smoke-replicas.sh shared-a100-small
```

The replica smoke script starts one `smoke-openai.sh` process per replica in
parallel and prints each worker's captured output after all checks finish. This
is useful after `run-replica-set.sh` reports readiness because it confirms that
all workers can serve chat requests at the same time.

Use the matching topology and the same model or served-model overrides used to
start the replicas:

```bash
VLLM_SHARED_MODEL="Qwen/Qwen3-1.7B" \
VLLM_SHARED_SERVED_MODEL="Qwen/Qwen3-1.7B" \
VLLM_SMOKE_STREAM="1" \
./deploy/vllm/smoke-replicas.sh shared-a100-small
```

## Gateway Compatibility

The packaged gateway config currently expects:

```yaml
models:
  - name: qwen3-8b
    enabled: true
    backend:
      type: vllm
      base_url: http://127.0.0.1:8001
      model: Qwen/Qwen3-8B
```

If you change `VLLM_HOST`, `VLLM_PORT`, or `VLLM_SERVED_MODEL_NAME`, update the
gateway config used for that run. Keep the public alias stable unless the run is
intentionally comparing aliases.

For gateway and Prometheus validation through Docker Compose, use
`deploy/compose/README.md`. A gateway container cannot reach a host vLLM process
that only listens on `127.0.0.1`, so bind vLLM to a private Docker-reachable host
address for Compose runs.

## Provenance To Record

For saved benchmark or experiment artifacts, record:

- GPU model, driver, and visible device mapping from `nvidia-smi`
- `deploy/vllm/pyproject.toml` and `uv.lock` versions used
- `UV_TORCH_BACKEND` value used for lock, sync, and run
- vLLM version and install or sync command
- model ID and served model name
- vLLM bind address and backend URL used by the gateway
- worker IDs, ports, and GPU assignments for replica-set runs
- `CUDA_DEVICE_ORDER` and `CUDA_VISIBLE_DEVICES`
- cache paths such as `HF_HOME` and `VLLM_CACHE_ROOT`
- `VLLM_EXTRA_ARGS` or topology-specific extra args
- whether the benchmark runner was same-host, containerized, or a private
  remote client

Reusable gateway benchmark wrapper usage lives in `benchmarks/README.md`. Keep
raw vLLM startup logs, benchmark JSON, stdout/stderr captures, and metrics
snapshots under the matching `experiments/` folder.

## Multi-Node Notes

When multi-node replicas are introduced, assign worker IDs that include the node
name, bind each worker to a routable private interface, and record network path
details in the experiment inventory. Keep the same direct `/v1/models` and
`/v1/chat/completions` checks for every worker before gateway traffic is sent.
