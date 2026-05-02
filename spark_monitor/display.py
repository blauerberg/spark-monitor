from __future__ import annotations

from rich.console import Group
from rich.table import Table
from rich.text import Text

from .collectors import CpuStats, GpuProcess, GpuStats, RamStats

_BAR = 24  # bar character width (fallback for None width)
_MAX_METRICS_WIDTH = 66  # max wide format metrics line: "  Usage: 100%  Clock: 2392 MHz  Power: 1000W  Temp: 100°C"
_NARROW_BAR = 40  # fixed bar width below threshold
_THRESHOLD = 75  # terminal width threshold for format switching


def _bar(value: float, total: float = 100.0, width: int = _BAR) -> str:
    filled = round(width * value / total)
    return "█" * filled + "░" * (width - filled)


def _styled_bar(value: float, total: float = 100.0, width: int = _BAR) -> Text:
    pct = value / total * 100
    style = "red" if pct >= 80 else "yellow" if pct >= 50 else "green"
    filled = round(width * value / total)
    t = Text()
    t.append("█" * filled, style=style)
    t.append("░" * (width - filled), style="dim")
    return t


def _gb(n: int) -> str:
    return f"{n / 1000**3:.1f} GB"


def render_cpu(s: CpuStats, width: int | None = None) -> Text:
    if width and width < _THRESHOLD:
        bw = _NARROW_BAR
    else:
        bw = int(width * 0.8) if width else _BAR
    t = Text()
    t.append(" CPU: ", style="bold")
    t.append_text(_styled_bar(s.usage, width=bw))
    t.append("\n")
    temp = f" Temp: {s.temp:.0f}°C" if s.temp is not None else ""
    temp_c = f" {s.temp:.0f}°C" if s.temp is not None else ""
    if width and width < _THRESHOLD:
        t.append(f"        {s.usage:.1f}% {int(s.clock)}MHz N/A{temp_c}\n")
    else:
        t.append(f"        Usage: {s.usage:.1f}%  Clock: {int(s.clock)} MHz  Power: N/A{temp}\n")
    return t


def render_ram(s: RamStats, width: int | None = None) -> Text:
    if width and width < _THRESHOLD:
        b = _NARROW_BAR
    else:
        b = int((width * 0.8) if width else _BAR)
    pct = s.used / s.total * 100
    used_gb = s.used / 1e9
    total_gb = s.total / 1e9
    t = Text()
    t.append(" RAM: ", style="bold")
    t.append_text(_styled_bar(s.used, s.total, b))
    t.append("\n")
    if width and width < _THRESHOLD:
        t.append(f"        {used_gb:.1f}/{total_gb:.1f} GB ({pct:.0f}%)\n")
    else:
        t.append(f"        Usage: {used_gb:.1f}/{total_gb:.1f} GB ({pct:.0f}%)\n")
    return t


def render_gpu(s: GpuStats, width: int | None = None) -> Text:
    if width and width < _THRESHOLD:
        bw = _NARROW_BAR
    else:
        bw = int(width * 0.8) if width else _BAR
    t = Text()
    t.append(" GPU: ", style="bold")
    t.append_text(_styled_bar(s.usage, width=bw))
    t.append("\n")
    if width and width < _THRESHOLD:
        t.append(f"        {s.usage:.1f}% {int(s.clock)}MHz {s.power:.0f}W {s.temp}°C\n")
    else:
        t.append(f"        Usage: {s.usage:.1f}%  Clock: {int(s.clock)} MHz  Power: {s.power:.0f}W  Temp: {s.temp}°C\n")
    return t


def render_processes(procs: list[GpuProcess]) -> Group | None:
    if not procs:
        return None
    table = Table(show_header=True, box=None, padding=(0, 1))
    table.add_column("PID", style="cyan", no_wrap=True)
    table.add_column("Type", no_wrap=True)
    table.add_column("User", style="green")
    table.add_column("Mem", style="yellow")
    table.add_column("Command")
    for p in procs:
        type_style = "magenta" if p.type == "G" else "blue"
        type_cell = f"[{type_style}]{p.type}[/{type_style}]"
        table.add_row(str(p.pid), type_cell, p.user, _gb(p.mem_bytes), p.command)
    header = Text(" GPU Processes:", style="bold")
    return Group(header, table)


def render_statusline(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
    _BAR_HORIZONTAL = 8
    pct_ram = ram.used / ram.total * 100
    b = _BAR_HORIZONTAL
    temp_cpu = f" {cpu.temp:.0f}°C" if cpu.temp is not None else ""
    t = Text()
    t.append("CPU", style="bold cyan")
    t.append("")
    t.append_text(_styled_bar(cpu.usage, width=b))
    t.append(f" {cpu.usage:4.0f}%{temp_cpu} ")
    t.append("RAM", style="bold green")
    t.append("")
    t.append_text(_styled_bar(ram.used, ram.total, b))
    t.append(f" {pct_ram:4.0f}% ")
    t.append("GPU", style="bold yellow")
    t.append("")
    t.append_text(_styled_bar(gpu.usage, width=b))
    t.append(f" {gpu.usage:4.0f}% {gpu.temp}°C {gpu.power:.0f}W")
    return t


def render_all(
    cpu: CpuStats,
    ram: RamStats,
    gpu: GpuStats,
    procs: list[GpuProcess],
    width: int | None = None,
) -> Group:
    t = Text("\n")
    t.append_text(render_cpu(cpu, width=width))
    t.append_text(render_ram(ram, width=width))
    t.append_text(render_gpu(gpu, width=width))
    proc_section = render_processes(procs)
    sections: list = [t]
    if proc_section:
        sections.append(proc_section)
    return Group(*sections)
