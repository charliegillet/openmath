import FormalConjecturesUtil

/-!
# Riemann Hypothesis and its generalizations

The Riemann Hypothesis asserts that all non-trivial zeros of the Riemann zeta function
$\zeta(s)$ have real part $\frac{1}{2}$. The trivial zeros are the negative even integers
$-2, -4, -6, \ldots$. The hypothesis is one of the seven Millennium Prize Problems
posed by the Clay Mathematics Institute.

The Generalized Riemann Hypothesis extends this to Dirichlet $L$-functions of primitive
Dirichlet characters.

Note: the **Extended Riemann Hypothesis** (ERH) for Dedekind zeta functions is intentionally
**not** stated here. Mathlib's `NumberField.dedekindZeta` is the naive Dirichlet series
(`LSeries`), not a meromorphic continuation; outside the region of absolute convergence
`tsum` returns junk `0`, producing spurious zeros that make the naive foramlisation of the
conjecture provably false. The ERH should be added once Mathlib provides a meromorphic
continuation of the Dedekind zeta function.

*References:*
- [The Clay Institute](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf)
- [Wikipedia: Riemann hypothesis](https://en.wikipedia.org/wiki/Riemann_hypothesis)
- [Wikipedia: Generalized Riemann hypothesis](https://en.wikipedia.org/wiki/Generalized_Riemann_hypothesis)
- [Wikipedia: Dedekind zeta function](https://en.wikipedia.org/wiki/Dedekind_zeta_function)
- J. Neukirch, *Algebraic Number Theory*, Springer (Grundlehren 322), 1999, Chapter VII, §5.
- D. A. Marcus, *Number Fields*, Springer (GTM 81), 1977, Chapter VII.
-/

namespace RiemannHypothesis

/-- The **Riemann Hypothesis**: all non-trivial zeros of the Riemann zeta function have real
part $\frac{1}{2}$. That is, if $\zeta(s) = 0$, $s \neq 1$, and $s$ is not a trivial zero
$-2(n+1)$ for some $n \in \mathbb{N}$, then $\operatorname{Re}(s) = \frac{1}{2}$.

This is the official Millennium Prize Problem as posed by the
[Clay Mathematics Institute](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf).

This uses the `RiemannHypothesis` type from Mathlib, which is defined as
`∀ (s : ℂ), riemannZeta s = 0 → (¬∃ n : ℕ, s = -2 * (n + 1)) → s ≠ 1 → s.re = 1 / 2`. -/
theorem hill : RiemannHypothesis :=
