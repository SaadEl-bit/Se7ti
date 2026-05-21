"""
FieldScreen AI v2 — Hardware & Software Compatibility Checker
Checks if this machine can run torch and TrOCR (microsoft/trocr-base-printed).
"""

import sys
import os
import platform
import multiprocessing
import shutil
import time


# ── Terminal colours (work on Windows 10+ and Linux) ───────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"

def ok(msg: str)   -> str: return f"{GREEN}  [OK]{RESET}  {msg}"
def warn(msg: str) -> str: return f"{YELLOW}  [!!]{RESET}  {msg}"
def fail(msg: str) -> str: return f"{RED}  [KO]{RESET}  {msg}"
def info(msg: str) -> str: return f"{CYAN}  [--]{RESET}  {msg}"
def section(title: str) -> None:
    print(f"\n{BOLD}{WHITE}{'-' * 55}{RESET}")
    print(f"{BOLD}{WHITE}  {title}{RESET}")
    print(f"{BOLD}{WHITE}{'-' * 55}{RESET}")


# ── System helpers ──────────────────────────────────────────────────────────

def get_ram_gb() -> tuple[float, float]:
    """Return (total_gb, available_gb). Cross-platform."""
    try:
        if platform.system() == "Windows":
            import ctypes

            class _MEMSTATEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength",                 ctypes.c_ulong),
                    ("dwMemoryLoad",             ctypes.c_ulong),
                    ("ullTotalPhys",             ctypes.c_ulonglong),
                    ("ullAvailPhys",             ctypes.c_ulonglong),
                    ("ullTotalPageFile",         ctypes.c_ulonglong),
                    ("ullAvailPageFile",         ctypes.c_ulonglong),
                    ("ullTotalVirtual",          ctypes.c_ulonglong),
                    ("ullAvailVirtual",          ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = _MEMSTATEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            gb = 1024 ** 3
            return stat.ullTotalPhys / gb, stat.ullAvailPhys / gb

        # Linux / WSL
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        total_kb     = int(next(l for l in lines if l.startswith("MemTotal")).split()[1])
        available_kb = int(next(l for l in lines if l.startswith("MemAvailable")).split()[1])
        return total_kb / (1024 ** 2), available_kb / (1024 ** 2)

    except Exception:
        return 0.0, 0.0


def get_cpu_freq_ghz() -> float | None:
    """Return max CPU frequency in GHz, or None if unavailable."""
    try:
        if platform.system() == "Windows":
            import subprocess
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "MaxClockSpeed"],
                text=True, stderr=subprocess.DEVNULL,
            )
            mhz = int([l.strip() for l in out.splitlines() if l.strip().isdigit()][0])
            return mhz / 1000

        with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq") as f:
            return int(f.read().strip()) / 1_000_000
    except Exception:
        return None


def get_disk_free_gb(path: str) -> float:
    """Return free disk space in GB at path."""
    total, used, free = shutil.disk_usage(path)
    return free / (1024 ** 3)


# ── Check functions ─────────────────────────────────────────────────────────

def check_python() -> bool:
    section("1. Python")
    v = sys.version_info
    ver = f"{v.major}.{v.minor}.{v.micro}"
    print(info(f"Executable : {sys.executable}"))
    print(info(f"Version    : {ver}"))

    if v >= (3, 12):
        print(ok(f"Python {ver} — fully compatible"))
        return True
    elif v >= (3, 9):
        print(warn(f"Python {ver} — compatible but 3.12+ recommended"))
        return True
    else:
        print(fail(f"Python {ver} — requires >= 3.9"))
        return False


def check_system() -> bool:
    section("2. System (CPU & RAM)")
    os_name   = platform.system()
    arch      = platform.machine()
    cpu_cores = multiprocessing.cpu_count()
    total_ram, avail_ram = get_ram_gb()
    freq      = get_cpu_freq_ghz()

    print(info(f"OS         : {os_name} {platform.release()} ({arch})"))
    print(info(f"CPU cores  : {cpu_cores} logical cores"))
    if freq:
        print(info(f"CPU speed  : {freq:.2f} GHz"))

    ram_ok = True
    if total_ram >= 8:
        print(ok(f"Total RAM  : {total_ram:.1f} GB — excellent for TrOCR"))
    elif total_ram >= 4:
        print(warn(f"Total RAM  : {total_ram:.1f} GB — minimum, TrOCR base needs ~600 MB free"))
    else:
        print(fail(f"Total RAM  : {total_ram:.1f} GB — insufficient (need at least 4 GB)"))
        ram_ok = False

    if avail_ram >= 2:
        print(ok(f"Free RAM   : {avail_ram:.1f} GB available"))
    elif avail_ram >= 0.6:
        print(warn(f"Free RAM   : {avail_ram:.1f} GB — tight, close other apps before running OCR"))
    else:
        print(fail(f"Free RAM   : {avail_ram:.1f} GB — not enough to load TrOCR model"))
        ram_ok = False

    return ram_ok


def check_disk() -> bool:
    section("3. Disk Space")
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    free_gb = get_disk_free_gb(project_dir)
    print(info(f"Checking   : {project_dir}"))

    # torch CPU ~800 MB, trocr-base-printed ~330 MB, transformers ~200 MB
    needed_gb = 2.0
    if free_gb >= 10:
        print(ok(f"Free space : {free_gb:.1f} GB — plenty of room"))
        return True
    elif free_gb >= needed_gb:
        print(warn(f"Free space : {free_gb:.1f} GB — enough, but keep at least 2 GB free"))
        return True
    else:
        print(fail(f"Free space : {free_gb:.1f} GB — need at least {needed_gb} GB (torch + models)"))
        return False


