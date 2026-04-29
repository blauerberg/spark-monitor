from spark_monitor.collectors import CpuStats, GpuStats, RamStats
from spark_monitor.display import render_compact_horizontal, render_compact_vertical

_GIB = 1024 ** 3
_CPU = CpuStats(usage=45.0, clock=2000.0, temp=52.0)
_RAM = RamStats(used=32 * _GIB, total=64 * _GIB)
_GPU = GpuStats(usage=89.0, clock=1500, temp=67, power=250.0)


def test_render_compact_vertical_has_three_lines():
    text = render_compact_vertical(_CPU, _RAM, _GPU)
    lines = [line for line in text.plain.splitlines() if line]
    assert len(lines) == 3


def test_render_compact_vertical_contains_labels():
    text = render_compact_vertical(_CPU, _RAM, _GPU)
    plain = text.plain
    assert "CPU" in plain
    assert "RAM" in plain
    assert "GPU" in plain


_CPU_NO_TEMP = CpuStats(usage=45.0, clock=2000.0, temp=None)


def test_render_compact_horizontal_is_single_line():
    text = render_compact_horizontal(_CPU, _RAM, _GPU)
    plain = text.plain.strip()
    assert "\n" not in plain


def test_render_compact_horizontal_contains_all_metrics():
    text = render_compact_horizontal(_CPU, _RAM, _GPU)
    plain = text.plain
    assert "CPU" in plain
    assert "RAM" in plain
    assert "GPU" in plain
    assert "52" in plain   # CPU temp
    assert "67" in plain   # GPU temp
    assert "250" in plain  # GPU power


def test_render_compact_horizontal_omits_cpu_temp_when_none():
    text = render_compact_horizontal(_CPU_NO_TEMP, _RAM, _GPU)
    plain = text.plain
    assert "CPU" in plain
    assert "67" in plain   # GPU temp still shown
