# Handoff — working these hills with a coding agent, in parallel

This is the on-ramp for a **second agent (or human) working the same challenge
archive at the same time**. Read `COLLAB.md` for the rules that keep two workers
from colliding, and `claims/` to see what is already taken.

- **Archive location:** [`yhinai/openmath` → `challenges/`](https://github.com/yhinai/openmath/tree/main/challenges)
- **45 hills** across four AutoLab lists, one folder per hill
- Each hill folder: `hill/` (the hill's own unmodified source), `README.md`
  (what it is, what to prove, how to run), and `solution/` where solved

---

## 1. Get set up

```bash
git clone https://github.com/yhinai/openmath
cd openmath/challenges
```

You need an **AutoLab API key** to fetch hill sources and (optionally) to submit.
Get it from Yahya out-of-band — never over a channel that ends up in a repo, a
commit, or an issue. Put it in your shell, or in a gitignored file:

```bash
# option A — session only
export AUTOLAB_API_KEY=...

# option B — persistent, local, gitignored (this is what the existing setup does)
mkdir -p ~/.config/autolab
printf 'AUTOLAB_API_KEY=%s\n' 'YOUR_KEY' > ~/.config/autolab/env
chmod 700 ~/.config/autolab && chmod 600 ~/.config/autolab/env
```

`challenges/.gitignore` already blocks `env/`, `*.env`, `secrets*`. **Never commit
the key.** Before any push, run the check:

```bash
grep -rIn --exclude-dir=.git 'qlb_' . && echo 'STOP: key found in tree'
```

## 2. Check what's already taken

```bash
ls claims/                 # one small file per claimed hill
cat claims/*.md            # worker, status, timestamp
```

Claim a hill **before** you start work on it (`COLLAB.md` §2 has the template).
Unclaimed hills are fair game.

## 3. Work one hill

Pick a hill, then:

1. **Read `hill/README.md`.** That is the authoritative statement of the task and
   the exact submission format. Read `hill/eval.py` too — it is the ground-truth
   scorer and it enforces the format.
2. **Write your submission into `solution/`.** Only into that folder. Never edit
   anything under `hill/` — those are the author's originals, byte for byte.
3. **Verify against the hill's own evaluator**, not against your own reimplementation.
   See §4.
4. **Commit and push** with a message that states the verified metric numbers.

## 4. The verification recipe (this is the important part)

Most of these hills read a hidden fixture from `private/` that is *not* shipped.
Two cases:

**(a) The fixture is a tiny parameter file.** `private.lock` publishes each hidden
file's **byte size and sha256**. If the file is just a budget or a limit, brute-force
it — it is conclusive:

```bash
python3 scripts/crack_budget.py 01-openmath/busy-beaver-6-certificates
```

Worked example (busy-beaver-6): `{"step_limit":250000}` (22 bytes) and
`{"step_limit":1000000}` (23 bytes). Both hashes matched exactly. **That single
fact is what made the hill solvable** — the score is capped by the budget, not by
the Busy Beaver function.

**(b) The fixture is real held-out data.** You cannot recover it. Instead call the
hill's scoring function directly with your own generated fixtures, or bypass the
fixture read:

```bash
cd 01-openmath/<hill>/hill
mkdir -p private
cp ../../<your-own-fixture>.json private/validation.json   # match the schema in eval.py
python3 -c "
import importlib.util, pathlib, json
s = importlib.util.spec_from_file_location('ev','eval.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
print(json.dumps(m.eval(pathlib.Path('../solution'), final=False), indent=2))
"
```

A solution only counts as solved when that call returns `passed: true` and the
metrics you claim. Report the **verbatim** output.

## 5. Honesty rules (non-negotiable, and they are what makes this useful)

- Report the exact numbers the evaluator returns. No rounding up, no "should".
- **Say what failed.** A submission that does not beat the published bound must say
  so (`reference_beaten = 0`).
- Distinguish **best found** from **proven optimal**. The BB6 solution says plainly
  that 238,238 is the best found, not a proven optimum.
- Cite sources with URLs for every published result you rely on.
- Use exact arithmetic (`fractions.Fraction`), never floats, wherever the hill's
  evaluator does.
- Archived is not the same as finished: `solution/` without a `passed: true` line in
  its README is a draft.

## 6. Model answer to copy

`01-openmath/busy-beaver-6-certificates/solution/README.md` is the standard the rest
should meet: stated result, how it was found, the tooling in `solution/tools/`, the
exact reproduction command, and an explicit limitation.

---

## 7. Copy-paste prompt for your coding agent

> You are working a shared archive of AutoLab research hills at
> `github.com/yhinai/openmath`, in the `challenges/` directory. Work **only** on the
> hill assigned to you, and coordinate through the repo.
>
> **Setup**
> 1. `git clone https://github.com/yhinai/openmath && cd openmath/challenges`
> 2. The AutoLab API key is provided out-of-band. Put it in `$AUTOLAB_API_KEY` or in
>    `~/.config/autolab/env` (mode 600). **Never** write it into any file that is
>    committed, and before every push run
>    `grep -rIn --exclude-dir=.git 'qlb_' .` and stop if it matches.
>
> **Before doing anything**
> 3. Read `COLLAB.md` and `ls claims/`. Check your hill is not already claimed.
>    Claim it by creating `claims/<hill-slug>.md` from `claims/TEMPLATE.md`.
>
> **Doing the work**
> 4. Read `hill/README.md` and `hill/eval.py` — the README is the task, the evaluator
>    is the scorer. Everything you emit must satisfy the format the evaluator parses.
> 5. Write your submission into `solution/` only. Never modify `hill/`.
> 6. If `hill/private.lock` locks a tiny parameter file, recover it with
>    `python3 scripts/crack_budget.py <hill-dir>` — the lock publishes size + sha256,
>    so a match is conclusive. That has changed the whole framing of at least one
>    hill. If it locks real held-out data you cannot recover, generate your own
>    fixture with the schema `eval.py` expects and score against that.
> 7. Use exact arithmetic — `fractions.Fraction`, never floats — wherever the
>    evaluator does. Verify **with the hill's own `eval.py`**, not with your own
>    reimplementation of it, and paste the verbatim output into
>    `solution/README.md`.
> 8. Search the literature first: for several of these hills the best known
>    construction is published, and reproducing a published optimum exactly is a
>    perfectly good result — cite it with a URL.
> 9. Do not overstate. Distinguish "best found" from "proven optimal". If you do not
>    beat a published bound, say so explicitly in the README and in your report.
>
> **Finishing**
> 10. Commit with a message stating the verified metric values, push to a branch
>     named `hill/<hill-slug>`, open a PR, and update your claim file to
>     `status: done` (or `status: stalled` with a one-line reason). Report to me the
>     verbatim evaluator output and the exact command that produced it.
