import FormalConjecturesUtil

/-!
# Erdős Problem 4

*Reference:* [erdosproblems.com/4](https://www.erdosproblems.com/4)
-/

open Real

namespace Erdos4

def Erdos4For (C : ℝ) : Prop :=
  {n : ℕ | (n + 1).nth Nat.Prime - n.nth Nat.Prime >
    C * log (log n) * log (log (log (log n))) / (log (log (log n))) ^ 2 * log n}.Infinite

/--
Is it true that, for any $C > 0$, there infinitely many $n$ such that:
$$
  p_{n + 1} - p_n > C \frac{\log\log n\log\log\log\log n}{(\log\log\log n) ^ 2}\log n
$$
-/
theorem hill : answer(True) ↔ (∀ C > 0, Erdos4For C) :=
