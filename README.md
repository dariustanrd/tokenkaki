# tokenkaki

`tokenkaki` is a staged, runnable LLM inference platform for learning, building,
and measuring realistic OpenAI-compatible serving systems.

The project focuses on the full serving path: API gateway, routing and
scheduling, real vLLM/SGLang backends, observability, benchmarks, deployment,
and experiment writeups. Each stage should produce runnable code, reproducible
benchmark artifacts, saved results, and a technical interpretation of what the
measurements mean.

## Goals

- Build a real OpenAI-compatible inference endpoint.
- Use real backends as the normal serving path, starting with vLLM.
- Keep mock workers isolated as test and benchmark utilities only.
- Measure TTFT, TPOT, latency, throughput, errors, token counts, backend choice,
  and GPU metrics where available.
- Progress from a single measured backend to routing, tuning, quantization,
  Kubernetes, multi-GPU, multi-node, cache-aware routing, and disaggregated
  serving studies.
- Keep expensive live demos cost-controlled with auth, quotas, rate limits,
  replay mode, and clear teardown paths.

## Documentation

- [Vision](docs/VISION.md): project purpose, learning objective, and principles.
- [Architecture](docs/ARCHITECTURE.md): serving path, components, backend rules,
  and demo posture.
- [Roadmap](docs/ROADMAP.md): staged milestones and expected outputs.
- [Experiments](docs/EXPERIMENTS.md): stage definition of done, metrics, and
  report template.
- [Demo Strategy](docs/DEMO_STRATEGY.md): public and authenticated demo modes
  with cost controls.
