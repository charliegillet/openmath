# AutoLab challenge archive

Every hill from four AutoLab lists, each in its own folder with the hill's **own unmodified source** (`hill/`), a plain-language README (what it is, what to prove, how to run), and — where we have one — a **verified solution** (`solution/`).

**45 hills across 4 lists.**

## Lists

- **[OpenMath — Six Hills + The Week 100](01-openmath/README.md)** — [`alejandrozu/openmath`](https://app.autolab.ai/lists/alejandrozu/openmath) — 6 hills, 1 with a solution here
- **[Erdős Problems](02-erdos-problems/README.md)** — [`ottogin/erdos-problems`](https://app.autolab.ai/lists/ottogin/erdos-problems) — 30 hills, 0 with a solution here
- **[Hello hills v2](03-hello-hills-v2/README.md)** — [`seanaklein19/hello-hills-v2`](https://app.autolab.ai/lists/seanaklein19/hello-hills-v2) — 5 hills, 0 with a solution here
- **[Millennium Prize Problems](04-millennium-prize-problems/README.md)** — [`ottogin/millennium-prize-problems`](https://app.autolab.ai/lists/ottogin/millennium-prize-problems) — 4 hills, 0 with a solution here

## Layout

```
<list>/
  README.md                 list index
  <hill-name>/
    README.md               what it is, scoring, what to prove, how to run
    hill/                   the hill's own unmodified files (README.md, eval.py, hill.yaml, locks)
    solution/               our verified submission + notes   (only where solved)
scripts/
  fetch_all.py              re-fetch everything from the AutoLab API
  crack_budget.py           recover small hidden budget files (sha256 brute force)
```

## Pulling the data yourself

The hill sources are public and are fetched through the AutoLab REST API. The API key is read **only** from the `AUTOLAB_API_KEY` environment variable — it is never stored in this repo and is not present in any file here.

```bash
export AUTOLAB_API_KEY=...        # your key, kept in your shell only
python3 scripts/fetch_all.py
```

Useful read-only endpoints:

- `GET /api/v1/lists/<owner>/<name>` — a list and its hills
- `GET /api/v1/hills/<owner>/<name>` — one hill's metadata
- `GET /api/v1/hills/<owner>/<name>/files` — the hill's file tree
- `GET /api/v1/hills/<owner>/<name>/files?path=<p>` — one file's contents

All calls need `Authorization: Bearer $AUTOLAB_API_KEY`.

## Honesty note

Solutions here state exactly what was verified and against which evaluator, including the runs that failed. A submission that does not beat a published bound says so.
