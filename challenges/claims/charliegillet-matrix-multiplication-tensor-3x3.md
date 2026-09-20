# Claim: 01-openmath/matrix-multiplication-tensor-3x3

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: hill/matrix-multiplication-tensor-3x3

## Approach

Reproduce a published rank-23 exact decomposition of the 3x3 matrix-multiplication
tensor over Q and minimise the secondary metric `support` (nonzero coefficients in
u, v, w). Measured three published schemes on this metric and submitted the
sparsest: Laderman 1976 via Sedoglavic's database, specialised at lambda=1.
A flip-graph search annealed on `support` found no improvement on it.

## Result

rank = 23, support = 153, passed = true.

```
command: cd 01-openmath/matrix-multiplication-tensor-3x3/solution/tools && python3 verify_local.py
output:  [validation] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 153}], "passed": true}
         [final] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 153}], "passed": true}
```

Note: `scripts/verify_all.py --hill matrix-multiplication-tensor-3x3` reports
passed=False for this hill. That is the harness being unable to synthesise the
held-out replay fixture, not a failing submission; both outputs are pasted
verbatim in solution/README.md.

## Limitations

- rank 23 is BEST KNOWN, not proven optimal (open gap 19-23; Blaser lower bound 19).
- support 153 is BEST FOUND, not proven minimal. No lower bound claimed.
- reference_beaten = 0. No published bound was beaten; the scheme is Laderman's,
  reproduced. My own flip-graph and symmetry-orbit searches found nothing better.
- Not verified against the real held-out fixture (unavailable). The replay stage is
  implied by the 729 Brent identities, which are checked from public data.
- The Heule-Kauers-Seidl dataset of 17,000+ rank-23 schemes could not be retrieved
  (expired TLS cert on the Linz host, no Wayback snapshot). Mining it for the
  minimum-support member is the obvious next step and was NOT done.
