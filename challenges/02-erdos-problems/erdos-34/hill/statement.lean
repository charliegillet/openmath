import FormalConjecturesUtil

/-!
# Erdős Problem 34

*References:*
- [erdosproblems.com/34](https://www.erdosproblems.com/34)
- [Er77c] Erdős, Paul, *Problems and results on combinatorial number theory. III*. Number theory day
  (Proc. Conf., Rockefeller Univ., New York, 1976) (1977), 43-72.
- [ErGr80] Erdős, P. and Graham, R., *Old and new problems and results in combinatorial number
  theory*. Monographies de L'Enseignement Mathematique (1980).
- [He86] Hegyvári, N., *On consecutive sums in sequences*. Acta Math. Hungar. (1986),
  193--200.
- [Ko15] Konieczny, J., *On consecutive sums in permutations*. arXiv:1504.07156 (2015).
-/

namespace Erdos34

open scoped BigOperators

/-- The set of consecutive sums of a permutation `p` of `{1,…,n}`, where position `k` holds the
value `p k + 1`: the sums `∑_{u ≤ k ≤ v} (p k + 1)`. -/
def consecutiveSums (n : ℕ) (p : Equiv.Perm (Fin n)) : Finset ℕ :=
  (Finset.univ.filter (fun x : Fin n × Fin n => x.1 ≤ x.2)).image
    (fun x => ∑ k ∈ Finset.Icc x.1 x.2, ((p k : ℕ) + 1))

/--
For any permutation $\pi\in S_n$ of $\{1,\ldots,n\}$ let $S(\pi)$ count the number of distinct consecutive sums, that is, sums of the shape $\sum_{u\leq i\leq v}\pi(i)$. Is it true that
$$
S(\pi) = o(n^2)
$$
for all $\pi\in S_n$?

Hegyvári [He86] gave a counterexample.
-/
theorem hill : answer(False) ↔
    ∀ c : ℝ, 0 < c → ∃ N : ℕ, ∀ n ≥ N, ∀ p : Equiv.Perm (Fin n),
      ((consecutiveSums n p).card : ℝ) < c * (n : ℝ) ^ 2 :=
