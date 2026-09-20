import FormalConjecturesUtil

/-!
# Erdős Problem 16

*References:*
- [erdosproblems.com/16](https://www.erdosproblems.com/16)
- [Ch23] Chen, Yong-Gao, A conjecture of Erdős on $p+2^k$. arXiv:2312.04120 (2023).
- [Er50] Erdős, P., On integers of the form $2^k+p$ and some related problems. Summa Brasil. Math.
  (1950), 113-123.
- [Ro34] Romanoff, N. P., Über einige Sätze der additiven Zahlentheorie. Math. Ann. (1934), 668-678.
-/

open Nat Filter Set
open scoped Topology

namespace Erdos16

/--
The set of odd integers not of the form $2^k+p$.
-/
def Erdos16Set : Set ℕ :=
  { n | Odd n ∧ ¬ ∃ k p : ℕ, p.Prime ∧ n = 2 ^ k + p }

/--
A set of natural numbers has density 0.
-/
def density_zero (S : Set ℕ) : Prop :=
  open scoped Classical in
  Tendsto (fun x : ℕ ↦ (count (· ∈ S) x : ℝ) / (x : ℝ)) atTop (𝓝 0)

/--
Is the set of odd integers not of the form $2^k+p$ the union of an infinite arithmetic progression
and a set of density $0$?

Erdős called this conjecture "rather silly".

Chen [Ch23] has proved the answer is no.

This was formalized in Lean by Chin using Aristotle.
-/
theorem hill :
    answer(False) ↔
      ∃ A B : Set ℕ, Erdos16Set = A ∪ B ∧
        (∃ a d : ℕ, d > 0 ∧ A = { x | ∃ m : ℕ, x = a + m * d }) ∧
        density_zero B :=
