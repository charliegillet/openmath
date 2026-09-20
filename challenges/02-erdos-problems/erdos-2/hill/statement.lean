import FormalConjecturesUtil

/-!
# Erdős Problem 2

*Reference:* [erdosproblems.com/2](https://www.erdosproblems.com/2)

Erdős asked whether the smallest modulus in a distinct covering system can be arbitrarily large.
Hough proved that the answer is no, and Balister, Bollobás, Morris, Sahasrabudhe, and Tiba later
gave a simpler proof with an improved explicit upper bound.
-/

namespace Erdos2

/--
Can the smallest modulus of a covering system be arbitrarily large?

This problem has a negative answer: there is a universal bound on the least modulus of any
distinct covering system.
-/
theorem hill :
    answer(False) ↔
      ∀ B : ℕ, ∃ c : StrictCoveringSystem ℤ, ∀ i, ∃ m : ℕ,
        c.moduli i = Ideal.span {(m : ℤ)} ∧ B < m :=
