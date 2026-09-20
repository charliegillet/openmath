prelude

/-!
# Mathematics from the smallest Lean foundation

This module deliberately imports nothing—not even Lean's standard prelude.
It uses only Lean's trusted kernel mechanisms for defining inductive types,
recursive functions, and checking proof terms.
-/

universe u

/- Our own equality relation. We do not use Lean's built-in `Eq` below. -/
inductive Same {α : Sort u} (a : α) : α → Prop where
  | refl : Same a a

/- Our own Peano natural numbers. We do not use Lean's built-in `Nat`. -/
inductive Peano where
  | zero : Peano
  | next : Peano → Peano

/- Our primitive addition operation and its two defining Peano axioms. -/
axiom plus : Peano → Peano → Peano

axiom plus_zero (a : Peano) : Same (plus a Peano.zero) a

axiom plus_next (a b : Peano) :
  Same (plus a (Peano.next b)) (Peano.next (plus a b))

def one : Peano := Peano.next Peano.zero

def two : Peano := Peano.next one

#check Same.refl
#check Same.rec

/-
The next two results are derived only from our equality eliminator. They form
the tiny amount of proof infrastructure needed to chain the arithmetic axioms.
-/
theorem same_trans {α : Sort u} {a b c : α}
    (ab : Same a b) (bc : Same b c) : Same a c :=
  Same.rec ab bc

theorem next_respects_same {a b : Peano}
    (ab : Same a b) : Same (Peano.next a) (Peano.next b) :=
  Same.rec Same.refl ab

/- The actual derivation: unfold `one`, apply successor addition, then zero addition. -/
theorem one_plus_one_is_two : Same (plus one one) two :=
  same_trans
    (plus_next one Peano.zero)
    (next_respects_same (plus_zero one))

#check one_plus_one_is_two
#print axioms one_plus_one_is_two
