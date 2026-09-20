"""Evaluator for shakespeare: bits-per-character of a causal character-level LM.

The submission ships `model.py` exposing

    predict_next(prefix: str) -> dict[str, float]

The evaluator calls it once per character, passing ONLY the text seen so far
(text[:i]) and never the character being predicted. `predict_next` returns the
model's distribution over the next character as {candidate_char: natural-log-
probability}. bits/char is computed from the log-probability the model gave to
the character that actually appears.

Because the model is handed only the prefix, it physically cannot read the
current character — causality is structural, not probed. The only remaining
check is that each returned distribution is a real distribution
(sum_c P(c | prefix) <= 1): claiming probability 1 for a *guessed* character is
high variance and, being unable to see the answer, loses on average.

The prefix is passed in order (empty, then one char longer each call), so an
efficient model can keep incremental state across calls; a model that rescans
the whole prefix every call is correct but slow (bounded by the watchdog).
"""

import importlib.util
import math
import sys
from pathlib import Path

HILL = Path(__file__).resolve().parent
FLOOR_LOGPROB = math.log(1e-8)  # cap the penalty for a zero-probability char


def _reject(error: str) -> dict:
    return {"passed": False, "metrics": [], "config": [], "details": {"error": error}}


def _load_model(submission: Path):
    spec = importlib.util.spec_from_file_location("submitted_model", submission / "model.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["submitted_model"] = module
    spec.loader.exec_module(module)
    return module


def _prob_of_actual(dist, actual: str) -> float:
    """Validate one prediction's distribution; return P(actual next char)."""
    if not isinstance(dist, dict):
        raise ValueError("predict_next must return a dict {char: log-prob}")
    total = 0.0
    p_actual = 0.0
    for c, lp in dist.items():
        lp = float(lp)
        if not math.isfinite(lp) or lp > 0.0:
            raise ValueError("log-probs must be finite and <= 0")
        p = math.exp(lp)
        total += p
        if c == actual:
            p_actual = p
    if total > 1.0 + 1e-4:
        raise ValueError(f"distribution sums to {total:.4f} > 1 (not normalized)")
    return p_actual


def eval(submission: Path, *, final: bool = False, eval_chars: int = 8000) -> dict:
    if not (submission / "model.py").is_file():
        return _reject("submission must contain model.py")

    val = (HILL / "private" / "val.txt").read_text()
    half = len(val) // 2
    text = (val[half:] if final else val[:half])[:eval_chars]
    if len(text) < 2:
        return _reject("evaluation slice too short")

    try:
        model = _load_model(submission)
        total_logprob = 0.0
        for i in range(len(text)):
            dist = model.predict_next(text[:i])  # prefix ONLY — cannot see text[i]
            p = _prob_of_actual(dist, text[i])
            total_logprob += max(math.log(p) if p > 0.0 else FLOOR_LOGPROB, FLOOR_LOGPROB)
        bpc = -total_logprob / (len(text) * math.log(2))
    except Exception as exc:  # noqa: BLE001 — the report carries the reason
        return _reject(f"{type(exc).__name__}: {exc}")

    return {
        "passed": True,
        "metrics": [{"name": "bpc", "value": bpc, "direction": "min"}],
        "config": [
            {"name": "mode", "value": "test" if final else "validation", "primary": True},
            {"name": "eval_chars", "value": eval_chars, "primary": True},
        ],
        "details": {"chars_scored": len(text)},
    }
