# Why a template certifies a bound for arbitrarily large graphs

Fix symmetric A in {0,1}^{m by m}, positive integer weights w_i and Q=sum(w_i). For each t>=1 construct G_t with block i of size t*w_i. Every pair of distinct vertices in blocks i,j has color A_ij, including the case i=j. Hence G_t is a simple two-colored complete graph with t*Q vertices, regardless of the template's diagonal.

Sample four vertices of G_t independently and uniformly, allowing repetitions. Their block labels are independent with distribution Pr(i)=w_i/Q. Assign repeated-vertex pairs the template diagonal color as an auxiliary convention. The probability that all six colors agree is exactly the rational P in README.md; all ordered template tuples are included.

Condition on the four sampled vertices being distinct. The conditional probability of a monochromatic four-set is exactly M4(G_t)/binom(t*Q,4), because each four-set has 4! orderings. The probability of any vertex collision is at most 6/(t*Q), by the union bound on the six pairs. If p denotes the unconditional probability and q the conditional probability given no collision, writing p=(1-epsilon)*q+epsilon*r gives |p-q|<=epsilon. Therefore

    |M4(G_t)/binom(t*Q,4) - P| <= 6/(t*Q)

whenever t*Q>=4. It follows that the density converges to P as t tends to infinity.

For completeness, the minimum density a_n over n-vertex graphs is nondecreasing for n>=4: the average density of an n-vertex induced subgraph of any (n+1)-vertex graph equals that graph's density, so some induced n-vertex subgraph has density at most that average. Also 0<=a_n<=1, so its limit c4 exists. Since a_(tQ)<=M4(G_t)/binom(t*Q,4), taking limits along this subsequence proves c4<=P.

Thus verifying a finite certificate with P<B* proves a constructive upper bound on an infinite extremal problem. It is not evidence for a universal lower bound or for the exact value of c4.

## Counting implementation

The evaluator groups ordered block tuples by index multiplicities. For a fixed color, the five types 4, 3+1, 2+2, 2+1+1, 1+1+1+1 have factors 1,4,6,12,24. A repeated index is permitted only when its diagonal has that color. Off-diagonal indices must form a clique of that color. Vertex-weight products give the number of block assignments. The sum is an integer and its denominator is Q^4.

Tests compare the optimized bit-set implementation with a separately written literal four-index sum on small weighted templates. They also check color complement, relabeling, common scaling, splitting a block into twins, and explicit finite blow-ups. The supplied published 768-block construction is an independent nontrivial exact regression case.

## Scope of verification

This document is an ordinary mathematical proof. It is not a proof-assistant artifact. The evaluator's exact integer calculation, the correctness of its implementation, and the lifting argument constitute the stated computational proof protocol. Competition organizers must approve that trust boundary or require a formalized checker/lifting lemma under their pinned proof system. No model-generated assertion, self-reported objective, README claim, or arbitrary submitted proof text is accepted as a proof by eval.py.
