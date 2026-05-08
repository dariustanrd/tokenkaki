# Agent Guide

This guide defines implementation constraints for future work on `tokenkaki`.

## Project Direction

Build a staged, runnable LLM inference platform for learning and measuring
realistic OpenAI-compatible serving systems. Prefer changes that improve the
request path, backend integration, routing, observability, benchmarking,
deployment realism, or experiment quality.

## Serving Code Rules

- Real backend clients are the default serving path.
- vLLM is the first backend target.
- SGLang comes after the vLLM path is measurable.
- Mock workers are test and benchmark utilities only.
- Do not entangle mock-worker behavior with real backend clients.
- Label synthetic results clearly.
- Do not make mock workers the default for public docs, demos, or benchmark
  claims.
- When a model name, serving feature, or hardware requirement is phase-specific,
  verify it before implementation instead of assuming the roadmap entry is still
  current.

## Stage Rules

Every stage should produce:

- runnable code or deployment artifact
- reproducible benchmark command
- saved result artifact
- writeup-ready interpretation

When adding a feature, also consider whether the docs, benchmark scripts, or
experiment templates need to change.

## Benchmark Rules

- Use vLLM benchmarks for raw model-serving performance.
- Use NVIDIA GenAI-Perf for OpenAI-compatible endpoint behavior.
- Use Locust for product/API behavior such as concurrent users, auth, quotas,
  rate limits, and gateway overhead.
- Use Prometheus, Grafana, and DCGM Exporter to correlate request metrics with
  GPU/system metrics.
- Use `llm-d-benchmark` only for advanced distributed serving phases where the
  infrastructure supports it.

## Documentation Rules

- Keep public docs focused on technical learning and measurable systems work.
- Absolutely avoid calling mock-worker results real serving results.
- Prefer explicit metrics and reproducible commands over broad claims.
- The first blog post is the project intro and motivation post in the
  `Behind the API` series. It should explain what will be built, why it matters
  for inference optimization/platform roles, the staged plan, and the benchmark
  evidence expected from later posts.
