"""Support minimisation over rank-23 decompositions, flip graph with
PROPORTIONAL factor matching.

A rank-one term u (x) v (x) w is unchanged by (u,v,w) -> (au, bv, w/(ab)), so two
terms may be flipped whenever one factor is merely PROPORTIONAL, not equal.  We
rescale first (exactly, over Q), then apply the Kauers-Moosbauer flip.  Support
is scale-invariant, so the rescaling never distorts the objective.
"""
import json, random, sys
from collections import defaultdict
from fractions import Fraction as F

R = 23
def nnzv(t): return sum(1 for x in t if x)
def sup(U,V,W): return sum(nnzv(t) for t in U)+sum(nnzv(t) for t in V)+sum(nnzv(t) for t in W)

def direction(vec):
    """Scale-normalised direction: first nonzero entry becomes 1."""
    for x in vec:
        if x:
            return tuple(y/x for y in vec)
    return tuple(vec)

def scale_of(vec):
    for x in vec:
        if x: return x
    return F(1)

def load(p):
    d=json.load(open(p))
    conv=lambda M:[tuple(F(x) for x in r) for r in M]
    return conv(d["u"]),conv(d["v"]),conv(d["w"])

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

CAP=F(10**5)
def ok(v): return all(abs(x)<=CAP for x in v)

def run(U,V,W,seed,iters,T0=2.2,T1=0.05):
    rng=random.Random(seed)
    U,V,W=list(U),list(V),list(W)
    cur=sup(U,V,W); best=cur; bestS=(list(U),list(V),list(W))
    for it in range(iters):
        T=T0*(T1/T0)**(it/iters)
        which=rng.randrange(3)
        X = U if which==0 else (V if which==1 else W)
        g=defaultdict(list)
        for t in range(R): g[direction(X[t])].append(t)
        cand=[grp for grp in g.values() if len(grp)>1]
        if not cand: continue
        grp=rng.choice(cand)
        i,j=rng.sample(grp,2)
        # rescale term j so X[j] == X[i] exactly, pushing the scalar elsewhere
        lam = scale_of(X[i])/scale_of(X[j])
        Uj,Vj,Wj=U[j],V[j],W[j]
        if which==0:   Uj=tuple(x*lam for x in Uj); Wj=tuple(x/lam for x in Wj)
        elif which==1: Vj=tuple(x*lam for x in Vj); Wj=tuple(x/lam for x in Wj)
        else:          Wj=tuple(x*lam for x in Wj); Vj=tuple(x/lam for x in Vj)
        if which==0:
            a=tuple(x+y for x,y in zip(V[i],Vj)); b=tuple(x-y for x,y in zip(Wj,W[i]))
            if not(ok(a) and ok(b)): continue
            d=nnzv(a)-nnzv(V[i])+nnzv(b)-nnzv(Wj)+ (nnzv(Uj)-nnzv(U[j])) + (nnzv(Wj)-nnzv(W[j]))*0
            newV_i,newW_j,newU_j,newV_j=a,b,Uj,Vj
        elif which==1:
            a=tuple(x+y for x,y in zip(U[i],Uj)); b=tuple(x-y for x,y in zip(Wj,W[i]))
            if not(ok(a) and ok(b)): continue
            d=nnzv(a)-nnzv(U[i])+nnzv(b)-nnzv(Wj)
            newU_i=a
        else:
            a=tuple(x+y for x,y in zip(U[i],Uj)); b=tuple(x-y for x,y in zip(Vj,V[i]))
            if not(ok(a) and ok(b)): continue
            d=nnzv(a)-nnzv(U[i])+nnzv(b)-nnzv(Vj)
            newU_i=a
        # apply, then recompute support exactly (cheap at this size)
        oU,oV,oW=list(U),list(V),list(W)
        if which==0:
            U[j],V[j],W[j]=Uj,Vj,Wj; V[i]=a; W[j]=b
        elif which==1:
            U[j],V[j],W[j]=Uj,Vj,Wj; U[i]=a; W[j]=b
        else:
            U[j],V[j],W[j]=Uj,Vj,Wj; U[i]=a; V[j]=b
        new=sup(U,V,W); d=new-cur
        if d<=0 or rng.random()<pow(2.718281828,-d/T):
            cur=new
            if cur<best:
                best=cur; bestS=(list(U),list(V),list(W))
        else:
            U,V,W=oU,oV,oW
    return best,bestS

def dump(S,path):
    def enc(x): return int(x) if x.denominator==1 else [x.numerator,x.denominator]
    json.dump({"u":[[enc(x) for x in r] for r in S[0]],
               "v":[[enc(x) for x in r] for r in S[1]],
               "w":[[enc(x) for x in r] for r in S[2]]},open(path,"w"))

if __name__=="__main__":
    src,out,iters,seeds=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
    U,V,W=load(src); print("start",sup(U,V,W),flush=True)
    gb,gS=10**9,None
    for s in range(seeds):
        b,S=run(U,V,W,s,iters)
        if b<gb:
            gb,gS=b,S
            assert brent_ok(*gS),"BRENT FAILED"
            dump(gS,out); print("seed",s,"best",gb,flush=True)
    print("best:",gb,flush=True)
