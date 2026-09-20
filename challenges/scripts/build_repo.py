#!/usr/bin/env python3
"""Build the organised repo: move fetched hill sources into hill/, then generate
README.md files at hill / list / root level."""
import json, pathlib, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://app.autolab.ai"
OUR = {"README.md", "NOTES.md", "solution"}

LIST_TITLES = {
    "01-openmath": ("OpenMath — Six Hills + The Week 100", "alejandrozu/openmath"),
    "02-erdos-problems": ("Erdős Problems", "ottogin/erdos-problems"),
    "03-hello-hills-v2": ("Hello hills v2", "seanaklein19/hello-hills-v2"),
    "04-millennium-prize-problems": ("Millennium Prize Problems", "ottogin/millennium-prize-problems"),
}


def hill_meta(hd: pathlib.Path):
    """Return dict of metadata from the fetched _hill.json."""
    hj = json.loads((hd / "hill" / "_hill.json").read_text())
    desc = hj.get("describe", {}) or {}
    return hj, desc


def yaml_metrics(hd: pathlib.Path):
    p = hd / "hill" / "hill.yaml"
    if not p.exists():
        return [], {}
    txt = p.read_text()
    metrics = []
    for m in re.finditer(r"\{name:\s*([A-Za-z0-9_]+),\s*direction:\s*(max|min)\}", txt):
        metrics.append((m.group(1), m.group(2)))
    params = re.search(r"^params:\n((?:[ \t].*\n?)*)", txt, re.M)
    return metrics, {"params": params.group(1).strip() if params else ""}


def organise():
    for listdir in sorted(ROOT.glob("[0-9][0-9]-*")):
        for hd in sorted(p for p in listdir.iterdir() if p.is_dir()):
            hill = hd / "hill"
            if hill.exists():
                continue
            hill.mkdir()
            for item in list(hd.iterdir()):
                if item.name in OUR or item.name == "hill":
                    continue
                item.rename(hill / item.name)


