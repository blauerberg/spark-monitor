from __future__ import annotations

from rich.console import Group
from rich.table import Table
from rich.text import Text

from .collectors import CpuStats, GpuProcess, GpuStats, RamStats

_BAR = 24  # bar character width
_BAR_COMPACT = 16
_BAR_HORIZONTAL = 8


def _bar(value: float, total: float = 100.0, width: int = _BAR) -> str:
    filled = round(width * value / total)
    return "█" * filled + "░" * (width - filled)


def _gib(n: int) -> str:
    return f"{n / 1024**3:.1f} GiB"


def _section(title: str, *lines: str) -> Text:
    t = Text()
    t.append(f"{title}:\n", style="bold")
    for line in lines:
        t.append(f"  {line}\n")
    return t


def render_cpu(s: CpuStats) -> Text:
    clock = f"{s.clock / 1000:.2f} GHz" if s.clock else "N/A"
    temp = f"{s.temp:.0f}°C" if s.temp is not None else "N/A"
    line1 = f"{_bar(s.usage)}  {s.usage:5.1f}%   Clock: {clock}"
    line2 = f"{'':>{_BAR}}  Temp:  {temp:<9}  Power: N/A"
    return _section("CPU", line1, line2)


def render_ram(s: RamStats) -> Text:
    pct = s.used / s.total * 100
    line = f"{_bar(s.used, s.total)}  {_gib(s.used)} / {_gib(s.total)} ({pct:.0f}%)"
    return _section("RAM", line)


def render_gpu(s: GpuStats) -> Text:
    line1 = f"{_bar(s.usage)}  {s.usage:5.1f}%   Clock: {s.clock} MHz"
    line2 = f"{'':>{_BAR}}  Temp:  {s.temp}°C       Power: {s.power:.0f}W"
    return _section("GPU", line1, line2)


def render_processes(procs: list[GpuProcess]) -> Group | None:
    if not procs:
        return None
    table = Table(show_header=True, box=None, padding=(0, 1))
    table.add_column("PID", style="cyan", no_wrap=True)
    table.add_column("User", style="green")
    table.add_column("Mem", style="yellow")
    table.add_column("Command")
    for p in procs:
        table.add_row(str(p.pid), p.user, _gib(p.mem_bytes), p.command)
    header = Text("GPU Processes:\n", style="bold")
    return Group(header, table)


def render_compact_vertical(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
    temp_cpu = f"  {cpu.temp:.0f}°C" if cpu.temp is not None else ""
    temp_gpu = f"  {gpu.temp}°C"
    pct_ram = ram.used / ram.total * 100
    b = _BAR_COMPACT
    t = Text()
    t.append("\n")
    t.append(f"  CPU  {_bar(cpu.usage, width=b)}  {cpu.usage:4.0f}%{temp_cpu}\n")
    t.append(f"  RAM  {_bar(ram.used, ram.total, b)}  {pct_ram:4.0f}%\n")
    bar_gpu = _bar(gpu.usage, width=b)
    t.append(f"  GPU  {bar_gpu}  {gpu.usage:4.0f}%{temp_gpu}  {gpu.power:.0f}W\n")
    return t


def render_compact_horizontal(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
    pct_ram = ram.used / ram.total * 100
    b = _BAR_HORIZONTAL
    temp_cpu = f"  {cpu.temp:.0f}°C" if cpu.temp is not None else ""
    t = Text()
    t.append("\n")
    t.append(f"  CPU {_bar(cpu.usage, width=b)}  {cpu.usage:4.0f}%{temp_cpu}    ")
    t.append(f"RAM {_bar(ram.used, ram.total, b)}  {pct_ram:4.0f}%    ")
    bar_gpu = _bar(gpu.usage, width=b)
    t.append(f"GPU {bar_gpu}  {gpu.usage:4.0f}%  {gpu.temp}°C  {gpu.power:.0f}W\n")
    return t


def render_all(
    cpu: CpuStats,
    ram: RamStats,
    gpu: GpuStats,
    procs: list[GpuProcess],
) -> Group:
    sections: list = [render_cpu(cpu), render_ram(ram), render_gpu(gpu)]
    proc_section = render_processes(procs)
    if proc_section:
        sections.append(proc_section)
    return Group(*sections)
