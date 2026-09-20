import FormalConjecturesUtil

/-!
# Erdős Problem 6

*References:*
- [erdosproblems.com/6](https://www.erdosproblems.com/6)
- [BFT15] Banks, William D. and Freiberg, Tristan and Turnage-Butterbaugh, Caroline L., Consecutive primes in tuples. Acta Arith. (2015), 261-266.
- [Ma15] Maynard, James, Small gaps between primes. Ann. of Math. (2) (2015), 383-413.
-/

namespace Erdos6

/--
There are infinitely many $n$ such that $d_n < d_{n+1} < d_{n+2}$, where $d$
denotes the prime gap function.
-/
theorem hill :
    {n | primeGap n < primeGap (n + 1) ∧ primeGap (n + 1) < primeGap (n + 2)}.Infinite :=
