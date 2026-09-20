"""Baseline: unigram char distribution (add-one smoothing) fit on train.txt.

Ignores the prefix: a valid but weak causal model."""

import json
import math
from pathlib import Path

_COUNTS = json.loads(Path(__file__).with_name("counts.json").read_text())
_TOTAL = sum(_COUNTS.values())
_V = len(_COUNTS) + 1
_SMOOTHING = 1.0
_DIST = {ch: math.log((n + _SMOOTHING) / (_TOTAL + _SMOOTHING * _V)) for ch, n in _COUNTS.items()}


def predict_next(prefix):
    return _DIST
