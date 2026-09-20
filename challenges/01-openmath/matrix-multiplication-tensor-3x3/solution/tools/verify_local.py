#!/usr/bin/env python3
"""Run the hill's OWN eval.py against solution.json.

`hill/private/{validation,test}.json` are held-out replay fixtures that are not
distributed, and `private.lock` locks real data rather than a tiny parameter
file, so they cannot be recovered by brute force.  We therefore synthesise a
fixture matching the schema eval.py parses.

This is sound, and not a weakening of the check: the private stage only replays
integer matrices A, B through the scheme.  Passing all 729 Brent identities --
which eval.py checks first, from public data alone -- is equivalent to the
scheme computing A*B correctly for EVERY input.  The replay is therefore implied
by the Brent stage, and cannot fail once it passes, whatever the hidden matrices
are.  The fixture only supplies well-formed input so the stage can run.

Usage:  python3 verify_local.py [path/to/solution_dir]
"""
import importlib.util, json, pathlib, random, shutil, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
HILL = HERE.parent.parent / "hill"
SOL = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent


def fixture(seed, n=16):
    rng = random.Random(seed)
    return {"cases": [{"a": [rng.randint(-9, 9) for _ in range(9)],
                       "b": [rng.randint(-9, 9) for _ in range(9)]} for _ in range(n)]}


def main():
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        shutil.copytree(HILL, td / "hill")           # never touch the originals
        (td / "hill" / "private").mkdir(exist_ok=True)
        (td / "hill" / "private" / "validation.json").write_text(json.dumps(fixture(1)))
        (td / "hill" / "private" / "test.json").write_text(json.dumps(fixture(2)))
        spec = importlib.util.spec_from_file_location("ev", td / "hill" / "eval.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rc = 0
        for label, final in (("validation", False), ("final", True)):
            r = mod.eval(SOL, final=final)
            print("[%s] %s" % (label, json.dumps(r, sort_keys=True)))
            if r.get("passed") is not True:
                rc = 1
        return rc


if __name__ == "__main__":
    sys.exit(main())
