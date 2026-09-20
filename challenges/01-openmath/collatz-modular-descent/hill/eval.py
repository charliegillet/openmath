"""Exact evaluator for accelerated-Collatz residue-class descent certificates."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


HILL = Path(__file__).resolve().parent
MAX_BYTES = 262_144
MAX_RULES = 512
MAX_POWER = 32
MAX_STEPS = 24
MAX_EXPONENT = 32


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _v2(value: int) -> int:
    count = 0
    while value % 2 == 0:
        count += 1
        value //= 2
    return count


def _load_rules(submission: Path):
    path = Path(submission) / "solution.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("submission must contain a regular solution.json")
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError(f"solution.json exceeds the {MAX_BYTES}-byte limit")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"rules"} or not isinstance(data["rules"], list):
        raise ValueError('solution.json must contain only a list-valued "rules" field')
    if not 1 <= len(data["rules"]) <= MAX_RULES:
        raise ValueError(f"rules must contain between 1 and {MAX_RULES} entries")
    rules = []
    seen = set()
    for index, item in enumerate(data["rules"]):
        if not isinstance(item, dict) or set(item) != {"modulus_power", "residue", "exponents"}:
            raise ValueError(f"rules[{index}] must contain exactly modulus_power, residue, and exponents")
        k, residue, exponents = item["modulus_power"], item["residue"], item["exponents"]
        if type(k) is not int or not 2 <= k <= MAX_POWER:
            raise ValueError(f"rules[{index}].modulus_power must be an integer from 2 through {MAX_POWER}")
        if type(residue) is not int or not 0 < residue < (1 << k) or residue % 2 == 0:
            raise ValueError(f"rules[{index}].residue must be an odd integer in (0, 2^k)")
        if not isinstance(exponents, list) or not 1 <= len(exponents) <= MAX_STEPS:
            raise ValueError(f"rules[{index}].exponents must contain 1 through {MAX_STEPS} integers")
        if any(type(exponent) is not int or not 1 <= exponent <= MAX_EXPONENT for exponent in exponents):
            raise ValueError(f"rules[{index}].exponents must contain integers from 1 through {MAX_EXPONENT}")
        key = (k, residue, tuple(exponents))
        if key in seen:
            raise ValueError(f"rules[{index}] duplicates a previous rule")
        seen.add(key)
        rules.append(key)
    return rules


def _verify_rule(rule):
    k, residue, exponents = rule
    total_exponent = sum(exponents)
    if k < total_exponent + 1:
        raise ValueError(
            f"rule n ≡ {residue} (mod 2^{k}) needs k >= {total_exponent + 1} to stabilize its valuation pattern"
        )
    current = residue
    for step, expected in enumerate(exponents, 1):
        numerator = 3 * current + 1
        observed = _v2(numerator)
        if observed != expected:
            raise ValueError(
                f"rule n ≡ {residue} (mod 2^{k}) has v2(3x+1)={observed}, not {expected}, at step {step}"
            )
        current = numerator >> expected
    step_count = len(exponents)
    denominator = 1 << total_exponent
    numerator_factor = 3**step_count
    if numerator_factor >= denominator:
        raise ValueError(f"rule n ≡ {residue} (mod 2^{k}) is not contractive")
    if current >= residue:
        raise ValueError(f"rule n ≡ {residue} (mod 2^{k}) does not strictly descend at its least representative")
    return {
        "modulus_power": k,
        "residue": residue,
        "margin": Fraction(denominator - numerator_factor, denominator),
    }


def _load_targets(final: bool):
    filename = "test.json" if final else "validation.json"
    data = json.loads((HILL / "private" / filename).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"targets"} or not isinstance(data["targets"], list):
        raise ValueError("private target schema is invalid")
    targets = []
    seen = set()
    for item in data["targets"]:
        if not isinstance(item, dict) or set(item) != {"modulus_power", "residue", "weight"}:
            raise ValueError("private target schema is invalid")
        k, residue, weight = item["modulus_power"], item["residue"], item["weight"]
        if type(k) is not int or not 8 <= k <= 12 or type(residue) is not int or residue % 2 == 0:
            raise ValueError("private target contains an invalid residue class")
        if not 0 < residue < (1 << k) or type(weight) is not int or not 1 <= weight <= 1000:
            raise ValueError("private target contains an invalid weight")
        key = (k, residue)
        if key in seen:
            raise ValueError("private target contains a duplicate residue class")
        seen.add(key)
        targets.append((k, residue, weight))
    if not targets:
        raise ValueError("private target set is empty")
    return targets


def _covers(rule, target) -> bool:
    target_power, target_residue, _ = target
    return target_power >= rule["modulus_power"] and target_residue % (1 << rule["modulus_power"]) == rule["residue"]


def _config(final: bool):
    return [
        {"name": "certificate", "value": "accelerated-collatz-residue-descent", "primary": True},
        {"name": "target_family", "value": "private-odd-dyadic-residues", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]


def eval(submission: Path, *, final: bool = False) -> dict:
    config = _config(final)
    try:
        verified = [_verify_rule(rule) for rule in _load_rules(submission)]
        targets = _load_targets(final)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, RecursionError) as error:
        return {"passed": False, "metrics": [], "config": config, "details": {"error": str(error)[:400]}}
    covered_weight = 0
    margins = []
    for target in targets:
        matches = [rule for rule in verified if _covers(rule, target)]
        if matches:
            covered_weight += target[2]
            margins.append(max(rule["margin"] for rule in matches))
    total_weight = sum(target[2] for target in targets)
    coverage_ppm = covered_weight * 1_000_000 // total_weight
    min_descent_ppm = int(min(margins) * 1_000_000) if margins else 0
    return {
        "passed": True,
        "metrics": [
            {"name": "coverage_ppm", "value": coverage_ppm, "direction": "max"},
            {"name": "min_descent_ppm", "value": min_descent_ppm, "direction": "max"},
            {"name": "rule_count", "value": len(verified), "direction": "min"},
        ],
        "config": config,
        "details": {
            "rules_verified": len(verified),
            "private_targets_scored": len(targets),
            "covered_weight": covered_weight,
            "total_weight": total_weight,
        },
    }
