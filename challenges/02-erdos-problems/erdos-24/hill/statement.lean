import FormalConjecturesUtil

/-!
# Erdős Problem 24

*References:*
- [erdosproblems.com/24](https://www.erdosproblems.com/24)
- [Er90] Erdős, Paul, *Some of my favourite unsolved problems*. A tribute to Paul Erdős (1990),
  467-478.
- [Er97b] Erdős, Paul, *Some old and new problems in various branches of combinatorics*. Discrete
  Math. (1997), 227-231.
- [Er92b] Erdős, Paul, *Some of my favourite problems in various branches of combinatorics*.
  Matematiche (Catania) (1992), 231-240.
- [Er97f] Erdős, Paul, *Some unsolved problems*. Combinatorics, geometry and probability
  (Cambridge, 1993) (1997), 1-10.
- [Gr12] Grzesik, Andrzej, *On the maximum number of five-cycles in a triangle-free graph*.
  J. Combin. Theory Ser. B (2012), 1061-1066.
- [HHKNR13] Hatami, Hamed and Hladký, Jan and Kráľ, Daniel and Norine, Serguei and Razborov,
  Alexander, *On the number of pentagons in triangle-free graphs*. J. Combin. Theory Ser. A
  (2013), 722-732.
-/

open SimpleGraph

namespace Erdos24

/--
Does every triangle-free graph on $5n$ vertices contain at most $n^5$ copies of $C_5$?

Győri proved this with $1.03n^5$, which has been improved by Füredi. The answer is yes, as proved
independently by Grzesik [Gr12] and Hatami, Hladky, Král, Norine, and Razborov [HHKNR13].
-/
theorem hill : answer(True) ↔
    ∀ (n : ℕ) (G : SimpleGraph (Fin (5 * n))), G.CliqueFree 3 →
      G.copyCount (cycleGraph 5) ≤ n ^ 5 :=
