# Spark Monitor

A minimal CLI for monitoring DGX Spark resource usage. Displays only the essential metrics, simply.

## Installation

```bash
uv sync
```

## Usage

```bash
# Default (1-second refresh)
uv run spark-monitor

# Custom refresh interval
uv run spark-monitor --interval 0.5
```

Press `Ctrl+C` to exit.

## Display

- **CPU**: usage (bar), clock, temperature, power (N/A)
  - Power is always N/A. The current driver does not expose Grace CPU power.
    Investigated: tegrastats (not installed), hwmon/powercap (no sensors),
    `nvmlDeviceGetTotalEnergyConsumption` (GPU-only), `module.power.draw.average` (N/A in nvidia-smi).
    A future driver update enabling `module.power.draw.average` would make this available.
- **RAM**: usage (bar)
- **GPU**: usage (bar), clock, temperature, power
- **GPU Processes**: processes using the GPU (hidden when none)
