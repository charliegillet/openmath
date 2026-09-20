"""Evaluator for heilbronn-triangle.

Coordinates are read as exact decimals. Triangle areas are twice-signed
determinants in exact rational arithmetic, so the minimum is found without
rounding; only the final division by the container's area, which involves
sqrt(3), is done at 60 digits of precision. Containment is checked at the
same precision with a slack of 1e-12, because optimisers put points on the
slanted edges and doubles land a few 1e-17 outside them; the area is still
computed from the coordinates as given. There is no held-out data: a
configuration's value is a number anyone can recompute.
"""

import itertools
import json
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

import mpmath

mpmath.mp.dps = 60
SQRT3 = mpmath.sqrt(3)
CONTAINER_AREA_TWICE = SQRT3 / 2  # twice the area of the unit equilateral triangle
CONTAINMENT_SLACK = mpmath.mpf("1e-12")
MAX_DIGITS = 200
MIN_EXPONENT = -60


def _fail(error: str, **extra) -> dict:
    return {"passed": False, "metrics": [], "config": [], "details": {"error": error, **extra}}


def _read_points(path: Path, n: int) -> list[tuple[Fraction, Fraction]] | str:
    try:
        data = json.loads(path.read_text(), parse_float=Decimal, parse_int=Decimal)
    except (OSError, ValueError) as exc:
        return f"points.json is not valid JSON: {exc}"
    if not isinstance(data, list):
        return "points.json must be a JSON array of [x, y] pairs"
    if len(data) != n:
        return f"expected {n} points, got {len(data)}"
    points = []
    for i, item in enumerate(data):
        if not isinstance(item, list) or len(item) != 2:
            return f"point {i} must be a pair [x, y]"
        pair = []
        for value in item:
            if isinstance(value, bool) or not isinstance(value, (Decimal, str)):
                return f"point {i}: coordinates must be numbers or numeric strings, got {value!r}"
            try:
                number = Decimal(value)
            except (InvalidOperation, ValueError):
                return f"point {i}: {value!r} is not a number"
            if not number.is_finite():
                return f"point {i}: {value!r} is not a finite number"
            digits = number.as_tuple()
            if len(digits.digits) > MAX_DIGITS:
                return f"point {i}: at most {MAX_DIGITS} significant digits per coordinate"
            if number != 0 and (number.adjusted() > 0 or number.adjusted() < MIN_EXPONENT):
                return f"point {i}: {value!r} is outside the triangle or below 1e{MIN_EXPONENT}"
            pair.append(Fraction(number))
        points.append((pair[0], pair[1]))
    return points


def _inside(x: Fraction, y: Fraction) -> bool:
    mx, my = mpmath.mpf(x.numerator) / x.denominator, mpmath.mpf(y.numerator) / y.denominator
    slack = CONTAINMENT_SLACK
    return my >= -slack and my <= SQRT3 * mx + slack and my <= SQRT3 * (1 - mx) + slack


def eval(submission: Path, *, final: bool = False, n: int = 11) -> dict:
    path = submission / "points.json"
    if not path.is_file():
        return _fail("submission must contain points.json")
    points = _read_points(path, n)
    if isinstance(points, str):
        return _fail(points)

    outside = [i for i, (x, y) in enumerate(points) if not _inside(x, y)]
    if outside:
        return _fail(f"{len(outside)} point(s) lie outside the triangle: indices {outside[:10]}")

    if len(set(points)) != len(points):
        return _fail("two points coincide, so the minimum area is zero")

    smallest = None
    argmin = None
    for i, j, k in itertools.combinations(range(n), 3):
        (ax, ay), (bx, by), (cx, cy) = points[i], points[j], points[k]
        twice = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay))
        if smallest is None or twice < smallest:
            smallest, argmin = twice, (i, j, k)
            if twice == 0:
                break
    if smallest == 0:
        return _fail(f"points {argmin} are collinear, so the minimum area is zero")

    exact = mpmath.mpf(smallest.numerator) / smallest.denominator / CONTAINER_AREA_TWICE
    return {
        "passed": True,
        "metrics": [{"name": "min_area", "value": float(exact), "direction": "max"}],
        "config": [
            {"name": "n", "value": n, "primary": True},
            {"name": "region", "value": "unit equilateral triangle", "primary": False},
        ],
        "details": {
            "min_area_30_digits": mpmath.nstr(exact, 30),
            "smallest_triangle": list(argmin),
        },
    }