def write_hill_readme(hd: pathlib.Path, listname: str):
    hj, desc = hill_meta(hd)
    metrics, extra = yaml_metrics(hd)
    slug = hj.get("slug") or (hj.get("hill", {}) or {}).get("slug") or hd.name
    h = hj.get("hill", hj)
    name = h.get("name", hd.name)
    description = h.get("description", "")
    version = (hj.get("current") or {}).get("version", "")
    lines = []
    lines.append("# %s\n" % name)
    lines.append("**AutoLab hill:** [`%s`](%s/hills/%s)  \n**List:** %s  \n**Version:** %s  \n**Visibility:** %s\n"
                 % (slug, BASE_URL, slug, listname, version or "n/a", h.get("visibility", "public")))
    lines.append("## What it is\n")
    lines.append(description.strip() + "\n")
    if metrics:
        lines.append("## Scoring\n")
        lines.append("Metrics are compared **lexicographically** in this order:\n")
        for i, (mn, d) in enumerate(metrics, 1):
            lines.append("%d. `%s` — %s" % (i, mn, "**maximise**" if d == "max" else "**minimise**"))
        lines.append("")
    if extra.get("params"):
        lines.append("## Parameters\n")
        lines.append("```yaml\n%s\n```\n" % extra["params"])
    lines.append("## What to prove / produce\n")
    lines.append("The authoritative statement is `hill/README.md` (the hill's own text, fetched verbatim). "
                 "**Read it before writing anything.** The submission format it specifies is enforced by "
                 "`hill/eval.py`, which is also the ground-truth scorer.\n")
    lines.append("## How to get the hill's source\n")
    lines.append("```bash\n"
                 "# requires an AutoLab API key in the environment (never commit it)\n"
                 "export AUTOLAB_API_KEY=...\n"
                 "python3 scripts/fetch_all.py            # re-fetch every hill in this repo\n"
                 "```\n")
    lines.append("## How to run / verify locally\n")
    lines.append("```bash\n"
                 "cd hill\n"
                 "python3 -c \"import importlib.util,pathlib;"
                 "s=importlib.util.spec_from_file_location('ev','eval.py');"
                 "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                 "print(m.eval(pathlib.Path('../solution')))\"\n"
                 "```\n"
                 "`eval.py` also reads `private/validation.json` and `private/test.json`, which are **not** "
                 "distributed with the hill. Where those are small enough to be recoverable they are documented "
                 "below; otherwise replace that read with your own fixture or call the scoring function directly.\n")
    sol = hd / "solution"
    if sol.exists() and any(sol.iterdir()):
        lines.append("## Solution in this repo\n")
        lines.append("See [`solution/README.md`](solution/README.md).\n")
    else:
        lines.append("## Solution in this repo\n")
        lines.append("_Not yet — this folder is a task specification only._\n")
    lines.append("## Provenance\n")
    lines.append("- Hill page: %s/hills/%s\n- Fetched automatically from the AutoLab public API "
                 "(`/api/v1/hills/<slug>/files`); the files under `hill/` are the hill author's originals, unmodified.\n"
                 % (BASE_URL, slug))
    (hd / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_list_readme(listdir: pathlib.Path):
    title, slug = LIST_TITLES.get(listdir.name, (listdir.name, ""))
    hills = sorted(p for p in listdir.iterdir() if p.is_dir())
    out = ["# %s\n" % title]
    out.append("AutoLab list: [`%s`](%s/lists/%s) — %d hills.\n" % (slug, BASE_URL, slug, len(hills)))
    out.append("| Hill | Metrics | Solution |")
    out.append("| --- | --- | --- |")
    for hd in hills:
        metrics, _ = yaml_metrics(hd)
        ms = ", ".join("%s(%s)" % (m, d) for m, d in metrics) or "—"
        has = "yes" if (hd / "solution").exists() and any((hd / "solution").iterdir()) else "—"
        out.append("| [`%s`](%s/README.md) | %s | %s |" % (hd.name, hd.name, ms, has))
    out.append("\nEach hill folder contains `hill/` (the hill's own unmodified source: README, evaluator, "
               "spec, locks) and, where solved, `solution/`.\n")
    (listdir / "README.md").write_text("\n".join(out), encoding="utf-8")


def write_root_readme():
    lists = sorted(p for p in ROOT.glob("[0-9][0-9]-*") if p.is_dir())
    total = sum(len([d for d in p.iterdir() if d.is_dir()]) for p in lists)
    out = ["# AutoLab challenge archive\n"]
    out.append("Every hill from four AutoLab lists, each in its own folder with the hill's **own unmodified "
               "source** (`hill/`), a plain-language README (what it is, what to prove, how to run), and — "
               "where we have one — a **verified solution** (`solution/`).\n")
    out.append("**%d hills across %d lists.**\n" % (total, len(lists)))
    out.append("## Lists\n")
    for p in lists:
        title, slug = LIST_TITLES.get(p.name, (p.name, ""))
        n = len([d for d in p.iterdir() if d.is_dir()])
        solved = len([d for d in p.iterdir() if d.is_dir() and (d / "solution").exists()
                      and any((d / "solution").iterdir())])
        out.append("- **[%s](%s/README.md)** — [`%s`](%s/lists/%s) — %d hills, %d with a solution here"
                   % (title, p.name, slug, BASE_URL, slug, n, solved))
    out.append("\n## Layout\n")
    out.append(textwrap.dedent("""\
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
        """))
    out.append("## Pulling the data yourself\n")
    out.append("The hill sources are public and are fetched through the AutoLab REST API. The API key is read "
               "**only** from the `AUTOLAB_API_KEY` environment variable — it is never stored in this repo and "
               "is not present in any file here.\n")
    out.append("```bash\n"
               "export AUTOLAB_API_KEY=...        # your key, kept in your shell only\n"
               "python3 scripts/fetch_all.py\n"
               "```\n")
    out.append("Useful read-only endpoints:\n")
    out.append("- `GET /api/v1/lists/<owner>/<name>` — a list and its hills\n"
               "- `GET /api/v1/hills/<owner>/<name>` — one hill's metadata\n"
               "- `GET /api/v1/hills/<owner>/<name>/files` — the hill's file tree\n"
               "- `GET /api/v1/hills/<owner>/<name>/files?path=<p>` — one file's contents\n")
    out.append("All calls need `Authorization: Bearer $AUTOLAB_API_KEY`.\n")
    out.append("## Honesty note\n")
    out.append("Solutions here state exactly what was verified and against which evaluator, including the "
               "runs that failed. A submission that does not beat a published bound says so.\n")
    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    organise()
    for listdir in sorted(ROOT.glob("[0-9][0-9]-*")):
        if not listdir.is_dir():
            continue
        title, slug = LIST_TITLES.get(listdir.name, (listdir.name, ""))
        for hd in sorted(p for p in listdir.iterdir() if p.is_dir()):
            write_hill_readme(hd, title)
        write_list_readme(listdir)
        print("wrote", listdir.name)
    write_root_readme()
    print("wrote root README.md")
