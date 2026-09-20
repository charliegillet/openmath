import Std.Tactic

namespace OpenMath.Kobon

structure Line where
  a : Int
  b : Int
  c : Int
deriving Repr, DecidableEq, Inhabited

structure Point where
  x : Rat
  y : Rat
deriving Repr, DecidableEq

def intersection (first second : Line) : Option Point :=
  let w := first.a * second.b - first.b * second.a
  if w = 0 then
    none
  else
    some {
      x := (first.b * second.c - first.c * second.b : Int) / (w : Rat)
      y := (first.c * second.a - first.a * second.c : Int) / (w : Rat)
    }

def coordinate (line : Line) (point : Point) : Rat :=
  if line.b = 0 then point.y else point.x

def strictlyBetween (value left right : Rat) : Bool :=
  (left < value && value < right) || (right < value && value < left)

def sideIsEmpty (lines : Array Line) (side : Nat)
    (first second : Point) : Bool :=
  let line := lines[side]!
  let left := coordinate line first
  let right := coordinate line second
  (List.range lines.size).all fun other =>
    if other = side then
      true
    else
      match intersection line lines[other]! with
      | none => true
      | some point => !(strictlyBetween (coordinate line point) left right)

def isTriangularFace (lines : Array Line) (i j k : Nat) : Bool :=
  match intersection lines[i]! lines[j]!,
        intersection lines[i]! lines[k]!,
        intersection lines[j]! lines[k]! with
  | some ij, some ik, some jk =>
      ij != ik &&
      sideIsEmpty lines i ij ik &&
      sideIsEmpty lines j ij jk &&
      sideIsEmpty lines k ik jk
  | _, _, _ => false

def triangleIndices (lines : Array Line) : List (Nat × Nat × Nat) :=
  (List.range lines.size).flatMap fun i =>
    (List.range lines.size).flatMap fun j =>
      (List.range lines.size).filterMap fun k =>
        if i < j && j < k && isTriangularFace lines i j k then
          some (i, j, k)
        else
          none

def lines : Array Line := #[
  ⟨0, 1, -366⟩,
  ⟨0, 1, -431⟩,
  ⟨14, -99, 34099⟩,
  ⟨86, -135, 18268⟩,
  ⟨494, -625, 24279⟩,
  ⟨60, -41, -7469⟩,
  ⟨699, -382, -154073⟩,
  ⟨350, -191, -50935⟩,
  ⟨760, -251, -205751⟩,
  ⟨799, 31, -325992⟩,
  ⟨394, 59, -168297⟩,
  ⟨724, 341, -427427⟩,
  ⟨683, 411, -461387⟩,
  ⟨683, 412, -412078⟩,
  ⟨203, 173, -149460⟩,
  ⟨379, 704, -438209⟩,
  ⟨296, 741, -439693⟩,
  ⟨115, 791, -359574⟩
]

def triangleCount : Nat := (triangleIndices lines).length

#eval triangleCount

theorem line_count_is_18 : lines.size = 18 := by
  rfl

theorem triangle_count_is_93 : triangleCount = 93 := by
  native_decide

#print axioms triangle_count_is_93

end OpenMath.Kobon
