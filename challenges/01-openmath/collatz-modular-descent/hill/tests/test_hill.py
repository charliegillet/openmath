import importlib.util
import json
from pathlib import Path

from hills import run_evaluator


HILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("collatz_eval", HILL / "eval.py")
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def submit(tmp_path, payload, *, final=False):
    (tmp_path / "solution.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_evaluator(HILL, tmp_path, final=final)


def test_baseline_is_an_exact_descent_certificate():
    result = run_evaluator(HILL, HILL / "examples" / "baseline")
    assert result["passed"], result
    assert result["metrics"][0]["name"] == "coverage_ppm"
    assert result["metrics"][0]["value"] > 0
    assert result["metrics"][1]["value"] > 0
    assert result["details"]["rules_verified"] == 2


def test_wrong_valuation_is_rejected(tmp_path):
    result = submit(tmp_path, {"rules": [{"modulus_power": 4, "residue": 9, "exponents": [3]}]})
    assert not result["passed"]
    assert "v2" in result["details"]["error"]


def test_insufficient_modulus_cannot_claim_pattern_stability(tmp_path):
    result = submit(tmp_path, {"rules": [{"modulus_power": 3, "residue": 5, "exponents": [4]}]})
    assert not result["passed"]
    assert "stabilize" in result["details"]["error"]


def test_malformed_submission_is_rejected(tmp_path):
    for payload in [{}, {"rules": []}, {"rules": [{"modulus_power": 4, "residue": 8, "exponents": [2]}]}]:
        result = submit(tmp_path, payload)
        assert not result["passed"]
        assert result["metrics"] == []


def test_final_uses_the_private_test_split():
    result = run_evaluator(HILL, HILL / "examples" / "baseline", final=True)
    assert result["passed"], result
    assert result["config"][-1] == {"name": "mode", "value": "test", "primary": False}
    assert result["details"]["private_targets_scored"] > 0


def test_submission_code_is_not_executed(tmp_path):
    (tmp_path / "sitecustomize.py").write_text("raise RuntimeError('executed')", encoding="utf-8")
    payload = json.loads((HILL / "examples" / "baseline" / "solution.json").read_text(encoding="utf-8"))
    result = submit(tmp_path, payload)
    assert result["passed"], result
