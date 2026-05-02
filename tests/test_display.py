from rich.console import Console

from spark_monitor.collectors import CpuStats, GpuStats, RamStats
from spark_monitor.display import (
    render_all,
    render_cpu,
    render_gpu,
    render_ram,
    render_statusline,
)

_GIB = 1024**3
_CPU = CpuStats(usage=45.0, clock=2000.0, temp=52.0)
_RAM = RamStats(used=32 * _GIB, total=64 * _GIB)
_GPU = GpuStats(usage=89.0, clock=1500, temp=67, power=250.0)


def test_render_cpu_has_two_lines():
    text = render_cpu(_CPU, width=100)
    lines = [line for line in text.plain.splitlines() if line]
    assert len(lines) == 2


def test_render_cpu_contains_metrics():
    text = render_cpu(_CPU, width=100)
    plain = text.plain
    assert "CPU" in plain
    assert "45.0%" in plain
    assert "2000 MHz" in plain
    assert "Power: N/A" in plain
    assert "Temp: 52°C" in plain


def test_render_ram_has_two_lines():
    text = render_ram(_RAM, width=100)
    lines = [line for line in text.plain.splitlines() if line]
    assert len(lines) == 2


def test_render_ram_contains_metrics():
    text = render_ram(_RAM, width=100)
    plain = text.plain
    assert "RAM" in plain
    assert "Usage:" in plain
    assert "GB" in plain
    assert "%" in plain


def test_render_gpu_has_two_lines():
    text = render_gpu(_GPU, width=100)
    lines = [line for line in text.plain.splitlines() if line]
    assert len(lines) == 2


def test_render_gpu_contains_metrics():
    text = render_gpu(_GPU, width=100)
    plain = text.plain
    assert "GPU" in plain
    assert "89.0%" in plain
    assert "1500 MHz" in plain
    assert "Power: 250W" in plain
    assert "Temp: 67°C" in plain


def test_render_statusline_is_single_line_no_margins():
    text = render_statusline(_CPU, _RAM, _GPU)
    plain = text.plain
    assert "\n" not in plain
    assert not plain.startswith(" ")


def test_render_statusline_contains_all_metrics():
    text = render_statusline(_CPU, _RAM, _GPU)
    plain = text.plain
    assert "CPU" in plain
    assert "RAM" in plain
    assert "GPU" in plain
    assert "52" in plain  # CPU temp
    assert "67" in plain  # GPU temp
    assert "250" in plain  # GPU power


def test_render_all_has_leading_blank_line():
    console = Console(record=True, width=120)
    console.print(render_all(_CPU, _RAM, _GPU, [], width=100))
    plain = console.export_text()
    assert plain.startswith("\n")


def test_render_all_bar_width_is_80_percent():
    console = Console(record=True, width=100)
    console.print(render_all(_CPU, _RAM, _GPU, [], width=100))
    plain = console.export_text()
    # Bar width should be int(100 * 0.8) = 80 characters
    # Find the bar line (contains █ or ░)
    for line in plain.splitlines():
        if "█" in line or "░" in line:
            bar_part = "".join(c for c in line if c in ("█", "░"))
            assert len(bar_part) == 80
            break


def test_render_all_uses_80_percent_bar():
    text_wide = render_cpu(_CPU, width=200)
    text_narrow = render_cpu(_CPU, width=50)
    # Extract bar widths
    wide_bar = "".join(c for c in text_wide.plain if c in ("█", "░"))
    narrow_bar = "".join(c for c in text_narrow.plain if c in ("█", "░"))
    assert len(wide_bar) == 160  # int(200 * 0.8)
    assert len(narrow_bar) == 40  # int(50 * 0.8)


def test_render_cpu_compact_format():
    text = render_cpu(_CPU, width=60)
    plain = text.plain
    assert "Usage:" not in plain
    assert "Clock:" not in plain
    assert "Power:" not in plain
    assert "Temp:" not in plain
    assert "45.0%" in plain
    assert "2000MHz" in plain


def test_render_gpu_compact_format():
    text = render_gpu(_GPU, width=60)
    plain = text.plain
    assert "Usage:" not in plain
    assert "Clock:" not in plain
    assert "Power:" not in plain
    assert "Temp:" not in plain
    assert "89.0%" in plain
    assert "1500MHz" in plain


def test_render_ram_compact_format():
    text = render_ram(_RAM, width=60)
    plain = text.plain
    assert "Usage:" not in plain
    assert "GB" in plain
    assert "%" in plain
