import FormalConjecturesUtil

/-!
# Erdős Problem 26

*References:*
- [erdosproblems.com/26](https://www.erdosproblems.com/26)
- [Te19](https://arxiv.org/pdf/1908.00488) G. Tenenbaum,
  _Some of Erdős' unconventional problems in number theory, thirty-four years later_,
  arXiv:1908.00488 [math.NT] (2019)
-/

namespace Erdos26

/-- A sequence of naturals $(a_i)$ is _thick_ if their sum of reciprocals diverges:
$$
  \sum_i \frac{1}{a_i} = \infty
$$-/
def IsThick {ι : Type*} (A : ι → ℕ) : Prop := ¬Summable (fun i ↦ (1 : ℝ) / A i)

theorem hill {ι : Type*} [Finite ι] (A : ι → ℕ) : ¬IsThick A :=
