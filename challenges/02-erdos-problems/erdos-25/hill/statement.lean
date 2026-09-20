import FormalConjecturesUtil

/-!
# Erdős Problem 25: Logarithmic density of size-dependent congruences

*Reference:* [erdosproblems.com/25](https://www.erdosproblems.com/25)
-/

open Filter Finset Real Nat Set
open scoped Topology

namespace Erdos25

/--
Let $n_1 < n_2 < \dots$ be an arbitrary sequence of integers, each with an associated residue class
$a_i \pmod{n_i}$. Let $A$ be the set of integers $n$ such that for every $i$ either $n < n_i$ or
$n \not\equiv a_i \pmod{n_i}$. Must the logarithmic density of $A$ exist?
-/
theorem hill : answer(sorry) ↔
    ∀ (seq_n : ℕ → ℕ) (seq_a : ℕ → ℤ), (∀ i, 0 < seq_n i) → StrictMono seq_n →
      ∃ d, Set.HasLogDensity
        { x : ℕ | ∀ i, (x : ℤ) < seq_n i ∨ ¬((x : ℤ) ≡ seq_a i [ZMOD seq_n i]) } d :=
