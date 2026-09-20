"""Exact weighted blow-up certificates for K4 Ramsey multiplicity.

Submission code is never executed. Repeated template indices denote distinct
vertices inside a cluster. See LIFTING.md for the asymptotic argument.
"""
from __future__ import annotations
import json
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 4_194_304
MAX_BLOCKS = 1024
MAX_WEIGHT = 65535
TIME_LIMIT_S = 480
SCALE = 10**12
# McKay improvement in the final note of arXiv:2206.04036v3.
REFERENCE = Fraction(10486266368, 768**4)


def _unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_unique)


def _validate(data):
    if not isinstance(data, dict) or set(data) != {"schema", "weights", "red_rows"}:
        raise ValueError("solution must have exactly schema, weights, red_rows")
    if data["schema"] != "weighted-two-color-blowup-v1":
        raise ValueError("unsupported schema")
    weights, rows = data["weights"], data["red_rows"]
    if not isinstance(weights, list) or not 1 <= len(weights) <= MAX_BLOCKS:
        raise ValueError(f"weights must contain 1..{MAX_BLOCKS} entries")
    if any(type(w) is not int or not 1 <= w <= MAX_WEIGHT for w in weights):
        raise ValueError(f"weights must be integers in 1..{MAX_WEIGHT}; booleans are invalid")
    n = len(weights)
    if not isinstance(rows, list) or len(rows) != n:
        raise ValueError("red_rows must have one bit string per block")
    if any(not isinstance(row, str) or len(row) != n or set(row) - {"0", "1"} for row in rows):
        raise ValueError("red_rows must be square binary strings")
    if any(rows[i][j] != rows[j][i] for i in range(n) for j in range(i)):
        raise ValueError("red_rows must be symmetric")
    common = 0
    for w in weights:
        common = gcd(common, w)
    return [w // common for w in weights], rows


def _mask_sum(values):
    """Exact weighted bit-set sum, with a uniform-weight fast path."""
    if len(set(values)) == 1:
        value = values[0]
        return lambda mask: mask.bit_count() * value
    planes = []
    for b in range(max(values).bit_length()):
        mask = sum(1 << i for i, w in enumerate(values) if (w >> b) & 1)
        if mask:
            planes.append((mask, 1 << b))
    return lambda mask: sum((mask & plane).bit_count() * scale for plane, scale in planes)


def _density(weights, rows, *, deadline=None):
    """Exact red and blue hom(K4) numerators with denominator Q**4.

    Index multiplicity types 4, 3+1, 2+2, 2+1+1 and 1+1+1+1 have
    multinomial coefficients 1, 4, 6, 12 and 24 respectively.
    """
    n = len(weights)
    sums = _mask_sum(weights)
    totals = []
    for color in "10":
        loops = [int(rows[i][i] == color) for i in range(n)]
        adj = [sum(1 << j for j in range(n) if i != j and rows[i][j] == color) for i in range(n)]
        higher = [mask & ~((1 << (i + 1)) - 1) for i, mask in enumerate(adj)]
        square_loop_sum = _mask_sum([w*w*loop for w, loop in zip(weights, loops)])
        total = sum(w**4 * loop for w, loop in zip(weights, loops))
        for i, wi in enumerate(weights):
            if deadline is not None and monotonic() > deadline:
                raise ValueError("exact verification exceeded the 480-second evaluator budget")
            if loops[i]:
                total += 4 * wi**3 * sums(adj[i])
            js = higher[i]
            while js:
                bit = js & -js
                j = bit.bit_length() - 1
                js ^= bit
                wj = weights[j]
                wij = wi * wj
                if loops[i] and loops[j]:
                    total += 6 * wij**2
                common = higher[i] & higher[j]
                if not common:
                    continue
                total += 12 * wij * ((wi*loops[i] + wj*loops[j])*sums(common) + square_loop_sum(common))
                ks = common
                while ks:
                    bit = ks & -ks
                    k = bit.bit_length() - 1
                    ks ^= bit
                    if ks:
                        total += 24 * wij * weights[k] * sums(ks & adj[k])
        totals.append(total)
    return totals[0], totals[1], sum(weights)**4


def _oracle(weights, rows):
    """Independent literal ordered-tuple oracle for tiny fixtures."""
    red = blue = 0
    for a, b, c, d in product(range(len(weights)), repeat=4):
        colors = (rows[a][b], rows[a][c], rows[a][d], rows[b][c], rows[b][d], rows[c][d])
        mass = weights[a]*weights[b]*weights[c]*weights[d]
        if all(x == "1" for x in colors):
            red += mass
        elif all(x == "0" for x in colors):
            blue += mass
    return red, blue, sum(weights)**4


def _audit(final):
    suite = _read(ROOT / "private" / ("test.json" if final else "validation.json"))
    for fixture in suite["fixtures"]:
        w, a = _validate(fixture)
        if _density(w, a) != _oracle(w, a):
            raise RuntimeError("internal counting audit failed")
    return suite["id"]


def _metrics(red, blue, denominator):
    density = Fraction(red + blue, denominator)
    beaten = density < REFERENCE
    return density, beaten, [
        {"name": "reference_beaten", "value": int(beaten), "direction": "max"},
        {"name": "density_ppt", "value": (SCALE*density.numerator + density.denominator - 1)//density.denominator, "direction": "min"},
    ]


def eval(submission: Path, *, final: bool = False) -> dict:
    config = [
        {"name": "protocol", "value": "k4-weighted-blowup-v1", "primary": True},
        {"name": "reference", "value": "10486266368/768^4", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]
    try:
        directory = Path(submission)
        path = directory / "solution.json"
        if directory.is_symlink() or path.is_symlink() or not path.is_file():
            raise ValueError("a regular, non-symlink solution.json is required")
        if path.stat().st_size > MAX_BYTES:
            raise ValueError("solution.json exceeds the 4 MiB limit")
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            raise ValueError("solution.json exceeds the 4 MiB limit")
        weights, rows = _validate(json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique))
        audit_id = _audit(final)
        red, blue, denominator = _density(weights, rows, deadline=monotonic() + TIME_LIMIT_S)
        density, beaten, metrics = _metrics(red, blue, denominator)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        return {"passed": False, "metrics": [], "config": config, "details": {"error": str(error)[:300]}}
    gap = REFERENCE - density
    return {
        "passed": True, "metrics": metrics, "config": config,
        "details": {
            "exact_density": f"{density.numerator}/{density.denominator}",
            "red_numerator": str(red), "blue_numerator": str(blue), "raw_denominator": str(denominator),
            "exact_reference": f"{REFERENCE.numerator}/{REFERENCE.denominator}",
            "exact_reference_gap": f"{gap.numerator}/{gap.denominator}",
            "template_blocks": len(weights), "weight_sum": sum(weights),
            "asymptotic_bound": "c4 <= exact_density by the weighted blow-up lemma",
            "target_achieved": beaten, "parent_problem_resolved": False,
            "research_status": "candidate improvement on the frozen reference; novelty and formal review required" if beaten else "valid construction; no improvement on the frozen reference",
            "audit_suite": audit_id,
            "trust_boundary": "Python integer certificate check plus mathematical lifting lemma; no approved proof-assistant acceptance is asserted",
        },
    }
