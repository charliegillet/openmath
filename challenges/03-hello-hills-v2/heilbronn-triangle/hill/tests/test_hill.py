"""Checks on the hill itself, run by `hills check`."""

import json
import math
from pathlib import Path

from hills import run_evaluator

HILL = Path(__file__).resolve().parents[1]
EXAMPLES = HILL / "examples"


def _write(tmp_path, points):
    (tmp_path / "points.json").write_text(json.dumps(points))
    return tmp_path


def test_baseline_is_valid():
    result = run_evaluator(HILL, EXAMPLES / "baseline")
    assert result["passed"], result["details"]
    assert result["metrics"][0]["name"] == "min_area"
    assert 0.02 < result["metrics"][0]["value"] < 0.0365


def test_four_points_exact_value(tmp_path):
    # Three corners plus the centroid: every triangle has a third of the area.
    apex_y = "0.86602540378443864676372317075293618347140262690519"
    points = [[0, 0], [1, 0], ["0.5", apex_y], ["0.5", "0.28867513459481288225457439025097872782380087563506"]]
    result = run_evaluator(HILL, _write(tmp_path, points), n=4)
    assert result["passed"], result["details"]
    assert math.isclose(result["metrics"][0]["value"], 1 / 3, rel_tol=1e-15)


def test_missing_file_is_rejected(tmp_path):
    result = run_evaluator(HILL, tmp_path)
    assert not result["passed"]
    assert "points.json" in result["details"]["error"]


def test_outside_point_is_rejected(tmp_path):
    points = [[0, 0], [1, 0], ["0.5", "0.9"], ["0.5", "0.2"]]
    result = run_evaluator(HILL, _write(tmp_path, points), n=4)
    assert not result["passed"]
    assert "outside" in result["details"]["error"]


def test_collinear_points_are_rejected(tmp_path):
    points = [[0, 0], ["0.5", 0], [1, 0], ["0.5", "0.2"]]
    result = run_evaluator(HILL, _write(tmp_path, points), n=4)
    assert not result["passed"]
    assert "collinear" in result["details"]["error"]


def test_wrong_count_is_rejected(tmp_path):
    result = run_evaluator(HILL, _write(tmp_path, [[0, 0], [1, 0]]))
    assert not result["passed"]
    assert "expected 11" in result["details"]["error"]


def test_nan_inf_and_bool_are_rejected(tmp_path):
    for bad in ('"nan"', '"inf"', '"Infinity"', "true", "1e999999999", '"1e-999999999"'):
        (tmp_path / "points.json").write_text('[[0, 0], [1, 0], ["0.5", %s], ["0.5", "0.2"]]' % bad)
        result = run_evaluator(HILL, tmp_path, n=4)
        assert not result["passed"], bad


def test_digit_cap_is_enforced(tmp_path):
    long = "0." + "3" * 201
    points = [[0, 0], [1, 0], ["0.5", "0.8"], [long, "0.2"]]
    result = run_evaluator(HILL, _write(tmp_path, points), n=4)
    assert not result["passed"]
    assert "200 significant digits" in result["details"]["error"]


def test_alphaevolve_construction_scores_in_the_papers_units():
    result = run_evaluator(HILL, EXAMPLES / "alphaevolve")
    assert result["passed"], result["details"]
    assert 0.0365 < result["metrics"][0]["value"] < 0.0366


def test_edge_points_from_doubles_are_accepted(tmp_path):
    import math
    points = [[0, 0], [1, 0], ["0.5", repr(math.sqrt(3) / 2)], [repr(0.3), repr(math.sqrt(3) * 0.3)]]
    result = run_evaluator(HILL, _write(tmp_path, points), n=4)
    assert result["passed"], result["details"]
