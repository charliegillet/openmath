"""Checks run by `hills check`."""

import textwrap
from pathlib import Path

from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]


def test_baseline_scores_reasonably():
    result = run_evaluator(HILL, HILL / "examples" / "baseline", eval_chars=2000)
    assert result["passed"], result["details"]
    (bpc,) = [m for m in result["metrics"] if m["name"] == "bpc"]
    assert 3.0 < bpc["value"] < 6.1


def test_missing_model_is_rejected(tmp_path):
    result = run_evaluator(HILL, tmp_path, eval_chars=2000)
    assert not result["passed"] and "model.py" in result["details"]["error"]


def test_cannot_peek_current_char(tmp_path):
    """The model is only ever handed the prefix, so a would-be peeker has no
    access to text[i]: guessing 'the next char is whatever I most expect' with
    probability 1 is wrong most of the time and lands on the floor penalty —
    it scores far WORSE than the baseline, never bpc 0."""
    (tmp_path / "model.py").write_text(textwrap.dedent("""
        # 'Certain' the next char is always 'e' (can't see the real next char).
        def predict_next(prefix):
            return {"e": 0.0}
    """))
    result = run_evaluator(HILL, tmp_path, eval_chars=2000)
    assert result["passed"]  # it's a valid (normalized) model...
    (bpc,) = [m for m in result["metrics"] if m["name"] == "bpc"]
    assert bpc["value"] > 6.0  # ...but far worse than the ~4.1 baseline


def test_unnormalized_distribution_is_rejected(tmp_path):
    (tmp_path / "model.py").write_text(textwrap.dedent("""
        import math
        _A = "abcdefghijklmnopqrstuvwxyz ."
        def predict_next(prefix):
            return {c: math.log(0.9) for c in _A}  # sum ~ 0.9*|A| >> 1
    """))
    result = run_evaluator(HILL, tmp_path, eval_chars=2000)
    assert not result["passed"]
    assert "sums to" in result["details"]["error"]


def test_copied_baseline_scores_from_an_unrelated_directory(tmp_path, monkeypatch):
    import shutil

    submission = tmp_path / "submission"
    shutil.copytree(HILL / "examples" / "baseline", submission)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    result = run_evaluator(HILL, submission, eval_chars=2000)
    assert result["passed"], result["details"]
    assert 3.0 < result["metrics"][0]["value"] < 6.1
