from pathlib import Path
from hills import run_evaluator

HILL = Path(__file__).resolve().parent.parent

def test_sorry_is_rejected():
    r = run_evaluator(HILL, HILL / 'examples' / 'baseline')
    assert not r['passed']
