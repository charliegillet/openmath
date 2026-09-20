# matrix-multiplication-tensor-3x3 — rank 23, support 153

An exact rank-23 decomposition of the 3×3 matrix-multiplication tensor over ℚ,
with 153 nonzero coefficients across `u`, `v`, `w`. All coefficients are integers
in {−1, 0, +1}.

**Result: `rank = 23`, `support = 153`, `passed: true`.**

This is a **reproduction of a published construction**, not a new one, and 23 is
the **best known** rank, *not* a proven optimum. See *Limitations* below.

## Result

```
rank    = 23      (metric direction: min)
support = 153     (metric direction: min)
passed  = true    (729/729 Brent identities, exact arithmetic over Q)
```

## How it was found

The scheme is J. D. Laderman's 1976 rank-23 algorithm, taken from Sedoglavic's
database, which stores it as a one-parameter family in λ. Every entry of that
family is one of `0, ±1, ±λ, ±1/λ`, so the nonzero *pattern* — and therefore
`support` — is identical for every λ ≠ 0. Specialising at λ = 1 gives integer
coefficients in {−1, 0, 1}.

The hill indexes `A` and `B` row-major but indexes `C` as `3*column + row`.
Rather than guess the orientation, `tools/build_solution.py` tries all six slot
permutations and both flattenings and keeps those satisfying all 729 Brent
identities; six orientations are valid (the matrix-multiplication tensor is
invariant under cyclic permutation of its three slots together with transposition),
all at support 153.

### Alternatives measured, and rejected

Both were verified `passed: true` by the hill's own `eval.py`, and both are worse
on the secondary metric, so neither is submitted:

| scheme | source | support |
| --- | --- | --- |
| **Laderman 1976 (λ=1) — submitted** | Sedoglavic database | **153** |
| flip-graph scheme `gg-333-rank23` | `khoruzhii/flip-cpd` dataset | 155 |
| 56-addition ternary scheme | arXiv:2604.27645 | 175 |

The recent literature on rank-23 3×3 schemes minimises **additions after
common-subexpression elimination**, which is a different objective from this
hill's `support`. A scheme with fewer additions is not automatically sparser:
the 56-addition scheme of arXiv:2604.27645 has support 175, well above Laderman's
153. So the published addition records (56, 52) do **not** bound this metric, and
no published figure for minimum `support` was located.

### Search that did not improve on 153

`tools/search_support.py` implements a flip-graph local search (Kauers–Moosbauer
transitions) annealed directly on `support`, with factors matched up to
*proportionality* over ℚ — each rank-one term is only defined up to scalars, so
proportional matching is exact and admits strictly more moves than exact matching.
A sandwich-symmetry orbit search over `u → P u Q⁻¹`, `v → Q v R⁻¹`, `w → R w P⁻¹`
for small unimodular `P, Q, R` was also run.

**Neither found anything below 153.** Reported honestly: this search produced no
improvement, and the submitted scheme is entirely the published one. The flip
graph around these schemes turns out to be move-poor — the submitted scheme has
only three proportional factor pairs, so the walk has ~6 available moves and
explores a small neighbourhood.

## Reproducing the verification

`hill/private/{validation,test}.json` are real held-out replay fixtures. Unlike
the busy-beaver hill, `private.lock` here locks genuine data, not a tiny
parameter file, so `scripts/crack_budget.py` cannot recover it. A fixture
matching the schema in `eval.py` is synthesised instead.

**This does not weaken the check.** `eval.py` verifies all 729 Brent identities
*first*, from public data alone. Passing them is equivalent to the scheme
computing `A·B` correctly for **every** input, so the private replay stage is
mathematically implied by the Brent stage and cannot fail once it passes,
whatever the hidden matrices contain. The fixture only supplies well-formed input
so that stage can run.

```bash
cd 01-openmath/matrix-multiplication-tensor-3x3/solution/tools
python3 verify_local.py
```

Verbatim output:

```
[validation] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 153}], "passed": true}
[final] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 153}], "passed": true}
```

### The archive-wide verifier reports FAILED for this hill

Run as the archive instructs:

```bash
python3 scripts/verify_all.py --hill matrix-multiplication-tensor-3x3
```

Verbatim output:

```
========================================================================
HILL: 01-openmath/matrix-multiplication-tensor-3x3
  NOT recovered: private/test.json (real held-out data; fixture must be supplied)
  NOT recovered: private/validation.json (real held-out data; fixture must be supplied)
  [validation] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpo99j15hi/hill/private/validation.json'"}
  [final] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpo99j15hi/hill/private/test.json'"}
========================================================================
VERDICT: SOME CHECKS FAILED
```

This `passed=False` is **not** a failure of the submission. `verify_all.py` only
reconstructs hidden files that are tiny parameter files; it cannot synthesise a
replay fixture, so `eval.py` aborts on the missing file before scoring anything.
The `passed: true` above comes from the same `eval.py`, with the fixture supplied.
Both outputs are reported so the discrepancy is not mistaken for a passing run.

## Limitations — what this does NOT prove

- **Rank 23 is best known, not proven optimal.** Whether 3×3 matrix multiplication
  is possible with 22 multiplications is open. The best published lower bound on
  the rank of the 3×3 tensor is 19 (Bläser), so the gap 19–23 is genuinely open.
  Nothing here narrows it.
- **Support 153 is best found, not proven minimal.** No lower bound on `support`
  is established or claimed. A sparser rank-23 scheme may well exist.
- **`reference_beaten = 0`.** No published bound was beaten. The submitted scheme
  is Laderman's, reproduced; my own search found nothing better than the published
  construction. The comparison against 155 and 175 is a comparison against two
  other *published* schemes on this hill's metric, not an improvement on any
  published record.
- **Not verified against the real held-out fixture**, which is unavailable. The
  argument that the replay is implied by the Brent identities is a mathematical
  one, given above; it was not executed against the hill author's actual data.
- The Heule–Kauers–Seidl dataset of 17,000+ inequivalent rank-23 schemes could
  not be retrieved (the Linz host serves an expired/self-signed certificate and
  has no Wayback snapshot; TLS verification was not disabled). Mining it for the
  minimum-support member is the obvious next step and was **not** done.

## Sources

- J. D. Laderman, *A noncommutative algorithm for multiplying 3×3 matrices using
  23 multiplications*, Bull. Amer. Math. Soc. 82 (1976) 126–128.
  https://doi.org/10.1090/S0002-9904-1976-13988-2
- A. Sedoglavic, *Fast Matrix Multiplication Algorithms Database*.
  https://fmm.univ-lille.fr/3x3x3.html
- M. J. H. Heule, M. Kauers, M. Seidl, *New ways to multiply 3×3-matrices*,
  J. Symbolic Computation. https://arxiv.org/abs/1905.10192
- M. Kauers, J. Moosbauer, *Flip graphs for matrix multiplication*.
  https://arxiv.org/abs/2212.01175
- *An Exact 56-Addition, Rank-23 Scheme for General 3×3 Matrix Multiplication*.
  https://arxiv.org/abs/2604.27645
- flip-graph scheme dataset: https://github.com/khoruzhii/flip-cpd

## Files

- `solution.json` — the submission: `u`, `v`, `w`, each 23×9, integer coefficients.
- `tools/build_solution.py` — rebuilds `solution.json` from the published source.
- `tools/verify_local.py` — runs the hill's own `eval.py` with a synthesised fixture.
- `tools/search_support.py` — the flip-graph support search (found no improvement).
