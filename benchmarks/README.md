# Benchmarks

Benchmark commands live here, while saved outputs live under milestone folders
in `experiments/`.

## Milestone 1 Gateway Serving Benchmark

Use `./benchmarks/vllm-gateway-serving.sh` to run `vllm bench serve` from the
pinned `deploy/vllm/` runtime environment against the gateway OpenAI chat
endpoint.

Canonical runbooks:

- Backend setup and direct vLLM smoke tests: `deploy/vllm/README.md`
- Compose gateway and Prometheus stack: `deploy/compose/README.md`
- Milestone interpretation: the relevant `Behind the API` blogpost or
  experiment writeup
- Raw evidence: milestone folders under `experiments/`

The wrapper sets both `--backend openai-chat` and
`--endpoint-type openai-chat`. vLLM `0.9.2` needs both options for the chat
completion request shape; setting only the backend leaves the endpoint type at
the CLI default.

Default command:

```bash
./benchmarks/vllm-gateway-serving.sh
```

Configuration:

| Variable | Default | Meaning |
| --- | --- | --- |
| `GATEWAY_BASE_URL` | `http://127.0.0.1:8000` | Base URL for the gateway being benchmarked. Use `http://127.0.0.1:18000` for the Compose stack when published on the alternate port from `deploy/compose/README.md`. |
| `PUBLIC_MODEL` | `qwen3-8b` | Public model alias sent to the gateway. This must match the gateway registry alias for the run. |
| `TOKENIZER_MODEL` | `Qwen/Qwen3-8B` | Model/tokenizer identifier used by vLLM benchmark tooling to synthesize token-length-controlled prompts. Keep this aligned with the backend model family. |
| `NUM_PROMPTS` | `10` | Number of benchmark requests after vLLM's initial one-request validation. Larger values reduce noise but consume more GPU time. |
| `REQUEST_RATE` | `5` | Target request arrival rate in requests per second. vLLM also accepts `inf` for burst tests; label those separately. |
| `RANDOM_INPUT_LEN` | `128` | Target random prompt length in tokens. This controls prefill work. |
| `RANDOM_OUTPUT_LEN` | `64` | Target generated output length in tokens. This controls decode work. |
| `RANDOM_RANGE_RATIO` | `0.0` | Variation around the requested input and output lengths. Record non-zero values because they change workload interpretation. |
| `TEMPERATURE` | `0` | Sampling temperature sent through the OpenAI-compatible request. |
| `RESULT_DIR` | `experiments/001_vllm_gateway_baseline/4_gateway_serve` | Directory where vLLM benchmark JSON is saved. Keep benchmark output unmodified. |
| `RESULT_FILENAME` | `vllm-gateway-serving.json` | Benchmark JSON filename. Use descriptive names that include path and workload context. |
| `VLLM_PROJECT_DIR` | `deploy/vllm` | Directory containing the pinned vLLM runtime. Override only when intentionally using a different benchmark runtime, and record that as provenance. |

Fixed vLLM benchmark options:

| vLLM option | Value |
| --- | --- |
| `--backend` | `openai-chat` |
| `--endpoint-type` | `openai-chat` |
| `--endpoint` | `/v1/chat/completions` |
| `--dataset-name` | `random` |
| `--save-result` | enabled |
| `--metadata` | gateway/model/runner fields |

Useful overrides:

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=10 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=128 \
RANDOM_OUTPUT_LEN=64 \
RESULT_FILENAME=vllm-gateway-serving-compose-small.json \
./benchmarks/vllm-gateway-serving.sh
```

Tiny smoke run used to validate the command path:

```bash
GATEWAY_BASE_URL=http://127.0.0.1:18000 \
NUM_PROMPTS=1 \
REQUEST_RATE=1 \
RANDOM_INPUT_LEN=16 \
RANDOM_OUTPUT_LEN=8 \
RESULT_FILENAME=vllm-gateway-serving-smoke.json \
./benchmarks/vllm-gateway-serving.sh
```

The default output path is:

```text
experiments/001_vllm_gateway_baseline/4_gateway_serve/vllm-gateway-serving.json
```

Keep result interpretation separate from the benchmark output. The blogpost
or experiment writeup should include the command, environment, workload, result
summary, and interpretation. Raw benchmark JSON, stdout/stderr logs, gateway
metrics, backend-reported token usage, and GPU metrics should stay under
`experiments/` as related evidence streams, not interchangeable measurements.

Interpretation rules:

- `NUM_PROMPTS=1` is only a smoke test for command and endpoint correctness.
- A saved benchmark claim needs enough prompts to reduce noise and should record
  gateway placement, vLLM placement, GPU, model, request rate, and token lengths.
- `REQUEST_RATE`, input length, and output length define the workload. Compare
  runs only when these are intentionally the same or the difference is the
  experiment variable.
- A `commands.md` file may exist during active work, but it is optional. Do not
  rely on it as the only place where a published benchmark command is recorded.