def check_torch() -> bool:
    section("4. PyTorch")
    try:
        import torch

        version = torch.__version__
        print(ok(f"torch {version} installed"))

        # CUDA
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            print(ok(f"CUDA GPU   : {gpu_name} ({vram:.1f} GB VRAM) — inference will be fast"))
        else:
            print(warn("CUDA       : not available — will use CPU (2-5s/image, acceptable)"))

        # Quick tensor op to confirm torch works
        t0 = time.time()
        _ = torch.zeros(1000, 1000).matmul(torch.ones(1000, 1000))
        elapsed = (time.time() - t0) * 1000
        print(ok(f"CPU tensor : 1000×1000 matmul in {elapsed:.0f} ms"))

        if elapsed < 500:
            print(ok("CPU speed  : fast enough for real-time OCR"))
        elif elapsed < 2000:
            print(warn(f"CPU speed  : moderate — expect ~3-6s per ordonnance image"))
        else:
            print(warn(f"CPU speed  : slow — expect >6s per image, consider smaller model"))

        return True

    except ImportError:
        print(fail("torch is NOT installed in this environment"))
        print(info("Install : pip install torch --index-url https://download.pytorch.org/whl/cpu"))
        return False


def check_transformers() -> bool:
    section("5. Transformers (HuggingFace)")
    try:
        import transformers

        version = transformers.__version__
        print(ok(f"transformers {version} installed"))

        # Check TrOCR classes are available
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        print(ok("TrOCRProcessor + VisionEncoderDecoderModel importable"))
        return True

    except ImportError as e:
        print(fail(f"transformers not installed — {e}"))
        print(info("Install : pip install transformers==5.8.1"))
        return False


def check_trocr_inference() -> bool:
    section("6. TrOCR Live Inference Test")
    try:
        import torch
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        from PIL import Image

        model_name = "microsoft/trocr-base-printed"
        print(info(f"Loading model : {model_name}"))
        print(info("First run downloads ~330 MB — subsequent runs use local cache."))

        t0 = time.time()
        processor = TrOCRProcessor.from_pretrained(model_name)
        model     = VisionEncoderDecoderModel.from_pretrained(model_name)
        load_time = time.time() - t0
        print(ok(f"Model loaded  : {load_time:.1f}s"))

        # Generate a synthetic prescription-like image
        image = Image.new("RGB", (400, 80), color=(255, 255, 255))
        pixel_values = processor(image, return_tensors="pt").pixel_values

        t1 = time.time()
        with torch.no_grad():
            generated_ids = model.generate(pixel_values)
        infer_time = time.time() - t1
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print(ok(f"Inference     : {infer_time:.2f}s on blank test image"))
        print(info(f"Output text   : {repr(text)}"))

        if infer_time < 3:
            print(ok("Performance   : excellent for a hackathon demo"))
        elif infer_time < 6:
            print(warn(f"Performance   : acceptable (~{infer_time:.0f}s/image) — usable in demo"))
        else:
            print(warn(f"Performance   : slow ({infer_time:.0f}s/image) — consider trocr-small-printed"))

        return True

    except ImportError:
        print(warn("Skipped — torch or transformers not installed yet"))
        print(info("Run this check again after: pip install torch transformers"))
        return False
    except Exception as e:
        print(fail(f"TrOCR inference failed : {e}"))
        return False


# ── Final verdict ───────────────────────────────────────────────────────────

def print_verdict(results: dict[str, bool]) -> None:
    section("VERDICT")

    labels = {
        "python":       "Python >= 3.9",
        "system":       "RAM >= 4 GB",
        "disk":         "Disk space >= 2 GB free",
        "torch":        "PyTorch installed",
        "transformers": "Transformers installed",
        "trocr":        "TrOCR inference works",
    }

    all_critical = all(results[k] for k in ("python", "system", "disk"))
    ml_ready     = all(results[k] for k in ("torch", "transformers", "trocr"))

    for key, label in labels.items():
        if results[key]:
            print(ok(label))
        else:
            print(fail(label))

    print()
    if all_critical and ml_ready:
        print(f"{GREEN}{BOLD}  FULLY COMPATIBLE — tu peux utiliser TrOCR immédiatement.{RESET}")
    elif all_critical and results["torch"] and results["transformers"]:
        print(f"{YELLOW}{BOLD}  COMPATIBLE — torch+transformers OK, mais l'inférence n'a pas pu être testée.{RESET}")
    elif all_critical:
        print(f"{YELLOW}{BOLD}  SYSTÈME OK — installe torch + transformers pour activer l'OCR (Phase 2).{RESET}")
        print(f"{CYAN}  pip install torch --index-url https://download.pytorch.org/whl/cpu{RESET}")
        print(f"{CYAN}  pip install transformers==5.8.1{RESET}")
    else:
        print(f"{RED}{BOLD}  INCOMPATIBLE — problème matériel (RAM ou espace disque insuffisant).{RESET}")


# ── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    # Enable ANSI colours on Windows
    if platform.system() == "Windows":
        os.system("color")

    print(f"\n{BOLD}{CYAN}  FieldScreen AI v2 — Compatibility Checker{RESET}")
    print(f"{CYAN}  TrOCR (microsoft/trocr-base-printed) + PyTorch{RESET}")

    results = {
        "python":       check_python(),
        "system":       check_system(),
        "disk":         check_disk(),
        "torch":        check_torch(),
        "transformers": check_transformers(),
        "trocr":        False,
    }

    if results["torch"] and results["transformers"]:
        results["trocr"] = check_trocr_inference()
    else:
        section("6. TrOCR Live Inference Test")
        print(warn("Skipped — torch or transformers not installed"))

    print_verdict(results)
    print()


if __name__ == "__main__":
    main()
