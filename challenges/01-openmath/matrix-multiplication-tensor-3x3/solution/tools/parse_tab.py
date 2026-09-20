"""Parse an HKS .tab scheme (algebra.uni-linz.ac.at) into u,v,w and measure it."""
import itertools, json, sys
from fractions import Fraction as F

def parse_tab(path):
    rows=[]
    for line in open(path):
        line=line.strip()
        if not line or set(line) <= set("-+"): continue
        parts=[p.split() for p in line.split("|")]
        if len(parts)!=3: continue
        rows.append([[F(x) for x in p] for p in parts])
    assert len(rows)%3==0, len(rows)
    terms=[]
    for i in range(0,len(rows),3):
        blk=rows[i:i+3]
        terms.append([[blk[r][s] for r in range(3)] for s in range(3)])  # 3 matrices, each list of 3 rows
    return terms

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

def orient(terms):
    """Return (support, U,V,W) for a Brent-valid orientation, or None."""
    raw = sum(1 for t in terms for M in t for r in M for x in r if x!=0)
    for perm in itertools.permutations(range(3)):
        for fu,fv,fw in itertools.product((flat_rm,flat_cm),repeat=3):
            U=[fu(t[perm[0]]) for t in terms]
            V=[fv(t[perm[1]]) for t in terms]
            W=[fw(t[perm[2]]) for t in terms]
            if brent_ok(U,V,W):
                return raw, sup(U,V,W), U,V,W
    return raw, None, None, None, None

if __name__=="__main__":
    terms=parse_tab(sys.argv[1])
    r=orient(terms)
    print("terms:",len(terms),"raw nonzeros:",r[0],"valid-orientation support:",r[1])
    if len(sys.argv)>2 and r[1] is not None:
        enc=lambda x:int(x) if x.denominator==1 else [x.numerator,x.denominator]
        json.dump({"u":[[enc(x) for x in row] for row in r[2]],
                   "v":[[enc(x) for x in row] for row in r[3]],
                   "w":[[enc(x) for x in row] for row in r[4]]},open(sys.argv[2],"w"))
        print("wrote",sys.argv[2])
