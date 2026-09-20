"""Local harness: runs the hill's REAL eval.py (unmodified) on ../solution.

eval.py needs private/validation.json + private/test.json which are withheld
from the distributed hill. We therefore point eval.py's ROOT at ./audit/, which
holds locally authored arithmetic fixtures. Those fixtures do not affect the
score: per the hill README they only audit the evaluator's own counting code
(_density vs the independent _oracle). All scoring numbers come from the
unmodified eval.py.
"""
import importlib.util
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
HILL = HERE.parent / "hill" / "eval.py"

spec = importlib.util.spec_from_file_location("hill_eval", HILL)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

# redirect the withheld private fixtures to our own audit directory
E.ROOT = HERE / "audit"

submission = HERE if len(sys.argv) < 2 else pathlib.Path(sys.argv[1])
t = time.time()
report = E.eval(submission, final="--final" in sys.argv)
elapsed = time.time() - t
print(json.dumps(report, indent=2))
print("elapsed_seconds=%.2f" % elapsed)
