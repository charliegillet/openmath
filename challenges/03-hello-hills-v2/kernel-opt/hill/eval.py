"""Evaluator for kernel-opt: single-thread SGEMM throughput in GFLOP/s.

The submission ships `kernel.c` defining

    void gemm(int n, const float *A, const float *B, float *C);

computing C = A @ B (row-major, n x n). The evaluator compiles it with a fixed
command line, checks correctness against a NumPy reference on inputs seeded
from private/, then times the n=512 case and reports best-of-3 GFLOP/s.

Numbers are only comparable on the same machine — the leaderboard's
`machine` config entry keeps different hosts in different comparison classes.
"""

import ctypes
import json
import platform
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

HILL = Path(__file__).resolve().parent
CFLAGS = ["-O3", "-march=native", "-ffast-math", "-shared", "-fPIC", "-lm"]


def _fail(error: str) -> dict:
    return {"passed": False, "metrics": [], "config": [], "details": {"error": error}}


def _compile(source: Path, workdir: Path) -> Path:
    out = workdir / "kernel.so"
    cmd = ["cc", str(source), "-o", str(out), *CFLAGS]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"compilation failed:\n{proc.stderr[-1500:]}")
    return out


def _gemm_fn(lib_path: Path):
    lib = ctypes.CDLL(str(lib_path))
    fn = lib.gemm
    fn.restype = None
    f32p = ctypes.POINTER(ctypes.c_float)
    fn.argtypes = [ctypes.c_int, f32p, f32p, f32p]

    def call(n: int, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        c = np.zeros((n, n), dtype=np.float32)
        fn(
            n,
            a.ctypes.data_as(f32p),
            b.ctypes.data_as(f32p),
            c.ctypes.data_as(f32p),
        )
        return c

    return call


def eval(submission: Path, *, final: bool = False, n: int = 512, tolerance: float = 2e-3) -> dict:
    source = submission / "kernel.c"
    if not source.is_file():
        return _fail("submission must contain kernel.c")
    seeds = json.loads((HILL / "private" / "seeds.json").read_text())
    seeds = seeds["test" if final else "validation"]

    try:
        with tempfile.TemporaryDirectory(prefix="kernel-opt-") as scratch:
            call = _gemm_fn(_compile(source, Path(scratch)))
            compiler = subprocess.run(
                ["cc", "--version"], capture_output=True, text=True, timeout=10, check=True
            ).stdout.splitlines()[0]

            # Correctness on small cases, seeds hidden in private/.
            for case, seed in enumerate(seeds):
                rng = np.random.default_rng(seed)
                m = 96
                a = rng.standard_normal((m, m), dtype=np.float32)
                b = rng.standard_normal((m, m), dtype=np.float32)
                got = call(m, np.ascontiguousarray(a), np.ascontiguousarray(b))
                want = a @ b
                err = float(np.max(np.abs(got - want)) / (np.max(np.abs(want)) + 1e-9))
                if not np.isfinite(got).all() or err > tolerance:
                    return _fail(f"wrong result for correctness case {case}: relative error {err:.2e}")

            # Throughput at the timed size, with FRESH random inputs for every
            # timed repetition (and a separate warmup). Distinct data each rep
            # defeats a kernel that memoizes on the (n, A, B) it saw during
            # warmup and replays a cached result with a memcpy — which would
            # otherwise time the memcpy, not the matmul, yet pass correctness
            # and the checksum. Each rep's output is verified against the oracle.
            trng = np.random.default_rng(seeds[0] + 1)
            warm = np.ascontiguousarray(trng.standard_normal((n, n), dtype=np.float32))
            call(n, warm, warm)  # warmup on data never reused for timing
            best = float("inf")
            got = None
            timings = []
            for rep in range(3):
                a = np.ascontiguousarray(trng.standard_normal((n, n), dtype=np.float32))
                b = np.ascontiguousarray(trng.standard_normal((n, n), dtype=np.float32))
                t0 = time.perf_counter()
                got = call(n, a, b)
                elapsed = time.perf_counter() - t0
                timings.append(elapsed)
                best = min(best, elapsed)
                want = a @ b
                timed_err = float(np.max(np.abs(got - want)) / (np.max(np.abs(want)) + 1e-9))
                if not np.isfinite(got).all() or timed_err > tolerance:
                    return _fail(
                        f"wrong result at the timed size n={n} (rep {rep}): "
                        f"relative error {timed_err:.2e}"
                    )
            checksum = float(np.sum(got))
            gflops = (2.0 * n**3) / best / 1e9
    except Exception as exc:  # noqa: BLE001 — the report carries the reason
        return _fail(f"{type(exc).__name__}: {exc}")

    return {
        "passed": True,
        "metrics": [{"name": "gflops", "value": gflops, "direction": "max"}],
        "config": [
            {"name": "mode", "value": "test" if final else "validation", "primary": True},
            {"name": "n", "value": n, "primary": True},
            {"name": "tolerance", "value": tolerance, "primary": True},
            {"name": "machine", "value": platform.node() or "unknown", "primary": True},
        ],
        "details": {
            "seconds_best_of_3": best,
            "timings_seconds": timings,
            "compiler": compiler,
            "compiler_flags": CFLAGS,
            "architecture": platform.machine(),
            "platform": platform.system(),
            "checksum": checksum,
        },
    }
