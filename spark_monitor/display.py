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
    if width is not None and width >= 80:
        return _render_cpu_compact(s)
    return _render_cpu_full(s)


def _render_cpu_full(s: CpuStats) -> Text:
    clock = f"{s.clock / 1000:.2f} GHz" if s.clock else "N/A"
    temp = f"{s.temp:.0f}°C" if s.temp is not None else "N/A"
    t = Text()
    t.append("CPU:\n", style="bold")
    t.append(" ")
    t.append_text(_styled_bar(s.usage))
    t.append(f" {s.usage:5.1f}%  Clock: {clock}\n")
    t.append(f"  {'':>{_BAR}}  Temp: {temp}  Power: N/A")
    return t


def _render_cpu_compact(s: CpuStats) -> Text:
    temp = f" {s.temp:.0f}°C" if s.temp is not None else ""
    t = Text()
    t.append("CPU:\n", style="bold")
    t.append(" ")
    t.append_text(_styled_bar(s.usage, width=_BAR_COMPACT))
    t.append(f" {s.usage:4.0f}%{temp}")
    return t


def render_ram(s: RamStats, width: int | None = None) -> Text:
    b = _BAR_COMPACT if (width is not None and width >= 80) else _BAR
    pct = s.used / s.total * 100
    t = Text()
    t.append("RAM:\n", style="bold")
    t.append(" ")
    t.append_text(_styled_bar(s.used, s.total, b))
    t.append(f" {_gb(s.used)}/{_gb(s.total)} ({pct:.0f}%)")
    return t


def render_gpu(s: GpuStats, width: int | None = None) -> Text:
    if width is not None and width >= 80:
        return _render_gpu_compact(s)
    return _render_gpu_full(s)


def _render_gpu_full(s: GpuStats) -> Text:
    t = Text()
    t.append("GPU:\n", style="bold")
    t.append(" ")
    t.append_text(_styled_bar(s.usage))
    t.append(f" {s.usage:5.1f}%  Clock: {s.clock} MHz\n")
    t.append(f"  {'':>{_BAR}}  Temp: {s.temp}°C  Power: {s.power:.0f}W")
    return t


def _render_gpu_compact(s: GpuStats) -> Text:
    t = Text()
    t.append("GPU:\n", style="bold")
    t.append(" ")
    t.append_text(_styled_bar(s.usage, width=_BAR_COMPACT))
    t.append(f" {s.usage:4.0f}% {s.temp}°C {s.power:.0f}W")
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
    header = Text("GPU Processes:", style="bold")
    return Group(header, table)


def render_compact_vertical(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
    temp_cpu = f" {cpu.temp:.0f}°C" if cpu.temp is not None else ""
    temp_gpu = f" {gpu.temp}°C"
    pct_ram = ram.used / ram.total * 100
    b = _BAR_COMPACT
    t = Text()
    t.append("\n")
    t.append(" CPU", style="bold cyan")
    t.append(" ")
    t.append_text(_styled_bar(cpu.usage, width=b))
    t.append(f" {cpu.usage:4.0f}%{temp_cpu}\n")
    t.append(" RAM", style="bold green")
    t.append(" ")
    t.append_text(_styled_bar(ram.used, ram.total, b))
    t.append(f" {pct_ram:4.0f}%\n")
    t.append(" GPU", style="bold yellow")
    t.append(" ")
    t.append_text(_styled_bar(gpu.usage, width=b))
    t.append(f" {gpu.usage:4.0f}%{temp_gpu} {gpu.power:.0f}W\n")
    return t


def render_compact_horizontal(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
    pct_ram = ram.used / ram.total * 100
    b = _BAR_HORIZONTAL
    temp_cpu = f" {cpu.temp:.0f}°C" if cpu.temp is not None else ""
    t = Text()
    t.append("\n")
    t.append(" CPU", style="bold cyan")
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
    t.append(f" {gpu.usage:4.0f}% {gpu.temp}°C {gpu.power:.0f}W\n")
    return t


def render_statusline(cpu: CpuStats, ram: RamStats, gpu: GpuStats) -> Text:
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
    sections: list = [
        render_cpu(cpu, width=width),
        render_ram(ram, width=width),
        render_gpu(gpu, width=width),
    ]
    proc_section = render_processes(procs)
    if proc_section:
        sections.append(proc_section)
    return Group(*sections)
