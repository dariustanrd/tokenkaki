# Milestone 1 vLLM Gateway Baseline

This folder stores reproducible artifacts for the Milestone 1 gateway baseline.

## Layout

- `commands.md`: exact commands used for setup, serving, benchmark runs, and
  metrics capture.
- `configs/`: copied gateway, vLLM, Compose, Prometheus, and benchmark config
  used for saved runs.
- `raw/`: unmodified benchmark JSON, logs, and metrics snapshots.
- `plots/`: generated charts derived from raw artifacts.
- `report.md`: writeup-ready interpretation of the saved evidence.

## Provenance

Every saved run should record:

- benchmark runner placement
- gateway placement and config
- vLLM placement, bind address, model, and launch flags
- network path between runner, gateway, and backend
- raw benchmark command
- gateway metrics snapshot timing
- whether results are same-host baseline or a labeled non-baseline path
