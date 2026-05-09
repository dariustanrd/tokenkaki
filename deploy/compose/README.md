# Compose Gateway And Metrics

This Compose stack runs only the `tokenkaki.gateway` service and Prometheus.
The vLLM OpenAI-compatible backend remains an external process for Milestone 1.

## Topology

- Gateway container: `http://127.0.0.1:8000`
- Prometheus container: `http://127.0.0.1:9090`
- External vLLM backend from gateway container: `http://host.docker.internal:8001`

On Linux, Compose maps `host.docker.internal` to the Docker host through
`host-gateway`.

Important: a bridge-network container cannot reach a host process that is bound
only to `127.0.0.1`. For end-to-end chat validation through this Compose stack,
start vLLM on a private host interface reachable from Docker, such as the
Docker bridge address, and keep it off public interfaces unless a later
milestone explicitly adds public exposure and auth.

## Run

Start vLLM first from the repository root:

```bash
./deploy/vllm/run-openai-server.sh
```

If validating the Compose gateway against vLLM, bind vLLM to a private
Docker-reachable host address instead of loopback. On many Linux hosts this is
the `docker0` address:

```bash
ip -4 addr show docker0
VLLM_HOST=<docker0-address> ./deploy/vllm/run-openai-server.sh
```

This was validated on the Milestone 1 GPU host with:

```bash
VLLM_HOST=172.17.0.1 ./deploy/vllm/run-openai-server.sh
```

Then start the gateway and Prometheus stack:

```bash
docker compose -f deploy/compose/compose.yaml up --build
```

If `8000` or `9090` is already in use on the host, publish the containers on
alternate host ports:

```bash
TOKENKAKI_GATEWAY_PORT=18000 TOKENKAKI_PROMETHEUS_PORT=19090 \
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

On the Milestone 1 GPU host, the same request was validated through the Compose
gateway published on alternate host port `18000` while vLLM was bound to
`172.17.0.1:8001`.

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
- If vLLM listens somewhere else, update `backend.base_url` in that file. The
  default `http://host.docker.internal:8001` assumes Docker can reach vLLM on
  the host gateway address.
- Benchmark results from this stack should still label vLLM as an external
  backend and preserve metric provenance separately from benchmark-observed
  latency.
