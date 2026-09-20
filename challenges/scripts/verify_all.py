#!/usr/bin/env python3
"""Verify every solved hill in this archive against the hill's OWN evaluator.

For each `<list>/<hill>/solution/`, this:
  1. copies `hill/` to a scratch directory (never touches the originals),
  2. tries to reconstruct the hidden `private/*.json` from the size+sha256 that
     `private.lock` publishes (tiny parameter files only),
  3. imports the hill's real `eval.py` and runs `eval(solution, final=False/True)`,
  4. prints the metrics verbatim.

Usage:
    python3 scripts/verify_all.py [--hill <slug-substring>] [--quiet]

Exit status is 0 only if every checked solution returned passed=True.
"""
import argparse, hashlib, importlib.util, json, pathlib, re, shutil, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Serialisations tried when recovering a tiny hidden parameter file.
# Note: AutoLab writes these compactly, with NO space after the colon.
SHAPES = [
    '{{"step_limit":{n}}}\n', '{{"step_limit": {n}}}\n',
    '{{"step_limit":{n}}}', '{{"step_limit": {n}}}',
    '{{"limit":{n}}}\n', '{{"budget":{n}}}\n',
    '{{"max_steps":{n}}}\n', '{{"seed":{n}}}\n',
]
MAX_TRIES = 2_000_000   # eval.py itself asserts budgets <= 2e6


def recover(lock_path: pathlib.Path, outdir: pathlib.Path):
    """Reconstruct every locked file we can, by brute force over small ints."""
    recovered, failed = {}, []
    try:
        entries = json.loads(lock_path.read_text()).get("entries", [])
    except Exception:
        return recovered, failed
    for e in entries:
        want, size, rel = e["sha256"], e.get("size"), e["path"]
        hit = None
        tries = 0
        for shape in SHAPES:
            fixed = len(shape.format(n=0))          # length with a 1-digit number
            digits = None if size is None else size - (fixed - 1)
            if digits is None or not (1 <= digits <= 9):
                continue
            lo, hi = 10 ** (digits - 1), 10 ** digits
            # Scan upward from the smallest legal value, bounded: budgets tend to be
            # small and round, and an unbounded shape must not hang the verifier.
            for n in range(lo, min(hi, lo + MAX_TRIES)):
                s = shape.format(n=n)
                tries += 1
                if len(s) == size and hashlib.sha256(s.encode()).hexdigest() == want:
                    hit = s
                    break
            if hit:
                break
        if hit:
            dest = outdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(hit)
            recovered[rel] = hit.strip()
        else:
            failed.append(rel)
    return recovered, failed


def run_hill(hilldir: pathlib.Path, quiet=False):
    hill, sol = hilldir / "hill", hilldir / "solution"
    if not sol.exists() or not any(sol.iterdir()):
        return None
    if not (hill / "eval.py").exists():
        return {"hill": hilldir.name, "error": "no hill/eval.py"}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        shutil.copytree(hill, td / "hill")
        rec, failed = recover(td / "hill" / "private.lock", td / "hill")
        spec = importlib.util.spec_from_file_location("ev_%s" % hilldir.name, td / "hill" / "eval.py")
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as ex:
            return {"hill": hilldir.name, "error": "eval.py import failed: %s" % ex}
        out = {"hill": hilldir.name, "hill_slug": str(hilldir.relative_to(ROOT)),
               "recovered": rec, "unrecovered": failed, "modes": {}}
        for label, final in (("validation", False), ("final", True)):
            try:
                r = mod.eval(sol, final=final)
                out["modes"][label] = {"passed": r.get("passed"),
                                       "metrics": {m["name"]: m["value"] for m in r.get("metrics", [])},
                                       "details": r.get("details", {})}
            except Exception as ex:
                out["modes"][label] = {"passed": None, "error": "%s: %s" % (type(ex).__name__, ex)}
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hill", default=None, help="only hills whose path contains this")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rows, ok = [], True
    for listdir in sorted(p for p in ROOT.glob("[0-9][0-9]-*") if p.is_dir()):
        for hilldir in sorted(p for p in listdir.iterdir() if p.is_dir()):
            if args.hill and args.hill not in str(hilldir):
                continue
            res = run_hill(hilldir, args.quiet)
            if res is None:
                continue
            rows.append(res)
    if not rows:
        print("no solved hills found (nothing with a non-empty solution/ directory)")
        return 0
    for r in rows:
        print("=" * 72)
        print("HILL:", r.get("hill_slug", r["hill"]))
        if "error" in r:
            print("  ERROR:", r["error"]); ok = False; continue
        for k, v in r["recovered"].items():
            print("  recovered %s -> %s" % (k, v))
        for k in r["unrecovered"]:
            print("  NOT recovered: %s (real held-out data; fixture must be supplied)" % k)
        for label, m in r["modes"].items():
            passed = m.get("passed")
            print("  [%s] passed=%s %s" % (label, passed, m.get("metrics") or m.get("error", "")))
            if m.get("details"):
                print("        details: %s" % m["details"])
            if passed is not True:
                ok = False
    print("=" * 72)
    print("VERDICT:", "all checked solutions passed" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
