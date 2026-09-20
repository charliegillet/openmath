"""Rebuild solution.json from the published source.

Source: A. Sedoglavic, "Fast Matrix Multiplication Algorithms Database",
https://fmm.univ-lille.fr/3x3x3.html -> 3x3x3_tensor.mpl.bz2, which catalogues
the rank-23 decomposition of J. D. Laderman, "A noncommutative algorithm for
multiplying 3x3 matrices using 23 multiplications", Bull. AMS 82 (1976) 126-128,
https://doi.org/10.1090/S0002-9904-1976-13988-2

Sedoglavic stores it as a one-parameter family in l; every entry is one of
0, +-1, +-l, +-1/l, so the NONZERO PATTERN -- and therefore `support` -- is the
same for every l != 0.  We specialise at l = 1 to get integer coefficients.

The hill indexes A and B row-major but C as 3*column+row.  Rather than assume an
orientation, we try all slot permutations and both flattenings and keep the ones
that satisfy all 729 Brent identities.

Reproduce:
    curl -O https://fmm.univ-lille.fr/3x3x3_tensor.mpl.bz2
    bunzip2 3x3x3_tensor.mpl.bz2
    python3 build_solution.py            # writes solution.json
"""
import re, json, itertools
from fractions import Fraction as F

txt = open("3x3x3_tensor.mpl").read()
body = txt[txt.index("TriadSet("):]
mats = re.findall(r'Matrix\(3,\s*3,\s*\[\[(.*?)\]\]\)', body)
def cell(s):
    s = s.strip()
    s = s.replace("1/l", "1").replace("-l", "-1").replace("l", "1")
    return F(s) if s else F(0)
parsed = []
for m in mats:
    rows = m.split("],[")
    M = [[cell(c) for c in r.split(",")] for r in rows]
    assert len(M) == 3 and all(len(r) == 3 for r in M), m
    parsed.append(M)
triads = [parsed[i:i+3] for i in range(0, len(parsed), 3)]
print("triads parsed:", len(triads))

def flat_rm(M): return [M[r][c] for r in range(3) for c in range(3)]
def flat_cm(M): return [M[r][c] for c in range(3) for r in range(3)]

def target(a,b,c):
    row,inner=divmod(a,3); bi,col=divmod(b,3)
    return int(inner==bi and c==3*col+row)
TG=[[[target(a,b,c) for c in range(9)] for b in range(9)] for a in range(9)]
def brent_ok(U,V,W):
    for a in range(9):
        for b in range(9):
            t=TG[a][b]
            for c in range(9):
                if sum(U[k][a]*V[k][b]*W[k][c] for k in range(len(U)))!=t[c]: return False
    return True
def sup(U,V,W): return sum(1 for M in (U,V,W) for r in M for x in r if x!=0)

# try every assignment of the three slots and row/col flattening
best=None
for perm in itertools.permutations(range(3)):
    for fu,fv,fw in itertools.product((flat_rm,flat_cm),repeat=3):
        U=[fu(t[perm[0]]) for t in triads]
        V=[fv(t[perm[1]]) for t in triads]
        W=[fw(t[perm[2]]) for t in triads]
        if brent_ok(U,V,W):
            s=sup(U,V,W)
            print("VALID: perm",perm,"flat",fu.__name__,fv.__name__,fw.__name__,"support",s)
            if best is None or s<best[0]: best=(s,U,V,W)
if best:
    enc=lambda x:int(x) if x.denominator==1 else [x.numerator,x.denominator]
    json.dump({"u":[[enc(x) for x in r] for r in best[1]],
               "v":[[enc(x) for x in r] for r in best[2]],
               "w":[[enc(x) for x in r] for r in best[3]]},open("solution.json","w"))
    print("best support:",best[0])
else:
    print("no valid orientation found")
