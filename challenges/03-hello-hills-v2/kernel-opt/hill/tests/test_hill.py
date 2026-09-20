"""Checks run by `hills check`."""

from pathlib import Path

from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]


def test_baseline_compiles_verifies_and_scores():
    result = run_evaluator(HILL, HILL / "examples" / "baseline", n=256)
    assert result["passed"], result["details"]
    (m,) = [m for m in result["metrics"] if m["name"] == "gflops"]
    assert m["value"] > 0.05
    assert any(c["name"] == "machine" and c["primary"] for c in result["config"])


def test_wrong_kernel_is_rejected(tmp_path):
    (tmp_path / "kernel.c").write_text(
        "void gemm(int n, const float *A, const float *B, float *C) {\n"
        "    for (int i = 0; i < n * n; i++) C[i] = 0.0f;  /* not a matmul */\n"
        "}\n"
    )
    result = run_evaluator(HILL, tmp_path, n=256)
    assert not result["passed"]
    assert "wrong result" in result["details"]["error"]


def test_missing_source_is_rejected(tmp_path):
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert "kernel.c" in result["details"]["error"]


def test_noop_at_timed_size_is_rejected(tmp_path):
    """A kernel correct at the small size but a no-op at the timed size must
    not post a fake GFLOP/s."""
    (tmp_path / "kernel.c").write_text(
        "void gemm(int n, const float *A, const float *B, float *C) {\n"
        "    if (n == 96) {  /* correct only at the hidden correctness size */\n"
        "        for (int i = 0; i < n; i++)\n"
        "            for (int j = 0; j < n; j++) {\n"
        "                float acc = 0.0f;\n"
        "                for (int k = 0; k < n; k++) acc += A[i*n+k] * B[k*n+j];\n"
        "                C[i*n+j] = acc;\n"
        "            }\n"
        "        return;\n"
        "    }\n"
        "    /* timed size: do nothing (leave C as-is) */\n"
        "}\n"
    )
    # correctness runs at 96; time at 256 -> the no-op path must be caught
    result = run_evaluator(HILL, tmp_path, n=256)
    assert not result["passed"]
    assert "timed size" in result["details"]["error"]


def test_cross_call_memoization_is_rejected(tmp_path):
    """A kernel that caches the result of the first (warmup) call and replays it
    with a memcpy must not post a fake throughput: timed reps use fresh inputs,
    so the cache misses and the replayed (stale) output fails verification."""
    # Cache only at the timed size (n >= 200) so the m=96 correctness stage stays
    # honest and this test isolates the timing-integrity defense.
    (tmp_path / "kernel.c").write_text(
        "#include <string.h>\n"
        "static float cache[2048*2048];\n"
        "static int have = 0;\n"
        "void gemm(int n, const float *A, const float *B, float *C) {\n"
        "    if (have && n >= 200 && n <= 2048) { memcpy(C, cache, (size_t)n*n*sizeof(float)); return; }\n"
        "    for (int i=0;i<n;i++) for(int j=0;j<n;j++){float acc=0;for(int k=0;k<n;k++)acc+=A[i*n+k]*B[k*n+j];C[i*n+j]=acc;}\n"
        "    if (n >= 200 && n <= 2048) { memcpy(cache, C, (size_t)n*n*sizeof(float)); have = 1; }\n"
        "}\n"
    )
    result = run_evaluator(HILL, tmp_path, n=256)
    assert not result["passed"]
    assert "timed size" in result["details"]["error"]


def test_tolerance_is_part_of_comparison_config():
    for tolerance in (0.001, 0.01):
        result = run_evaluator(HILL, HILL / "examples" / "baseline", n=128, tolerance=tolerance)
        assert result["passed"], result["details"]
        primary = {entry["name"]: entry["value"] for entry in result["config"] if entry["primary"]}
        assert primary.get("tolerance") == tolerance


def test_timing_details_explain_the_reported_throughput():
    import math

    result = run_evaluator(HILL, HILL / "examples" / "baseline", n=128)
    assert result["passed"], result["details"]
    details = result["details"]
    timings = details.get("timings_seconds", [])
    assert len(timings) == 3 and all(seconds > 0 for seconds in timings)
    assert min(timings) == details["seconds_best_of_3"]
    assert math.isclose(result["metrics"][0]["value"], 2 * 128**3 / min(timings) / 1e9)
    assert details.get("compiler") and details.get("architecture")


def test_correctness_error_does_not_reveal_hidden_seed(tmp_path):
    (tmp_path / "kernel.c").write_text(
        "void gemm(int n, const float *A, const float *B, float *C) {"
        "for (int i=0; i<n*n; i++) C[i] = 0.0f;}"
    )
    result = run_evaluator(HILL, tmp_path, n=128)
    assert not result["passed"]
    leaks_seed = "seed" in result["details"]["error"]
    assert leaks_seed is False
