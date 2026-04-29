from __future__ import annotations

import argparse
import time

import psutil
import pynvml
from rich.live import Live

from .collectors import collect
from .display import render_all, render_compact


def main() -> None:
    parser = argparse.ArgumentParser(description="DGX Spark resource monitor")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Refresh interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Show minimal metrics in a compact 3-line layout",
    )
    args = parser.parse_args()

    pynvml.nvmlInit()
    # Prime psutil so the first cpu_percent() call returns a real value
    psutil.cpu_percent(interval=None)

    try:
        with Live(auto_refresh=False, screen=True) as live:
            while True:
                cpu, ram, gpu, procs = collect()
                if args.compact:
                    live.update(render_compact(cpu, ram, gpu))
                else:
                    live.update(render_all(cpu, ram, gpu, procs))
                live.refresh()
                time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        pynvml.nvmlShutdown()


if __name__ == "__main__":
    main()
