"""Exact evaluator for finite rational Grothendieck-constant witnesses."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path


HILL = Path(__file__).resolve().parent
MAX_BYTES = 262_144
MAX_SIDE = 8
MAX_DIMENSION = 16
MAX_COORDINATE = 1_000_000


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _rational(value, label: str) -> Fraction:
    if not isinstance(value, list) or len(value) != 2 or any(type(item) is not int for item in value):
        raise ValueError(f"{label} must be [numerator, denominator] with integer entries")
    numerator, denominator = value
    if not 0 < denominator <= MAX_COORDINATE or abs(numerator) > MAX_COORDINATE:
        raise ValueError(f"{label} exceeds the coordinate bound")
    if math.gcd(abs(numerator), denominator) != 1:
        raise ValueError(f"{label} must be in canonical lowest terms")
    return Fraction(numerator, denominator)


def _parse_witness(data, *, source: str):
    matrix, left, right = data.get("matrix"), data.get("left_vectors"), data.get("right_vectors")
    if not isinstance(matrix, list) or not 2 <= len(matrix) <= MAX_SIDE or any(not isinstance(row, list) for row in matrix):
        raise ValueError(f"{source} matrix must have 2 through {MAX_SIDE} rows")
    m = len(matrix)
    n = len(matrix[0]) if matrix else 0
    if not 2 <= n <= MAX_SIDE or any(len(row) != n for row in matrix):
        raise ValueError(f"{source} matrix must be rectangular with 2 through {MAX_SIDE} columns")
    if any(type(entry) is not int or entry not in {-1, 1} for row in matrix for entry in row):
        raise ValueError(f"{source} matrix entries must be -1 or 1")
    if not isinstance(left, list) or not isinstance(right, list) or len(left) != m or len(right) != n:
        raise ValueError(f"{source} vector counts must match the matrix dimensions")
    if any(not isinstance(vector, list) for vector in left + right):
        raise ValueError(f"{source} vectors must be lists")
    dimension = len(left[0]) if left else 0
    if not 2 <= dimension <= MAX_DIMENSION or any(len(vector) != dimension for vector in left + right):
        raise ValueError(f"{source} vectors must share a dimension from 2 through {MAX_DIMENSION}")
    parsed_sides = []
    for side, raw_vectors in (("left_vectors", left), ("right_vectors", right)):
        parsed_side = []
        for row_index, vector in enumerate(raw_vectors):
            parsed = [_rational(value, f"{side}[{row_index}][{column_index}]") for column_index, value in enumerate(vector)]
            if sum(value * value for value in parsed) != 1:
                raise ValueError(f"{side}[{row_index}] does not have exact squared norm one")
            parsed_side.append(parsed)
        parsed_sides.append(parsed_side)
    return matrix, parsed_sides[0], parsed_sides[1]


def _load_solution(submission: Path):
    solution_path = Path(submission) / "solution.json"
    if solution_path.is_symlink() or not solution_path.is_file():
        raise ValueError("submission must contain a regular solution.json")
    raw = solution_path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError(f"solution.json exceeds the {MAX_BYTES}-byte limit")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"matrix", "left_vectors", "right_vectors"}:
        raise ValueError("solution.json must contain exactly matrix, left_vectors, and right_vectors")
    return _parse_witness(data, source="submission")


def _sign_optimum(matrix) -> int:
    """Maximize over the left signs; each right sign then has a closed form."""
    m, n = len(matrix), len(matrix[0])
    best = 0
    for mask in range(1 << m):
        total = 0
        for column in range(n):
            column_sum = sum((1 if (mask >> row) & 1 else -1) * matrix[row][column] for row in range(m))
            total += abs(column_sum)
        best = max(best, total)
    return best


def _vector_objective(matrix, left, right) -> Fraction:
    return sum(
        matrix[row][column] * sum(left[row][coordinate] * right[column][coordinate] for coordinate in range(len(left[row])))
        for row in range(len(matrix))
        for column in range(len(matrix[0]))
    )


def _certificate_bits(left, right) -> int:
    return sum(
        value.numerator.bit_length() + value.denominator.bit_length()
        for vector in left + right
        for value in vector
    )


def _load_fixture(final: bool):
    filename = "test.json" if final else "validation.json"
    data = json.loads((HILL / "private" / filename).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"matrix", "left_vectors", "right_vectors", "expected"}:
        raise ValueError("private fixture schema is invalid")
    matrix, left, right = _parse_witness(data, source="private fixture")
    expected = data["expected"]
    if not isinstance(expected, dict) or set(expected) != {"sign_optimum", "objective"}:
        raise ValueError("private fixture expected schema is invalid")
    sign = expected["sign_optimum"]
    if type(sign) is not int or sign <= 0:
        raise ValueError("private fixture sign optimum is invalid")
    objective = _rational(expected["objective"], "private fixture objective")
    if _sign_optimum(matrix) != sign or _vector_objective(matrix, left, right) != objective:
        raise ValueError("private arithmetic fixture failed")


def _config(final: bool):
    return [
        {"name": "certificate", "value": "finite-rational-grothendieck-witness", "primary": True},
        {"name": "matrix_bounds", "value": "2-8-by-2-8", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]


def eval(submission: Path, *, final: bool = False) -> dict:
    config = _config(final)
    try:
        _load_fixture(final)
        matrix, left, right = _load_solution(submission)
        sign_optimum = _sign_optimum(matrix)
        objective = _vector_objective(matrix, left, right)
        if objective <= 0:
            raise ValueError("the submitted vector objective must be positive")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, RecursionError) as error:
        return {"passed": False, "metrics": [], "config": config, "details": {"error": str(error)[:400]}}
    ratio = objective / sign_optimum
    return {
        "passed": True,
        "metrics": [
            {"name": "gap_ppm", "value": int(ratio * 1_000_000), "direction": "max"},
            {"name": "matrix_area", "value": len(matrix) * len(matrix[0]), "direction": "min"},
            {"name": "certificate_bits", "value": _certificate_bits(left, right), "direction": "min"},
        ],
        "config": config,
        "details": {
            "matrix_shape": [len(matrix), len(matrix[0])],
            "vector_dimension": len(left[0]),
            "sign_optimum": sign_optimum,
            "vector_objective": f"{objective.numerator}/{objective.denominator}",
            "lower_bound": f"{ratio.numerator}/{ratio.denominator}",
        },
    }
