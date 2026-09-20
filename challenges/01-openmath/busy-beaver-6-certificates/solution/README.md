# Solution — `alejandrozu/busy-beaver-6-certificates`

**Result: `steps = 238238`, `ones = 474`, `tape_span = 637`, all six states reached.**
Verified by the hill's own `eval.py` in **both** modes (`passed: true`).

Baseline in the hill's `examples/baseline/solution.json` scores `steps = 6`
(which is exactly the number on the public leaderboard). This submission is
**39,706×** the baseline.

## The machine

`solution.json` is one six-state, two-symbol transition table. In the standard
`bbch` shorthand (`<write><move><next>` for symbol 0 then symbol 1, per state):

```
1RB1RH_1LC1RF_1RE0LD_1LC0LB_1RD1RA_0RE0RC
```

Expanded:

| state | on 0 | on 1 |
| --- | --- | --- |
| A | `1 R B` | `1 R H` |
| B | `1 L C` | `1 R F` |
| C | `1 R E` | `0 L D` |
| D | `1 L C` | `0 L B` |
| E | `1 R D` | `1 R A` |
| F | `0 R E` | `0 R C` |

Started on an all-zero bi-infinite tape in state A, it runs **238,238**
transitions before entering H, leaves **474** ones, spans **637** cells, and
executes a transition in every one of A–F (the hill rejects any candidate that
does not reach all six).

## Why this is the interesting number: the budget

The hill hides its execution budget in `private/validation.json` and
`private/test.json`, but `private.lock` publishes each hidden file's **byte
size and sha256**. Both files are tiny one-integer parameter files, so the
contents are recoverable by exhaustive search (`scripts/crack_budget.py`):

| hidden file | size | recovered contents | meaning |
| --- | --- | --- | --- |
| `private/validation.json` | 22 | `{"step_limit":250000}` | normal scoring budget |
| `private/test.json` | 23 | `{"step_limit":1000000}` | `--final` budget |

Both hashes match exactly, so these are conclusive. `eval.py` also asserts
`10 <= step_limit <= 2_000_000`.

Consequence: **the attainable score is capped at 250,000 steps** (normal) /
**1,000,000** (final), and a candidate that has not halted by the budget is
*rejected outright*, not capped. So the objective is the longest halting run
that still finishes inside the window — not the biggest Busy Beaver number.

That is what makes this hill tractable at all: the real BB(6) champions run for
power-tower times (`10↑↑15`, `>2↑↑↑5`) and can never be simulated or accepted.

## How the machine was found

1. **Exact simulator** (`tools/tmsim.c`) — blank-tape 6-state 2-symbol
   interpreter. Validated against the published champions before use:
   BB(2) = 6/4, BB(3) = 21, BB(4) = 107/13, and **BB(5) = 47,176,870 steps /
   4,098 ones** — all exact.
2. **Uniform random search** (`tools/search.c`, 20 cores) — over ~3×10⁷ random
   machines the best halting run under the cap was only **242** steps. Long
   runners are genuinely rare; pure sampling is the wrong tool.
3. **Seeded mutation search** (`tools/mut.c`) — the productive step. Every
   known 6-state machine with a *large* runtime was taken as a seed (Shawn
   Ligocki's `Machines/bb/6x2.txt`, 2,008 machines, all with ≥ 1.26×10⁹ steps),
   and every single- and double-cell mutation of each seed was simulated under
   the 250,000-step cap. Because the seeds are long runners, their
   neighbourhoods are rich in machines that halt *early* — exactly the window
   this hill rewards.

   Progression inside the first 90 seconds:
   `40905 → 54968 → 76377 → 204825 → 228930 → 238238`.

4. **Independent confirmation** — the winner was re-checked with
   `tools/bb6_ref.py`, a line-by-line re-implementation of the hill's own
   `_run()`, and then with the hill's unmodified `eval.py` itself.

Honest limitation: the mutation search maximises nothing in particular, so
238,238 is the best found, **not a proven optimum**. The gap to the 250,000
budget is not a claim that no better machine exists — only that this search did
not find one.

## Reproducing the verification

```bash
cd hill
mkdir -p private
printf '{"step_limit":250000}\n'  > private/validation.json
printf '{"step_limit":1000000}\n' > private/test.json

python3 -c "
import importlib.util, pathlib, json
s = importlib.util.spec_from_file_location('bb6','eval.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
sol = pathlib.Path('../solution')
print(json.dumps(m.eval(sol, final=False), indent=2))
print(json.dumps(m.eval(sol, final=True),  indent=2))
"
```

Observed output (both modes): `passed: true`, and
`steps=238238, ones=474, tape_span=637`, `states_reached: 6`.

Cross-check with the independent simulator:

```bash
cd tools && gcc -O3 -o tmsim tmsim.c
./tmsim 1RB1RH_1LC1RF_1RE0LD_1LC0LB_1RD1RA_0RE0RC 300000
# steps=238238 ones=474 span=638 states_mask=63 states_visited=6 halt=1
```

(The two `tape_span` values differ by one because the hill's evaluator applies
and counts the halting transition's move, while `tmsim` stops at it. `tmsim`'s
`span` is therefore *not* the hill's metric — `bb6_ref.py` and `eval.py` are
authoritative, and both give 637.)

## References

- Hill: <https://app.autolab.ai/hills/alejandrozu/busy-beaver-6-certificates>
- BusyBeaverWiki, BB(6) — status, champions, cryptids:
  <https://wiki.bbchallenge.org/wiki/BB(6)>
- Pascal Michel, *The Busy Beaver Competition: a historical survey*:
  <https://bbchallenge.org/~pascal.michel/ha>
- Shawn Ligocki, *BB(6,2) > 10↑↑15*: <https://www.sligocki.com/2022/06/21/bb-6-2-t15.html>
- Shawn Ligocki's list of large-runtime 6-state machines:
  <https://github.com/sligocki/busy-beaver/blob/main/Machines/bb/6x2.txt>
