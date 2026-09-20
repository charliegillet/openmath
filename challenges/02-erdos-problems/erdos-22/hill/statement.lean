import FormalConjecturesUtil

/-!
# Erdős Problem 22

The central problem of Ramsey–Turán theory: writing $\mathrm{rt}(n; k, \ell)$ for the maximum
number of edges of a $K_k$-free graph on $n$ vertices whose largest independent set has size
less than $\ell$, is it true that for every $\epsilon > 0$ and all sufficiently large $n$
$$\mathrm{rt}(n; 4, \epsilon n) \geq n^2/8?$$

Conjectured by Bollobás and Erdős [BoEr76], who constructed such a graph with
$(1/8 + o(1))n^2$ edges. Together with the matching upper bound
$\mathrm{rt}(n; 4, \epsilon n) \leq (1/8 + o(1))n^2$ of Szemerédi [Sz72], this determines the
Ramsey–Turán density of $K_4$ to be $1/8$. The conjecture as stated was proved by Fox, Loh,
and Zhao [FLZ15].

*References:*
* [erdosproblems.com/22](https://www.erdosproblems.com/22)
* [BoEr76] Bollobás, B. and Erdős, P., *On a Ramsey-Turán type problem*. J. Combin. Theory
  Ser. B 21 (1976), 166--168.
* [Sz72] Szemerédi, E., *On graphs containing no complete subgraph with 4 vertices*
  (Hungarian). Mat. Lapok 23 (1972), 113--116.
* [FLZ15] Fox, J., Loh, P.-S., and Zhao, Y., *The critical window for the classical
  Ramsey-Turán problem*. Combinatorica 35 (2015), 435--476.
-/

open Filter SimpleGraph

namespace Erdos22

open scoped Classical in
/--
Let $\epsilon > 0$ and let $n$ be sufficiently large depending on $\epsilon$. Is there a graph
on $n$ vertices with at least $n^2/8$ many edges which contains no $K_4$, such that the largest
independent set has size at most $\epsilon n$?

This is true, as proved by Fox, Loh, and Zhao [FLZ15].
-/
theorem hill : answer(True) ↔
    ∀ ε : ℝ, 0 < ε → ∀ᶠ (n : ℕ) in atTop,
      ∃ G : SimpleGraph (Fin n), G.CliqueFree 4 ∧
        (G.indepNum : ℝ) ≤ ε * n ∧ (n : ℝ) ^ 2 / 8 ≤ G.edgeFinset.card :=
