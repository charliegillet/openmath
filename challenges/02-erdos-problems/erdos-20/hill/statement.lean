import FormalConjecturesUtil

/-!
# Erdős Problem 20

*References:*
* [erdosproblems.com/20](https://www.erdosproblems.com/20)
* [Wikipedia](https://en.wikipedia.org/wiki/Sunflower_(mathematics))
* [ErRa60] Erdős, Paul and Rado, Richard. Intersection theorems for systems of sets.
  J. London Math. Soc. 35 (1960), 85--90.

-/
namespace Erdos20

/--
Let $f(n,k)$ be minimal such that every $F$ family of $n$-uniform sets with $|F| \ge f(n,k)$
contains a $k$-sunflower.
-/
noncomputable def f (n k : ℕ) : ℕ :=
  sInf {m | ∀ {α : Type}, ∀ (F : Set (Set α)),
    ((∀ f ∈ F, f.ncard = n) ∧ m ≤ F.ncard) → ∃ S ⊆ F, S.ncard = k ∧ IsSunflower S}

@[category test, AMS 5]
theorem f_0_1 : f 0 1 = 1 := by
  refine IsLeast.csInf_eq ⟨fun F hF ↦ ?_, fun n hn ↦ n.pos_of_ne_zero fun hn₀ ↦ ?_⟩
  · obtain ⟨A, hA⟩ := F.nonempty_of_ncard_ne_zero (by omega)
    exact ⟨{A}, by simpa using ⟨hA, isSunflower_singleton _⟩⟩
  · obtain ⟨S, hS⟩ := (hn (α := ℕ) {} (by simpa))
    simp_all [bot_unique hS.1]

/--
Is it true that $f(n,k) < c_k^n$ for some constant $c_k>0$ and for all $n > 0$?
-/
theorem hill : answer(sorry) ↔ ∃ (c : ℕ → ℕ), ∀ n k, n > 0 → f n k < (c k) ^ n :=
