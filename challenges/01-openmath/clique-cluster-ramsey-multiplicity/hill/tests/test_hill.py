"""Independent mathematical checks and adversarial certificate tests."""
import importlib.util
import json
import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ramsey_hill_eval", ROOT / "eval.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


def payload(weights, rows):
    return {"schema":"weighted-two-color-blowup-v1", "weights":weights, "red_rows":rows}


def submit(tmp_path, data, final=False):
    (tmp_path / "solution.json").write_text(json.dumps(data), encoding="utf-8")
    return E.eval(tmp_path, final=final)


def test_baseline_exact_and_modes_agree():
    a = E.eval(ROOT / "examples" / "baseline")
    b = E.eval(ROOT / "examples" / "baseline", final=True)
    assert a["passed"] and b["passed"]
    assert a["details"]["exact_density"] == "1/8"
    assert a["metrics"] == b["metrics"] == [
        {"name":"reference_beaten","value":0,"direction":"max"},
        {"name":"density_ppt","value":125_000_000_000,"direction":"min"},
    ]
    assert a["details"]["audit_suite"] != b["details"]["audit_suite"]
    assert not a["details"]["target_achieved"]
    assert not a["details"]["parent_problem_resolved"]


def test_published_768_seed_reproduces_paper_and_is_not_new_progress():
    report = E.eval(ROOT / "examples" / "published_cayley_768", final=True)
    assert report["passed"]
    assert Fraction(report["details"]["exact_density"]) == Fraction(4551721, 2**24 * 9)
    assert report["details"]["template_blocks"] == 768
    assert report["metrics"][0]["value"] == 0
    assert not report["details"]["target_achieved"]
    assert not report["details"]["parent_problem_resolved"]


def test_counter_matches_independent_tuple_oracle():
    rng = random.Random(514)
    for n in range(1, 8):
        for _ in range(7):
            a = [["0"]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1):
                    a[i][j] = a[j][i] = str(rng.randrange(2))
            rows = ["".join(r) for r in a]
            w = [rng.randrange(1,12) for _ in range(n)]
            assert E._density(w,rows) == E._oracle(w,rows)


def test_loops_and_collision_types_counted():
    for n in (1,2,4,7):
        w = list(range(1,n+1))
        red,blue,d = E._density(w,["1"*n]*n)
        assert (red,blue) == (d,0)
        red,blue,d = E._density(w,["0"*n]*n)
        assert (red,blue) == (0,d)


def test_relabelling_colors_scaling_and_refinement():
    w, rows = [2,3,5], ["110","100","001"]
    red, blue, d = E._density(w,rows)
    assert E._density(w,[r.translate(str.maketrans("01","10")) for r in rows]) == (blue,red,d)
    p = [2,0,1]
    assert E._density([w[i] for i in p],["".join(rows[i][j] for j in p) for i in p]) == (red,blue,d)
    assert E._density([2*x for x in w],rows) == (16*red,16*blue,16*d)
    p = [0,0,1,2]
    assert E._density([1,1,3,5],["".join(rows[i][j] for j in p) for i in p]) == (red,blue,d)


def test_finite_blowups_obey_collision_error_bound():
    w, rows = [1,2,1],["110","100","001"]
    red,blue,d = E._density(w,rows)
    limit = Fraction(red+blue,d)
    for t in (1,2,3,4):
        blocks = [i for i,wi in enumerate(w) for _ in range(t*wi)]
        good = count = 0
        for indices in combinations(range(len(blocks)),4):
            colors = {rows[blocks[i]][blocks[j]] for i,j in combinations(indices,2)}
            good += len(colors)==1
            count += 1
        assert abs(Fraction(good,count)-limit) <= Fraction(6,len(blocks))


def test_reference_uses_exact_strict_inequality():
    b=E.REFERENCE
    assert E._metrics(b.numerator,0,b.denominator)[1] is False
    below=b-Fraction(1,10**30)
    assert E._metrics(below.numerator,0,below.denominator)[1] is True
    assert E._metrics(b.numerator+1,0,b.denominator)[1] is False


@pytest.mark.parametrize("bad",[
    {}, payload([],[]), payload([True],["0"]), payload([0],["0"]),
    payload([-1],["0"]),payload([65536],["0"]), payload([1],["2"]),
    payload([1,1],["00","10"]),payload([1],["00"]),
    dict(payload([1],["0"]),claimed_score=0),
])
def test_malformed_rejected(tmp_path,bad):
    assert not submit(tmp_path,bad)["passed"]


def test_duplicate_keys_rejected(tmp_path):
    (tmp_path/"solution.json").write_text('{"schema":"x","schema":"y"}')
    assert not E.eval(tmp_path)["passed"]


def test_submission_code_ignored(tmp_path):
    (tmp_path/"eval.py").write_text('raise RuntimeError("do not execute")')
    (tmp_path/"sitecustomize.py").write_text('raise RuntimeError("do not execute")')
    assert submit(tmp_path,payload([1],["0"]))["passed"]


def test_time_budget_enforced():
    with pytest.raises(ValueError,match="budget"):
        E._density([1],["0"],deadline=-1)
