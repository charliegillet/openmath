import importlib.util
import json
from pathlib import Path

from hills import run_evaluator


HILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("grothendieck_eval", HILL / "eval.py")
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def baseline():
    return json.loads((HILL / "examples" / "baseline" / "solution.json").read_text(encoding="utf-8"))


def submit(tmp_path, payload, *, final=False):
    (tmp_path / "solution.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_evaluator(HILL, tmp_path, final=final)


def test_baseline_is_an_exact_lower_bound_witness():
    result = run_evaluator(HILL, HILL / "examples" / "baseline")
    assert result["passed"], result
    assert [metric["value"] for metric in result["metrics"][:2]] == [1_400_000, 4]
    assert result["details"]["sign_optimum"] == 2
    assert result["details"]["lower_bound"] == "7/5"


def test_non_unit_vector_is_rejected(tmp_path):
    payload = baseline()
    payload["left_vectors"][0] = [[2, 1], [0, 1]]
    result = submit(tmp_path, payload)
    assert not result["passed"]
    assert "norm one" in result["details"]["error"]


def test_noncanonical_rational_is_rejected(tmp_path):
    payload = baseline()
    payload["right_vectors"][0][0] = [6, 10]
    result = submit(tmp_path, payload)
    assert not result["passed"]
    assert "canonical" in result["details"]["error"]


def test_bad_matrix_shape_is_rejected(tmp_path):
    for payload in [{}, {"matrix": [], "left_vectors": [], "right_vectors": []}, {"matrix": [[0, 1], [1, 1]], "left_vectors": [], "right_vectors": []}]:
        result = submit(tmp_path, payload)
        assert not result["passed"]
        assert result["metrics"] == []


def test_final_uses_the_hidden_test_fixture():
    result = run_evaluator(HILL, HILL / "examples" / "baseline", final=True)
    assert result["passed"], result
    assert result["config"][-1] == {"name": "mode", "value": "test", "primary": False}


def test_private_fixtures_are_distinct_and_exact():
    validation = json.loads((HILL / "private" / "validation.json").read_text(encoding="utf-8"))
    test = json.loads((HILL / "private" / "test.json").read_text(encoding="utf-8"))
    assert validation["matrix"] != test["matrix"]
    SCORER._load_fixture(False)
    SCORER._load_fixture(True)


def test_submission_code_is_not_executed(tmp_path):
    (tmp_path / "sitecustomize.py").write_text("raise RuntimeError('executed')", encoding="utf-8")
    result = submit(tmp_path, baseline())
    assert result["passed"], result
