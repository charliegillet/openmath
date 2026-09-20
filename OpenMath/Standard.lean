import Std

namespace OpenMath.Standard

/-!
# The same proof with Lean's standard library

Here `Nat`, numerals, `+`, and `=` come from Lean's normal environment.
Both sides compute to the same canonical natural number, so reflexivity closes
the goal.
-/

theorem one_plus_one_is_two : 1 + 1 = 2 := by
  rfl

#check one_plus_one_is_two
#print one_plus_one_is_two
#print axioms one_plus_one_is_two

end OpenMath.Standard
