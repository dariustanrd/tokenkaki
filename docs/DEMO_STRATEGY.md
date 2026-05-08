# Demo Strategy

The demo strategy is realism-first and cost-controlled.

The project should end with a deployable OpenAI-compatible inference endpoint
that can be shown, tested, and reproduced. Public access should demonstrate the
real endpoint shape and measured behavior without exposing unlimited live GPU
capacity.

## Demo Modes

- **Public limited mode**: small number of live calls, cheap model, strict rate
  limits, or replay responses.
- **Authenticated live mode**: real vLLM-backed access for trusted users with
  quotas and monitoring.
- **Benchmark mode**: scripted load tests against controlled infrastructure.
- **Replay/report mode**: published benchmark artifacts for expensive or
  short-lived experiments.

## Cost Controls

Every live GPU deployment should have:

- authentication for real-model access
- per-user and global quotas
- request rate limits
- maximum input and output token limits
- spend or runtime budget
- observable usage metrics
- kill switch
- teardown instructions

## Public Surface

The public surface should include:

- endpoint documentation
- example requests
- current or last-known benchmark results
- deployment notes for replication
- clear labeling for live, replay, and offline experiment modes

The goal is to make the system easy to inspect and reproduce while keeping live
inference capacity bounded.
