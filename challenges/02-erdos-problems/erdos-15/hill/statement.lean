import FormalConjecturesUtil

/-!
# Erdős Problem 15: Convergence of Series with Primes

*Reference:* [erdosproblems.com/15](https://www.erdosproblems.com/15)
-/

namespace Erdos15

open Filter Topology

/--
Is it true that $\sum_{n=1}^\infty(-1)^n\frac{n}{p_n}$ converges,
where $p_n$ is the sequence of primes?

Note: In the problem statement, $p_n$ is the $n$-th prime, indexed such that $p_1=2, p_2=3, \ldots$.
We 0-index here to reflect how Nat.nth works.
-/
theorem hill : answer(sorry) ↔
    Summable (fun k : ℕ => (-1 : ℚ) ^ (k + 1) * (k + 1) / (k.nth Nat.Prime)) :=
