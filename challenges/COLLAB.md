# Working this archive in parallel

Two or more workers (human + coding agent) work the same 45 hills at the same time.
These rules exist so nobody overwrites anybody, and so a claim is a promise rather
than a vibe.

## 1. One worker per hill

A hill is worked by exactly one worker at a time. If a hill has no claim file, it is
free. If it has one, leave it alone unless the claim says `status: stalled` or
`status: abandoned` — then you may take it over, editing the existing claim file
rather than creating a second one.

## 2. Claim before you work

Create `claims/<owner>-<hill-slug>.md` from `claims/TEMPLATE.md`, commit it, push it,
**then** start. One file per claimed hill, one worker per file — this shape means two
workers adding different claims never touch the same line, so there are no
merge conflicts on the coordination data itself.

The claim file is small and is updated in place as you go:

| field | meaning |
| --- | --- |
| `worker` | who is on it (your GitHub handle) |
| `started` | ISO date you claimed it |
| `status` | `in-progress` / `done` / `stalled` / `abandoned` |
| `approach` | one or two lines: what you are actually trying |
| `result` | the verified metric values, verbatim, once you have them |

Update `status` and `result` in the same commit that lands your solution.

## 3. Touch only your own folders

- Write **only** into `<list>/<hill>/solution/` for the hill you claimed.
- **Never** edit anything under `<list>/<hill>/hill/`. Those are the hill author's
  files, fetched byte-for-byte from AutoLab. If a hill's source needs re-fetching,
  run `scripts/fetch_all.py` on a clean tree and check the diff is empty.
- Shared files (`README.md` at any level, `scripts/`, `HANDOFF.md`, `COLLAB.md`) are
  edited sparingly. Prefer adding a new file over rewriting a shared one.
- Do not reformat or reflow other people's files. Keep diffs about your hill.

## 4. Never commit a secret

The AutoLab key lives in `$AUTOLAB_API_KEY` or in `~/.config/autolab/env` (mode 600),
never in the tree. `.gitignore` blocks `env/`, `*.env`, `secrets*`. Before every push:

```bash
grep -rIn --exclude-dir=.git 'qlb_' . && echo 'STOP: key found in tree'
```

If a key ever lands in a commit, treat it as burned: rotate it and say so plainly.

## 5. Branches and pushes

- Branch per hill: `hill/<hill-slug>`. Do not push straight to `main` while others
  are working, except for claim files, which are safe to push directly.
- Keep commits small and frequent — an agent that pushes once at the end is
  indistinguishable from one that has hung.
- Commit messages state the **verified metric values**, not "update files".
- Rebase on `main` before pushing. Never force-push a branch you do not own.

## 6. Report shape

Lead with what was verified and by which command. Then the metric numbers
verbatim from the evaluator. Then what failed, what you skipped, and why. Then
anything still open. "Verified 238238 steps via the hill's eval.py; deeper
hill-climb found nothing better; not a proven optimum" beats a narrative.

## 7. Accuracy rules

- Exact arithmetic (`fractions.Fraction`) wherever the hill's evaluator uses it.
- Verify against the hill's **own** `eval.py`; a reimplementation is a debugging aid,
  never the authority.
- Distinguish *best found* from *proven optimal*. Never imply the first is the second.
- If you did not beat a published bound, say so in the README and the commit message.
- Cite published results you rely on with URLs.
