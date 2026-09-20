import FormalConjecturesUtil

/-!
# Erdős Problem 31

*References:*
- [erdosproblems.com/31](https://www.erdosproblems.com/31)
- [Er56] Erdős, P., *Problems and results in additive number theory*. Colloque sur la Théorie des
  Nombres, Bruxelles, 1955 (1956), 127-137.
- [Er59] Erdős, P., *Über einige Probleme der additiven Zahlentheorie*. Sammelband zu Ehren des 250.
  Geburtstages Leonhard Eulers (1959), 116-119.
- [Er65b] Erdős, Paul, *Some recent advances and current problems in number theory*. Lectures on
  Modern Mathematics, Vol. III (1965), 196-244.
- [Er73] Erdős, P., *Problems and results on combinatorial number theory*. A survey of combinatorial
  theory (Proc. Internat. Sympos., Colorado State Univ., Fort Collins, Colo., 1971) (1973), 117-138.
- [Lo54] Lorentz, G. G., *On a problem of additive number theory*. Proc. Amer. Math. Soc.
  (1954), 838-841.
-/

namespace Erdos31

open Filter
open scoped Pointwise

/--
Given any infinite set $A\subset \mathbb{N}$ there is a set $B$ of density $0$ such that $A+B$ contains all except finitely many integers.

Conjectured by Erdős and Straus. Proved by Lorentz [Lo54].
-/
theorem hill : ∀ A : Set ℕ, A.Infinite →
    ∃ B : Set ℕ, B.HasDensity 0 ∧ ∀ᶠ n in atTop, n ∈ A + B :=
