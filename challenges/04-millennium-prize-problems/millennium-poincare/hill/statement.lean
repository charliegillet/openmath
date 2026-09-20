import FormalConjecturesUtil

/-! # The Poincaré Conjecture

References:
- [Miln2022](https://www.claymath.org/wp-content/uploads/2022/06/poincare.pdf)
- [Wang2017](https://annals.math.princeton.edu/2017/186-2/p03).
- [mo296171](https://mathoverflow.net/questions/296171/unique-smooth-structure-on-3-manifolds)
- [mathlib4](https://github.com/leanprover-community/mathlib4)

The formalisations in this file are based on the ones written by Junyan Xu in Mathlib4.
-/

namespace PoincareConjecture

open scoped Manifold ContDiff EuclideanGeometry ContinuousMap

local macro:max "𝕊" noWs n:superscript(term) : term =>
  `(Metric.sphere (0 : EuclideanSpace ℝ (Fin ($(⟨n.raw[0]⟩) + 1))) 1)

/-- The predicate that the generalized Poincaré conjecture holds in dimension $n$, i.e. that
any $n$-dimensional manifold that is homotopy equivalent to the sphere is in fact homeomorphic
to the sphere. -/
def ConjectureFor (n : ℕ) : Prop :=
  ∀ (M : Type) [TopologicalSpace M] [T2Space M] [ChartedSpace (ℝ^n) M], M ≃ₕ 𝕊ⁿ → Nonempty (M ≃ₜ 𝕊ⁿ)

/--
The Millennium Problem, solved by Grigori Perelman in 2003: the Poincaré Conjecture holds.
-/
@[category research solved, AMS 54 57]
theorem poincare_conjecture : ConjectureFor 3 := by
  sorry

/--
The Generalized Poincaré Conjecture holds for surfaces.
-/
@[category textbook, AMS 54 57]
theorem poincare_conjecture.variants.dimension_two : ConjectureFor 2 := by
  sorry

/--
The Generalized Poincaré Conjecture holds for dimensions at least 5.
-/
@[category textbook, AMS 54 57]
theorem poincare_conjecture.variants.dimension_ge_five (n : ℕ) (hn : 5 ≤ n) : ConjectureFor n := by
  sorry

/--
The Generalized Poincaré Conjecture holds in dimension 4.
-/
@[category textbook, AMS 54 57]
theorem poincare_conjecture.variants.dimension_four : ConjectureFor 4 := by
  sorry

/-- The predicate that the smooth Poincaré conjecture holds in dimension $n$. -/
def SmoothConjectureFor (n : ℕ) : Prop :=
  ∀ (M : Type) [TopologicalSpace M] [ChartedSpace (ℝ^n) M] [IsManifold (𝓡 n) ∞ M],
    M ≃ₕ 𝕊ⁿ → Nonempty (M ≃ₘ⟮𝓡 n, 𝓡 n⟯ 𝕊ⁿ)

/-- A reformulation of the Millennium Problem in terms of smooth 3-folds. -/
@[category textbook, AMS 54 57]
theorem poincare_conjecture.variants.smooth_for_three : SmoothConjectureFor 3 := by
  sorry

/-- The smooth formulation of the Millennium Problem implies the general case. This follows from
the fact that every topological 3-fold admits a smooth structure [mo296171]. -/
@[category textbook, AMS 54 57]
theorem poincare_conjecture.variants.smooth_implication (H : SmoothConjectureFor 3) :
    ConjectureFor 3 := by
  sorry

/-- The values at which the smooth version of the conjecture is known to hold. -/
def SmoothTrueValues : Set ℕ := {1, 2, 3, 5, 6, 12, 56, 61}

/-- The smooth version of the Poincaré conjecture is known to hold in dimensions
$1, 2, 3, 5, 6, 12, 56, 61$. See [Wang2017]. -/
@[category research solved, AMS 54 57]
theorem poincare_conjecture.variants.smooth_known_cases (n : ℕ) (hn : n ∈ SmoothTrueValues) :
    SmoothConjectureFor n := by
  sorry

/-- The four dimensional case of the smooth version of the conjecture is still open.
See [Wang2017]. -/
theorem hill : SmoothConjectureFor 4 :=
