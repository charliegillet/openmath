"""Exact verifier for 3 by 3 matrix-multiplication tensor decompositions.

Candidates are data only: this evaluator never imports or executes submission
code. It checks every Brent identity over Q, then replays private regression
matrices for the selected evaluation mode.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HILL = Path(__file__).resolve().parent
MAX_BYTES = 262_144
MAX_RANK = 40
MAX_MAGNITUDE = 1_000_000


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _coefficient(value, label: str) -> Fraction:
    if type(value) is int:
        numerator, denominator = value, 1
    elif (
        isinstance(value, list)
        and len(value) == 2
        and type(value[0]) is int
        and type(value[1]) is int
    ):
        numerator, denominator = value
    else:
        raise ValueError(f"{label} must be an integer or [numerator, denominator]")
    if denominator < 1 or abs(numerator) > MAX_MAGNITUDE or denominator > MAX_MAGNITUDE:
        raise ValueError(f"{label} is outside the coefficient bounds")
    return Fraction(numerator, denominator)


def _factor(data, name: str):
    if not isinstance(data, list) or not 1 <= len(data) <= MAX_RANK:
        raise ValueError(f"{name} must contain between 1 and {MAX_RANK} rows")
    rows = []
    for row_index, row in enumerate(data):
        if not isinstance(row, list) or len(row) != 9:
            raise ValueError(f"{name}[{row_index}] must have exactly 9 coefficients")
        rows.append([_coefficient(value, f"{name}[{row_index}][{index}]") for index, value in enumerate(row)])
    return rows


def _load(submission: Path):
    path = Path(submission) / "solution.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("submission must contain a regular, non-symlink solution.json")
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError("solution.json exceeds the 262144-byte size limit")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"u", "v", "w"}:
        raise ValueError('solution.json must contain only "u", "v", and "w"')
    u, v, w = _factor(data["u"], "u"), _factor(data["v"], "v"), _factor(data["w"], "w")
    if len(u) != len(v) or len(u) != len(w):
        raise ValueError("u, v, and w must have the same row count")
    return u, v, w


def _target(a_index: int, b_index: int, c_index: int) -> int:
    row, inner = divmod(a_index, 3)
    b_inner, column = divmod(b_index, 3)
    return int(inner == b_inner and c_index == 3 * column + row)


def _check_brent(u, v, w):
    for a_index in range(9):
        for b_index in range(9):
            for c_index in range(9):
                value = sum(
                    (u[term][a_index] * v[term][b_index] * w[term][c_index] for term in range(len(u))),
                    Fraction(0),
                )
                expected = _target(a_index, b_index, c_index)
                if value != expected:
                    raise ValueError(
                        f"Brent identity fails at A[{a_index}], B[{b_index}], C[{c_index}]: "
                        f"got {value}, expected {expected}"
                    )


def _private_cases(final: bool):
    filename = "test.json" if final else "validation.json"
    data = json.loads((HILL / "private" / filename).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"cases"} or not isinstance(data["cases"], list):
        raise ValueError("private replay schema is invalid")
    cases = []
    for index, case in enumerate(data["cases"]):
        if not isinstance(case, dict) or set(case) != {"a", "b"}:
            raise ValueError("private replay schema is invalid")
        a, b = case["a"], case["b"]
        if not all(isinstance(matrix, list) and len(matrix) == 9 for matrix in (a, b)):
            raise ValueError("private replay matrix has invalid shape")
        if any(type(value) is not int for value in [*a, *b]):
            raise ValueError("private replay matrix has a non-integer entry")
        cases.append((a, b, index))
    if not cases:
        raise ValueError("private replay set is empty")
    return cases


def _replay(u, v, w, a, b):
    products = []
    for term in range(len(u)):
        left = sum((u[term][index] * a[index] for index in range(9)), Fraction(0))
        right = sum((v[term][index] * b[index] for index in range(9)), Fraction(0))
        products.append(left * right)
    result = [sum((w[term][index] * products[term] for term in range(len(u))), Fraction(0)) for index in range(9)]
    expected = [Fraction(0) for _ in range(9)]
    for row in range(3):
        for column in range(3):
            expected[3 * column + row] = sum(
                (a[3 * row + inner] * b[3 * inner + column] for inner in range(3)),
                Fraction(0),
            )
    if result != expected:
        raise ValueError("private arithmetic replay failed")


def _config(final: bool):
    return [
        {"name": "tensor", "value": "3x3-general-matrix-multiplication", "primary": True},
        {"name": "coefficient_domain", "value": "exact-rationals", "primary": True},
        {"name": "verification", "value": "729-brent-identities", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]


def eval(submission: Path, *, final: bool = False) -> dict:
    config = _config(final)
    try:
        u, v, w = _load(submission)
        _check_brent(u, v, w)
        for a, b, _ in _private_cases(final):
            _replay(u, v, w, a, b)
    except (OSError, UnicodeDecodeError, ValueError, TypeError, RecursionError, ZeroDivisionError) as error:
        return {
            "passed": False,
            "metrics": [],
            "config": config,
            "details": {"error": str(error)[:300]},
        }
    support = sum(value != 0 for factor in (u, v, w) for row in factor for value in row)
    return {
        "passed": True,
        "metrics": [
            {"name": "rank", "value": len(u), "direction": "min"},
            {"name": "support", "value": support, "direction": "min"},
        ],
        "config": config,
        "details": {
            "brent_identities_checked": 729,
            "private_replays_checked": len(_private_cases(final)),
            "coefficient_domain": "Q",
        },
    }
