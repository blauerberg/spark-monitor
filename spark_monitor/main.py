from __future__ import annotations

import argparse
import enum
import time

import psutil
import pynvml
from rich.console import Console
from rich.live import Live

from .collectors import collect
from .display import render_all, render_statusline


class DisplayMode(enum.Enum):
    FULL = "full"
    STATUSLINE = "statusline"


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DGX Spark resource monitor")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Refresh interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--statusline",
        action="store_true",
        help="Print a single line for use in tmux statusline, then exit",
    )
    return parser


def main() -> None:
    args = _make_parser().parse_args()

    if args.statusline:
        mode = DisplayMode.STATUSLINE
    else:
        mode = DisplayMode.FULL

    pynvml.nvmlInit()
    try:
        if mode is DisplayMode.STATUSLINE:
            # Each invocation is a fresh process, so use a blocking interval
            # for an accurate CPU reading instead of the primer+loop approach.
            cpu, ram, gpu, _ = collect(cpu_interval=0.5)
            Console(highlight=False).print(render_statusline(cpu, ram, gpu))
            return

        # Prime psutil so the first cpu_percent() call in the loop returns a real value
        psutil.cpu_percent(interval=None)

        with Live(auto_refresh=False, screen=True) as live:
            while True:
                cpu, ram, gpu, procs = collect()
                width = Console(force_terminal=True).width
                live.update(render_all(cpu, ram, gpu, procs, width=width))
                live.refresh()
                time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        pynvml.nvmlShutdown()


if __name__ == "__main__":
    main()
