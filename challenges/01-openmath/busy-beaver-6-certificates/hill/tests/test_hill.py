import importlib.util
import json
from pathlib import Path

from hills import run_evaluator


HILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bb6_eval", HILL / "eval.py")
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def baseline():
    return json.loads((HILL / "examples" / "baseline" / "solution.json").read_text(encoding="utf-8"))


def submit(tmp_path, payload, *, final=False):
    (tmp_path / "solution.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_evaluator(HILL, tmp_path, final=final)


def test_baseline_is_a_six_state_halting_witness():
    result = run_evaluator(HILL, HILL / "examples" / "baseline")
    assert result["passed"], result
    assert [metric["value"] for metric in result["metrics"]] == [6, 6, 7]
    assert result["details"] == {"halting_verified": True, "states_reached": 6}


def test_machine_that_loops_is_rejected(tmp_path):
    payload = baseline()
    for state in "ABCDEF":
        payload["transitions"][state]["1"] = payload["transitions"][state]["0"]
    payload["transitions"]["F"]["0"] = [1, "L", "A"]
    result = submit(tmp_path, payload)
    assert not result["passed"]
    assert "did not halt" in result["details"]["error"]


def test_machine_that_skips_states_is_rejected(tmp_path):
    payload = baseline()
    payload["transitions"]["A"]["0"] = [1, "R", "H"]
    result = submit(tmp_path, payload)
    assert not result["passed"]
    assert "without reaching all six states" in result["details"]["error"]


def test_malformed_machine_is_rejected(tmp_path):
    for payload in [{}, {"transitions": {}}, {"transitions": {state: {"0": [1, "R", "H"], "1": [1, "R", "H"]} for state in "ABCDE"}}]:
        result = submit(tmp_path, payload)
        assert not result["passed"]
        assert result["metrics"] == []


def test_final_uses_the_private_test_budget():
    result = run_evaluator(HILL, HILL / "examples" / "baseline", final=True)
    assert result["passed"], result
    assert result["config"][-1] == {"name": "mode", "value": "test", "primary": False}


def test_submission_code_is_not_executed(tmp_path):
    (tmp_path / "sitecustomize.py").write_text("raise RuntimeError('executed')", encoding="utf-8")
    result = submit(tmp_path, baseline())
    assert result["passed"], result
