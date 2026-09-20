import FormalConjecturesUtil

/-!
# Conjectures in Complexity Theory

This file contains formal statements of some of the main open conjectures
in complexity theory, including

- the P vs NP problem
- the NP vs coNP problem

*References:*
- [Wikipedia](https://en.wikipedia.org/wiki/P_versus_NP_problem)
- [The Clay Institute](https://www.claymath.org/millennium/p-vs-np/)
-/

namespace ComplexityTheory

/--
**P ≠ NP**:

The conjecture that the complexity classes P and NP are not equal.
-/
theorem hill : P ≠ NP :=
