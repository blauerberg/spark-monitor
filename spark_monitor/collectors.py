from __future__ import annotations

import pwd
from dataclasses import dataclass
from pathlib import Path

import psutil
import pynvml


@dataclass
class CpuStats:
    usage: float  # %
    clock: float | None  # MHz
    temp: float | None  # °C
    # No power field: Grace CPU power is not exposed by the current driver.
    # Investigated: tegrastats (not installed), hwmon/powercap (no sensors),
    # nvmlDeviceGetTotalEnergyConsumption (GPU-only, confirmed by delta test),
    # module.power.draw.average (returns N/A in nvidia-smi).
    # If a future driver enables module.power.draw.average, it can be read via
    # nvidia-smi --query-gpu=module.power.draw.average --format=csv,noheader,nounits


@dataclass
class RamStats:
    used: int  # bytes
    total: int  # bytes


@dataclass
class GpuStats:
    usage: float  # %
    clock: int  # MHz
    temp: int  # °C
    power: float  # W


@dataclass
class GpuProcess:
    pid: int
    user: str
    mem_bytes: int
    command: str


def _cpu_temp() -> float | None:
    temps = psutil.sensors_temperatures()
    # DGX Spark (Grace/ARM) exposes thermals under various keys
    for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz", "arm-soc"):
        if key in temps and temps[key]:
            return temps[key][0].current
    for entries in temps.values():
        if entries:
            return entries[0].current
    return None


def _proc_user(pid: int) -> str:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("Uid:"):
                uid = int(line.split()[1])
                return pwd.getpwuid(uid).pw_name
    except Exception:
        pass
    return "?"


def _proc_command(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip()
    except Exception:
        return "?"


def collect() -> tuple[CpuStats, RamStats, GpuStats, list[GpuProcess]]:
    # CPU
    freq = psutil.cpu_freq()
    cpu = CpuStats(
        usage=psutil.cpu_percent(interval=None),
        clock=freq.current if freq else None,
        temp=_cpu_temp(),
    )

    # RAM
    mem = psutil.virtual_memory()
    ram = RamStats(used=mem.used, total=mem.total)

    # GPU (index 0 — DGX Spark has a single GB10 GPU)
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    gpu = GpuStats(
        usage=float(util.gpu),
        clock=pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS),
        temp=pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU),
        power=pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0,  # mW → W
    )

    # GPU processes
    procs = [
        GpuProcess(
            pid=p.pid,
            user=_proc_user(p.pid),
            mem_bytes=p.usedGpuMemory,
            command=_proc_command(p.pid),
        )
        for p in pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
    ]

    return cpu, ram, gpu, procs
