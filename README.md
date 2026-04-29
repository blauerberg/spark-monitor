# Spark Monitor

A minimal CLI for monitoring DGX Spark resource usage. Displays only the essential metrics, simply.

Three display modes are available:

**Default** — full metrics with process list

![Screenshot](images/screenshot.png)

**`--compact-vertical`** — minimal 3-line layout

![Screenshot (compact-vertical)](images/screenshot-vertical.png)

**`--compact-horizontal`** — single-line layout

![Screenshot (compact-horizontal)](images/screenshot-horizontal.png)

## Quick Start

Run directly without installing:

```bash
uvx --from git+https://github.com/blauerberg/spark-monitor spark-monitor
```

Or install as a persistent command:

```bash
uv tool install git+https://github.com/blauerberg/spark-monitor
spark-monitor
```

To upgrade:

```bash
uv tool upgrade spark-monitor
```

## Usage

```bash
# Default (full metrics, 1-second refresh)
spark-monitor

# Compact 3-line layout
spark-monitor --compact-vertical

# Single-line layout
spark-monitor --compact-horizontal

# Custom refresh interval
spark-monitor --interval 0.5
```

Press `Ctrl+C` to exit.

## tmux statusline integration

`--statusline` prints a single line to stdout and exits immediately, making it suitable for embedding in the tmux status bar.

```bash
spark-monitor --statusline
```

Add to `~/.tmux.conf`:

```
set -g status-right '#(spark-monitor --statusline)'
set -g status-interval 5
```

`status-interval` controls how often tmux re-runs the command (in seconds). CPU usage is measured over a 0.5-second window on each invocation, so setting it below `2` is not recommended.

## Installation from source

```bash
git clone https://github.com/blauerberg/spark-monitor.git
cd spark-monitor
uv sync
uv run spark-monitor
```

## Display

- **CPU**: usage (bar), clock, temperature, power (N/A)
  - Power is always N/A. The current driver does not expose Grace CPU power.
- **RAM**: usage (bar)
- **GPU**: usage (bar), clock, temperature, power
- **GPU Processes**: processes using the GPU (hidden when none, default mode only)
