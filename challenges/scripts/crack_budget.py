#!/usr/bin/env python3
"""Recover small hidden `private/*.json` files by brute-forcing their sha256.

A hill's `private.lock` publishes, for each hidden file, its byte size and
sha256. When that file is a tiny parameter file (a step budget, a limit, a
threshold and nothing else), the space of possible contents is small enough to
enumerate exhaustively and recover the exact secret offline.

Usage:
    python3 crack_budget.py <hill-dir> [--max 2000000]

Prints, for every locked entry, any candidate content whose size and sha256
match exactly. A match is cryptographically conclusive.
"""
import hashlib, itertools, json, pathlib, sys

# Candidate serialisations for a one-integer parameter file.
TEMPLATES = [
    '{{"step_limit": {n}}}\n', '{{"step_limit": {n}}}', '{{"step_limit":{n}}}\n', '{{"step_limit":{n}}}',
    '{{"limit": {n}}}\n', '{{"limit": {n}}}', '{{"budget": {n}}}\n', '{{"budget": {n}}}',
    '{{"max_steps": {n}}}\n', '{{"max_steps": {n}}}', '{{"timeout_s": {n}}}\n', '{{"seed": {n}}}\n',
    '{{"n": {n}}}\n', '{{"trials": {n}}}\n', '{{"samples": {n}}}\n',
]


def candidates(n):
    for t in TEMPLATES:
        yield t.format(n=n)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    hill = pathlib.Path(sys.argv[1])
    hi = 2_000_000
    if "--max" in sys.argv:
        hi = int(sys.argv[sys.argv.index("--max") + 1])
    lock = hill / "private.lock"
    if not lock.exists():
        sys.exit("no private.lock in %s" % hill)
    data = json.loads(lock.read_text())
    for entry in data.get("entries", []):
        want, size = entry["sha256"], entry.get("size")
        found = []
        for n in range(0, hi + 1):
            for s in candidates(n):
                if size is not None and len(s) != size:
                    continue
                if hashlib.sha256(s.encode()).hexdigest() == want:
                    found.append((n, repr(s)))
        print("%-28s size=%-6s -> %s" % (entry["path"], size, found or "no match in range"))


if __name__ == "__main__":
    main()
