from spark_monitor.collectors import CpuStats, GpuStats, RamStats
from spark_monitor.display import render_compact_vertical

_GIB = 1024 ** 3
_CPU = CpuStats(usage=45.0, clock=2000.0, temp=52.0)
_RAM = RamStats(used=32 * _GIB, total=64 * _GIB)
_GPU = GpuStats(usage=89.0, clock=1500, temp=67, power=250.0)


def test_render_compact_vertical_has_three_lines():
    text = render_compact_vertical(_CPU, _RAM, _GPU)
    lines = [l for l in text.plain.splitlines() if l]
    assert len(lines) == 3


def test_render_compact_vertical_contains_labels():
    text = render_compact_vertical(_CPU, _RAM, _GPU)
    plain = text.plain
    assert "CPU" in plain
    assert "RAM" in plain
    assert "GPU" in plain
