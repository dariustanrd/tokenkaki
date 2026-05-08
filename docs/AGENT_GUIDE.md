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

## Stage Rules

Every stage should produce:

- runnable code or deployment artifact
- reproducible benchmark command
- saved result artifact
- writeup-ready interpretation

When adding a feature, also consider whether the docs, benchmark scripts, or
experiment templates need to change.

## Documentation Rules

- Keep public docs focused on technical learning and measurable systems work.
- Absolutely avoid calling mock-worker results real serving results.
- Prefer explicit metrics and reproducible commands over broad claims.
