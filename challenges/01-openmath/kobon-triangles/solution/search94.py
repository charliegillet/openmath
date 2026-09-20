#!/usr/bin/env python3
"""Exact search for a 94-triangle 18-line arrangement.

Everything is exact: integer line triples and integer/Fraction arithmetic only.
Moves are "mutations": replace one line by a line that passes exactly through an
existing arrangement vertex (combinatorial wall), optionally shifted off the wall
by +-1 in the constant term -- this is exactly the set of combinatorial-type
changes reachable from the current arrangement.

Usage: python3 search94.py <seconds> [seed] [out.json]
"""
import json
import multiprocessing as mp
import random
import sys
import time
from fractions import Fraction
from itertools import combinations
from math import gcd, isqrt

sys.path.insert(0, "hill")
import eval as H  # noqa: E402

N = 18
BASE = [tuple(l) for l in json.load(open("solution/solution.json"))["lines"]]
CACHE = {}


def count(lines):
    return len(H.count_triangles(list(lines)))


def norm(values):
    return H._normalize(tuple(values))


def intersection(u, v):
    return H._intersection(u, v)


def vertices(lines):
    out = []
    for i, j in combinations(range(len(lines)), 2):
        p = intersection(lines[i], lines[j])
        if p is not None:
            out.append((p, i, j))
    return out


def dirs_from(lines, extra_random=0, rng=None):
    ds = set()
    for a, b, _ in lines:
        g = gcd(abs(a), abs(b)) or 1
        ds.add((a // g, b // g))
        ds.add((-a // g, -b // g))
    for a in range(-3, 4):
        for b in range(-3, 4):
            if a or b:
                g = gcd(abs(a), abs(b))
                ds.add((a // g, b // g))
    if extra_random and rng is not None:
        for _ in range(extra_random):
            a = rng.randint(-40, 40)
            b = rng.randint(-40, 40)
            if a or b:
                g = gcd(abs(a), abs(b))
                ds.add((a // g, b // g))
    return sorted(ds)


def line_through(a, b, p):
    """Integer triple for the line through rational point p with direction (a,b)."""
    X, Y, W = p
    t = a * X + b * Y
    vals = (a * W, b * W, -t)
    g = gcd(gcd(abs(vals[0]), abs(vals[1])), abs(vals[2]))
    if g:
        vals = tuple(v // g for v in vals)
    return norm(vals)


def dist_num(p, line):
    """|a x + b y + c| * W  (integer, proportional to distance)."""
    X, Y, W = p
    a, b, c = line
    return abs(a * X + b * Y + c * W)


def candidates(lines, rng, nearest=24, nfar=3, offsets=(0, 1, -1), k=1):
    """Yield (index, new_line) moves."""
    verts = vertices(lines)
    dset = dirs_from(lines, extra_random=6, rng=rng)
    for i in range(N):
        dv = []
        for p, j, kk in verts:
            if i == j or i == kk:
                continue
            dv.append((dist_num(p, lines[i]), p))
        if not dv:
            continue
        dv.sort(key=lambda t: t[0])
        chosen = [p for _, p in dv[:nearest]]
        if dv and nfar:
            chosen += [p for _, p in rng.sample(dv, min(nfar, len(dv)))]
        for p in chosen:
            for (a, b) in dset:
                base = line_through(a, b, p)
                for off in offsets:
                    cand = (base[0], base[1], base[2] + off * k)
                    if cand[0] or cand[1]:
                        yield i, norm(cand)


def apply_move(lines, i, cand):
    if cand in lines:
        return None
    out = list(lines)
    out[i] = cand
    if len(set(out)) != N:
        return None
    return out


def eval_chunk(args):
    lines, moves = args
    best = (-1, None, None)
    for (i, cand) in moves:
        new = apply_move(lines, i, cand)
        if new is None:
            continue
        c = count(new)
        if c > best[0]:
            best = (c, i, tuple(new))
    return best


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    out_path = sys.argv[3] if len(sys.argv) > 3 else "solution/search94_best.json"
    rng = random.Random(seed)
    pool = mp.Pool(min(20, mp.cpu_count()))
    t0 = time.time()
    best_lines = BASE
    best = count(BASE)
    print(f"start count={best}", flush=True)
    rounds = 0
    while time.time() - t0 < budget:
        rounds += 1
        cur = best_lines
        if best > 93:
            break
        moves = list(candidates(cur, rng))
        rng.shuffle(moves)
        chunks = [moves[i::40] for i in range(40)]
        results = pool.map(eval_chunk, [(cur, ch) for ch in chunks])
        results.sort(key=lambda r: -r[0])
        top = results[0]
        print(f"round {rounds} t={time.time()-t0:.0f}s candidates={len(moves)} "
              f"best={top[0]} cur={best}", flush=True)
        if top[0] > best:
            best, best_lines = top[0], list(top[2])
            json.dump({"lines": [list(l) for l in best_lines]},
                      open(out_path, "w"))
            print(f"*** improved to {best} -> {out_path}", flush=True)
            if best >= 94:
                break
        # plateau walk: step to a 93-arrangement even when not improving
        if top[0] >= best and top[2] is not None and rng.random() < 0.7:
            best_lines = list(top[2])
            if top[0] > best:
                best = top[0]
        elif top[0] >= best - 1 and top[2] is not None and rng.random() < 0.25:
            best_lines = list(top[2])
        else:
            best_lines = cur
    pool.close()
    print("FINAL", best, "lines:", [list(l) for l in best_lines], flush=True)
    json.dump({"lines": [list(l) for l in best_lines], "triangles": best},
              open(out_path, "w"))
    return best


if __name__ == "__main__":
    main()
