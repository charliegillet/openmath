import FormalConjecturesUtil
import FormalConjectures.ErdosProblems.«28»

/-!
# Erdős Problem 40

*Reference:* [erdosproblems.com/40](https://www.erdosproblems.com/40)
-/

open AdditiveCombinatorics Filter Real Set
open scoped Pointwise

namespace Erdos40

/--
The predicate for a function $g\colon\mathbb{N} → \mathbb{R})$ that
$$\lvert A\cap \{1,\ldots,N\}\rvert \gg \frac{N^{1/2}}{g(N)}$$
implies $\limsup 1_A\ast 1_A(n)=\infty$.
-/
def Erdos40For (g : ℕ → ℝ) : Prop :=
  ∀ A : Set ℕ,
    (fun N : ℕ ↦ √N / g N) =O[atTop] (fun N ↦ ((A ∩ .Icc 1 N).ncard : ℝ)) →
    limsup (fun N ↦ (sumRep A N : ℕ∞)) atTop = ⊤

/--
Given a set of functions $\mathbb{N} → \mathbb{R})$, we assert that for all $g$ in that set,
if $g(N) → \infty$ then
$$\lvert A\cap \{1,\ldots,N\}\rvert \gg \frac{N^{1/2}}{g(N)}$$
implies $\limsup 1_A\ast 1_A(n)=\infty$.
-/
def Erdos40ForSet (G : Set (ℕ → ℝ)) : Prop := ∀ g ∈ G, Tendsto g atTop atTop → Erdos40For g

/--
For what functions $g(N) → \infty$ is it true that
$$\lvert A\cap \{1,\ldots,N\}\rvert \gg \frac{N^{1/2}}{g(N)}$$
implies $\limsup 1_A\ast 1_A(n)=\infty$?
-/
theorem hill : Erdos40ForSet answer(sorry) :=
