# Compose Gateway And Metrics

This Compose stack runs only the `tokenkaki.gateway` service and Prometheus.
The vLLM OpenAI-compatible backend remains an external process for Milestone 1.

## Topology

- Gateway container: `http://127.0.0.1:8000`
- Prometheus container: `http://127.0.0.1:9090`
- External vLLM backend from gateway container: `http://host.docker.internal:8001`

On Linux, Compose maps `host.docker.internal` to the Docker host through
`host-gateway`. Keep vLLM bound to loopback or a private interface unless a
later milestone explicitly adds public exposure and auth.

## Run

Start vLLM first from the repository root:

```bash
./deploy/vllm/run-openai-server.sh
```

Then start the gateway and Prometheus stack:

```bash
docker compose -f deploy/compose/compose.yaml up --build
```

## Verify

Check gateway health:

```bash
curl http://127.0.0.1:8000/healthz
```

Check public model aliases:

```bash
curl http://127.0.0.1:8000/v1/models
```

Send one non-streaming request through the gateway:

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -H 'x-request-id: compose-chat-001' \
  -d '{
    "model": "qwen3-0.6b",
    "messages": [
      {"role": "user", "content": "Say hello in one short sentence."}
    ],
    "temperature": 0,
    "max_tokens": 64,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
```

Check gateway metrics directly:

```bash
curl http://127.0.0.1:8000/metrics
```

Open Prometheus at `http://127.0.0.1:9090` and query:

```promql
tokenkaki_gateway_requests_total
tokenkaki_gateway_chat_completions_total
tokenkaki_gateway_backend_tokens_total
```

## Notes

- `deploy/compose/gateway.yaml` is the Compose-specific gateway config.
- If vLLM listens somewhere else, update `backend.base_url` in that file.
- Benchmark results from this stack should still label vLLM as an external
  backend and preserve metric provenance separately from benchmark-observed
  latency.
