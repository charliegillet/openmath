"""Contract tests for the exact tensor-rank evaluator."""

import importlib.util
import json
from pathlib import Path

from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("matmul_tensor_eval", HILL / "eval.py")
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def submit(tmp_path, payload, *, final=False):
    (tmp_path / "solution.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_evaluator(HILL, tmp_path, final=final)


def schoolbook():
    u, v, w = [], [], []
    for row in range(3):
        for inner in range(3):
            for column in range(3):
                left, right, output = [0] * 9, [0] * 9, [0] * 9
                left[3 * row + inner] = 1
                right[3 * inner + column] = 1
                output[3 * column + row] = 1
                u.append(left)
                v.append(right)
                w.append(output)
    return {"u": u, "v": v, "w": w}


def test_laderman_baseline_is_exact_rank_23():
    result = run_evaluator(HILL, HILL / "examples" / "baseline")
    assert result["passed"], result
    assert result["metrics"][0] == {"name": "rank", "value": 23, "direction": "min"}
    assert result["metrics"][1]["name"] == "support"
    assert result["details"]["brent_identities_checked"] == 729


def test_schoolbook_decomposition_and_rational_scaling_pass(tmp_path):
    payload = schoolbook()
    payload["u"][0][0] = [2, 1]
    payload["v"][0][0] = [1, 2]
    result = submit(tmp_path, payload)
    assert result["passed"], result
    assert [metric["value"] for metric in result["metrics"]] == [27, 81]


def test_one_wrong_coefficient_fails_an_exact_identity(tmp_path):
    payload = schoolbook()
    payload["w"][0][0] = -1
    result = submit(tmp_path, payload)
    assert not result["passed"]
    assert "Brent identity" in result["details"]["error"]


def test_malformed_submission_is_rejected(tmp_path):
    for payload in [
        {},
        {"u": [], "v": [], "w": []},
        {"u": [[0] * 9, [0] * 9], "v": [[0] * 9], "w": [[0] * 9]},
        {"u": [[0] * 9,], "v": [[0] * 9], "w": [[0, 0, 0, 0, 0, 0, 0, 0, True]]},
        {"u": [[0] * 8], "v": [[0] * 9], "w": [[0] * 9]},
    ]:
        result = submit(tmp_path, payload)
        assert not result["passed"]
        assert result["metrics"] == []


def test_final_uses_private_test_replays(tmp_path):
    result = submit(tmp_path, schoolbook(), final=True)
    assert result["passed"]
    assert result["details"]["private_replays_checked"] == 3
    assert result["config"][-1] == {"name": "mode", "value": "test", "primary": False}


def test_submission_code_is_not_executed(tmp_path):
    (tmp_path / "sitecustomize.py").write_text("raise RuntimeError('executed')", encoding="utf-8")
    result = submit(tmp_path, schoolbook())
    assert result["passed"]
