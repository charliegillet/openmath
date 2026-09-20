#!/usr/bin/env python3
"""Fetch every hill's public source (README, eval.py, hill.yaml, locks, examples)
from AutoLab into an organised local tree.

The API key is read ONLY from the AUTOLAB_API_KEY environment variable and is
never written to disk or into any generated file.
"""
import json, os, sys, time, urllib.request, urllib.parse, pathlib

KEY = os.environ.get("AUTOLAB_API_KEY")
BASE = "https://app.autolab.ai"
ROOT = pathlib.Path(__file__).resolve().parent.parent


def api(path, tries=4):
    for a in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
            with urllib.request.urlopen(r, timeout=60) as fh:
                return json.loads(fh.read().decode())
        except Exception as e:
            if a == tries - 1:
                raise
            time.sleep(1.5 * (a + 1))


def fetch_hill(slug, dest: pathlib.Path):
    dest.mkdir(parents=True, exist_ok=True)
    files = api("/api/v1/hills/%s/files" % slug)
    (dest / "_hill.json").write_text(json.dumps(files, indent=2))
    got = []
    for row in files.get("tree_rows", []):
        if row["kind"] != "file":
            continue
        p = row["path"]
        try:
            c = api("/api/v1/hills/%s/files?%s" % (slug, urllib.parse.urlencode({"path": p})))
        except Exception as e:
            got.append((p, "ERR " + str(e)))
            continue
        content = c.get("content")
        if not isinstance(content, str):
            got.append((p, "no-content"))
            continue
        out = dest / p
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        got.append((p, len(content)))
    return files, got


def main():
    if not KEY:
        sys.exit("AUTOLAB_API_KEY not set in environment")
    lists = json.loads((ROOT / "lists.json").read_text())
    for dirname, (listname, meta) in enumerate(lists.items(), start=1):
        folder = ROOT / ("%02d-%s" % (dirname, listname))
        for slug in meta["hills"]:
            dest = folder / slug.split("/")[-1]
            if (dest / "_hill.json").exists():
                print("skip (cached)", slug)
                continue
            try:
                files, got = fetch_hill(slug, dest)
                print("OK  %-58s %d files" % (slug, len(got)))
            except Exception as e:
                print("FAIL %-58s %s" % (slug, e))
            time.sleep(0.15)
    print("done")


if __name__ == "__main__":
    main()
