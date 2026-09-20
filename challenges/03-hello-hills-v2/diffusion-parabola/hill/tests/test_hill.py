"""Checks on the hill itself, run by `hills check`."""

import math
from pathlib import Path

from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]
BASELINE = HILL / "examples" / "baseline"


def test_baseline_scores():
    # Small step budget keeps the test fast; we only need a valid, finite score.
    result = run_evaluator(HILL, BASELINE, steps=200, n_samples=500)
    assert result["passed"]
    metric = result["metrics"][0]
    assert metric["name"] == "chamfer_distance"
    assert metric["direction"] == "min"
    assert math.isfinite(metric["value"])
    assert metric["value"] > 0.0


def test_config_marks_steps_primary_and_reports_chamfer():
    result = run_evaluator(HILL, BASELINE, steps=200, n_samples=500)
    config = {entry["name"]: entry for entry in result["config"]}
    assert config["steps"]["primary"] is True
    assert config["steps"]["value"] == 200
    assert config["n_samples"]["primary"] is True
    assert result["metrics"][0]["name"] == "chamfer_distance"
    assert result["metrics"][0]["direction"] == "min"


def test_final_uses_a_different_test_split():
    # Different held-out seed -> generally a different score, but always valid.
    val = run_evaluator(HILL, BASELINE, steps=200, n_samples=500)
    final = run_evaluator(HILL, BASELINE, steps=200, n_samples=500, final=True)
    assert val["passed"] and final["passed"]
    assert final["details"]["final"] is True
    assert val["details"]["final"] is False
    assert val["metrics"][0]["value"] != final["metrics"][0]["value"]


def test_missing_solution_is_rejected(tmp_path):
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert "solution.py" in result["details"]["error"]


def test_bad_return_shape_is_rejected(tmp_path):
    (tmp_path / "solution.py").write_text(
        "import numpy as np\n"
        "def train_and_sample(data, *, steps, n_samples, seed):\n"
        "    return np.zeros((n_samples, 3))\n"
    )
    result = run_evaluator(HILL, tmp_path, steps=100, n_samples=100)
    assert not result["passed"]
    assert "shape" in result["details"]["error"]


def test_nonfinite_samples_are_rejected(tmp_path):
    (tmp_path / "solution.py").write_text(
        "import numpy as np\n"
        "def train_and_sample(data, *, steps, n_samples, seed):\n"
        "    return np.full((n_samples, 2), np.nan)\n"
    )
    result = run_evaluator(HILL, tmp_path, steps=100, n_samples=100)
    assert not result["passed"]
    assert "NaN or inf" in result["details"]["error"]


def test_submission_exception_is_reported(tmp_path):
    (tmp_path / "solution.py").write_text(
        "def train_and_sample(data, *, steps, n_samples, seed):\n"
        "    raise ValueError('training failed')\n"
    )
    result = run_evaluator(HILL, tmp_path, steps=100, n_samples=100)
    assert not result["passed"]
    assert "training failed" in result["details"]["error"]


def test_public_copy_explains_missing_official_data(tmp_path):
    import shutil

    public = tmp_path / "public"
    shutil.copytree(HILL, public, ignore=shutil.ignore_patterns("private", ".vc"))
    result = run_evaluator(public, BASELINE, steps=100, n_samples=100)
    assert not result["passed"]
    assert "private evaluation data" in result["details"]["error"]
    assert "AutoLab" in result["details"]["error"]
