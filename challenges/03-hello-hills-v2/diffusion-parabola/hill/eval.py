"""Evaluator for diffusion-parabola.

The climber can read this file. That is deliberate: transparency about how you
are judged is a feature. The task is an open generative-modeling problem -- the training generator is public. Official validation and final samples use
distinct seeds stored in private evaluation data.

The submission is a directory holding `solution.py`, which must expose:

    def train_and_sample(data, *, steps, n_samples, seed):
        # data: np.ndarray (N, 2) training points
        # returns: np.ndarray (n_samples, 2) generated points

The evaluator generates the parabola train/test sets, imports the submission,
passes it the requested `steps` training budget, and scores the returned samples against the
held-out test set with the Chamfer distance (lower is better).
"""

import importlib
import json
import sys
from pathlib import Path

import numpy as np

HILL = Path(__file__).resolve().parent

# Fixed problem constants. These are baked in so every run is comparable.
N_TRAIN = 2000            # training points handed to the submission
N_TEST = 2000             # held-out points the samples are scored against
TRAIN_SEED = 0            # seed for the training split (same in every mode)
SUBMISSION_SEED = 0       # seed passed to the submission for its own RNG


def generate_parabola(n: int, seed: int) -> np.ndarray:
    """Points on a noisy parabola y = x**2 + N(0, 0.1), x ~ U(-2, 2)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2, 2, n)
    y = x ** 2 + rng.normal(0, 0.1, n)
    return np.stack([x, y], axis=1)


def chamfer_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Symmetric Chamfer distance between two 2D point sets (mean nearest)."""
    a2 = (a ** 2).sum(1)[:, None]
    b2 = (b ** 2).sum(1)[None, :]
    d2 = np.maximum(a2 + b2 - 2.0 * a @ b.T, 0.0)
    d = np.sqrt(d2)
    return float(d.min(axis=1).mean() + d.min(axis=0).mean())


def _config(steps: int, n_samples: int) -> list[dict]:
    # Steps and sample count are primary: different settings rank in separate
    # research-progress boards and are never compared to each other. The
    # validation/test split is tracked by the platform via the `final` flag,
    # so there is deliberately no `mode` config entry here.
    return [
        {"name": "steps", "value": steps, "primary": True},
        {"name": "n_samples", "value": n_samples, "primary": True},
    ]


def _fail(steps: int, n_samples: int, error: str) -> dict:
    return {
        "passed": False,
        "metrics": [],
        "config": _config(steps, n_samples),
        "details": {"error": error},
    }


def eval(submission: Path, *, final: bool = False,
         steps: int = 10000, n_samples: int = 2000) -> dict:
    steps = int(steps)
    n_samples = int(n_samples)

    submission = Path(submission)
    solution_path = submission / "solution.py"
    if not solution_path.is_file():
        return _fail(steps, n_samples, "submission must contain solution.py")

    # Deterministic data. Train is fixed; the test split depends only on the mode.
    data_train = generate_parabola(N_TRAIN, seed=TRAIN_SEED)
    try:
        seeds = json.loads((HILL / "private" / "seeds.json").read_text())
    except FileNotFoundError:
        return _fail(steps, n_samples,
                     "Official scoring requires private evaluation data. "
                     "Use AutoLab or an authorized complete hill bundle.")
    test_seed = seeds["test" if final else "validation"]
    data_test = generate_parabola(N_TEST, seed=test_seed)

    # Import the submission fresh (drop any cached module of the same name).
    sub_dir = str(submission.resolve())
    sys.path.insert(0, sub_dir)
    try:
        sys.modules.pop("solution", None)
        try:
            solution = importlib.import_module("solution")
            solution = importlib.reload(solution)
        except Exception as error:  # noqa: BLE001
            return _fail(steps, n_samples, f"could not import solution.py: {error!r}")

        if not hasattr(solution, "train_and_sample"):
            return _fail(steps, n_samples,
                         "solution.py must define train_and_sample(data, *, steps, n_samples, seed)")

        try:
            generated = solution.train_and_sample(
                data_train, steps=steps, n_samples=n_samples, seed=SUBMISSION_SEED
            )
        except Exception as error:  # noqa: BLE001
            return _fail(steps, n_samples, f"train_and_sample raised: {error!r}")
    finally:
        try:
            sys.path.remove(sub_dir)
        except ValueError:
            pass
        sys.modules.pop("solution", None)

    # Validate the returned samples before scoring.
    try:
        generated = np.asarray(generated, dtype=float)
    except Exception as error:  # noqa: BLE001
        return _fail(steps, n_samples, f"returned samples are not array-like: {error!r}")

    if generated.shape != (n_samples, 2):
        return _fail(steps, n_samples,
                     f"expected samples of shape ({n_samples}, 2), got {generated.shape}")
    if not np.all(np.isfinite(generated)):
        return _fail(steps, n_samples, "returned samples contain NaN or inf")

    cd = chamfer_distance(generated, data_test)

    return {
        "passed": True,
        "metrics": [{"name": "chamfer_distance", "value": cd, "direction": "min"}],
        "config": _config(steps, n_samples),
        "details": {
            "n_train": N_TRAIN,
            "n_test": N_TEST,
            "final": bool(final),
        },
    }
