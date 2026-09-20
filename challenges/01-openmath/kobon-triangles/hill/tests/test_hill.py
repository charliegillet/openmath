"""Contract tests and an independent exact geometric oracle."""
import importlib.util
import json
import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import pytest
from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kobon_eval", HILL / "eval.py")
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def submit(tmp_path, lines, n=None, final=False):
    (tmp_path / "solution.json").write_text(json.dumps({"lines": lines}))
    return run_evaluator(HILL, tmp_path, n=len(lines) if n is None else n, final=final)


def triangle_count(result):
    assert result["passed"], result
    assert result["metrics"][0]["name"] == "triangles"
    assert result["metrics"][0]["direction"] == "max"
    return result["metrics"][0]["value"]


def oracle(lines):
    """Independent oracle: reject a triangle if another line crosses its interior."""
    def meet(u, v):
        a, b, c = u
        d, e, f = v
        determinant = a * e - b * d
        if determinant == 0:
            return None
        return Fraction(b * f - c * e, determinant), Fraction(c * d - a * f, determinant)
    count = 0
    for i, j, k in combinations(range(len(lines)), 3):
        vertices = [meet(lines[i], lines[j]), meet(lines[i], lines[k]), meet(lines[j], lines[k])]
        if None in vertices or len(set(vertices)) != 3:
            continue
        for index, (a, b, c) in enumerate(lines):
            if index in (i, j, k):
                continue
            signs = [a * x + b * y + c for x, y in vertices]
            if min(signs) < 0 < max(signs):
                break
        else:
            count += 1
    return count


def test_baseline_scores():
    result = run_evaluator(HILL, HILL / "examples" / "baseline")
    assert triangle_count(result) == 16
    assert result["config"][0] == {"name": "n", "value": 18, "primary": True}


@pytest.mark.parametrize("split", ["validation", "test"])
def test_private_regression_fixtures(tmp_path, split):
    fixtures = json.loads((HILL / "private" / f"{split}.json").read_text())
    for fixture in fixtures:
        result = submit(tmp_path, fixture["lines"], final=split == "test")
        assert triangle_count(result) == fixture["triangles"], fixture["name"]
        assert oracle(fixture["lines"]) == fixture["triangles"], fixture["name"]


def test_missing_submission_rejected(tmp_path):
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert "solution.json" in result["details"]["error"]


@pytest.mark.parametrize("raw", [
    "not json", "[]", "null", '{}', '{"lines": null}', '{"lines": []}',
    '{"lines": [], "lines": []}', '{"lines": [], "triangles": 99999}', '{"lines": [[[[]]]]}',
])
def test_malformed_json_rejected(tmp_path, raw):
    (tmp_path / "solution.json").write_text(raw)
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert result["metrics"] == []


@pytest.mark.parametrize("bad_line", [
    [0, 0, 1], [True, 1, 0], [1.0, 0, 0], ["1", 0, 0],
    [1, 2], [1, 2, 3, 4], [10**30 + 1, 0, 0], [float("nan"), 1, 0], [float("inf"), 1, 0],
])
def test_invalid_lines_rejected(tmp_path, bad_line):
    result = submit(tmp_path, [bad_line, [0, 1, 0], [1, 1, -1]])
    assert not result["passed"]


def test_scaled_duplicate_rejected(tmp_path):
    result = submit(tmp_path, [[1, 2, 3], [-2, -4, -6], [0, 1, 0]])
    assert not result["passed"]
    assert "duplicates" in result["details"]["error"]


def test_wrong_line_count_rejected(tmp_path):
    assert not submit(tmp_path, [[1, 0, 0], [0, 1, 0], [1, 1, -1]], n=18)["passed"]


def test_oversized_file_rejected(tmp_path):
    (tmp_path / "solution.json").write_bytes(b" " * 65537)
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert "size limit" in result["details"]["error"]


def test_deep_json_rejected_without_traceback(tmp_path):
    (tmp_path / "solution.json").write_text("[" * 2000 + "]" * 2000)
    assert not run_evaluator(HILL, tmp_path)["passed"]


def test_final_scores_same_geometry(tmp_path):
    lines = [[1, 0, 0], [0, 1, 0], [1, 1, -1]]
    normal = submit(tmp_path, lines)
    final = submit(tmp_path, lines, final=True)
    assert triangle_count(normal) == triangle_count(final) == 1
    assert final["config"][-1]["value"] == "test"


def test_near_concurrency_uses_exact_arithmetic(tmp_path):
    m = 10**30
    assert triangle_count(submit(tmp_path, [[1, 0, 0], [0, 1, 0], [m, m, -1]])) == 1


def test_independent_oracle_on_varied_arrangements():
    rng = random.Random(9818)
    for _ in range(80):
        unique = set()
        while len(unique) < 8:
            row = tuple(rng.randint(-5, 5) for _ in range(3))
            if row[0] or row[1]:
                unique.add(SCORER._normalize(row))
        lines = sorted(unique)
        assert len(SCORER.count_triangles(lines)) == oracle(lines)


def test_order_scaling_and_affine_invariance():
    lines = [[2 * i, -1, -i * i] for i in range(18)]
    transformed = [[2 * a + b, a + b, 3 * a - 4 * b + c] for a, b, c in lines]
    assert len(SCORER.count_triangles(transformed)) == 16
    scaled = [[-7 * coefficient for coefficient in line] for line in reversed(transformed)]
    assert len(SCORER.count_triangles(scaled)) == 16


def test_maximum_line_count():
    lines = [[2 * i, -1, -i * i] for i in range(100)]
    assert len(SCORER.count_triangles(lines)) == 98


def test_submission_code_is_not_executed(tmp_path):
    (tmp_path / "sitecustomize.py").write_text('raise RuntimeError("submission executed")')
    (tmp_path / "eval.py").write_text('raise RuntimeError("submission executed")')
    assert triangle_count(submit(tmp_path, [[1, 0, 0], [0, 1, 0], [1, 1, -1]])) == 1

