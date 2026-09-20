# kernel-opt

**AutoLab hill:** [`ottogin/kernel-opt`](https://app.autolab.ai/hills/ottogin/kernel-opt)  
**List:** Hello hills v2  
**Version:** 0.1.0  
**Visibility:** public

## What it is

Make single-threaded matrix multiplication faster in C while keeping its answers correct. This hill measures CPU throughput in GFLOP/s; higher is better.

## Scoring

Metrics are compared **lexicographically** in this order:

1. `gflops` — **maximise**

## Parameters

```yaml
n: {type: int, default: 512, min: 128, max: 2048}
  tolerance: {type: float, default: 2.0e-3, min: 0.0, max: 0.1}
```

## What to prove / produce

The authoritative statement is `hill/README.md` (the hill's own text, fetched verbatim). **Read it before writing anything.** The submission format it specifies is enforced by `hill/eval.py`, which is also the ground-truth scorer.

## How to get the hill's source

```bash
# requires an AutoLab API key in the environment (never commit it)
export AUTOLAB_API_KEY=...
python3 scripts/fetch_all.py            # re-fetch every hill in this repo
```

## How to run / verify locally

```bash
cd hill
python3 -c "import importlib.util,pathlib;s=importlib.util.spec_from_file_location('ev','eval.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(m.eval(pathlib.Path('../solution')))"
```
`eval.py` also reads `private/validation.json` and `private/test.json`, which are **not** distributed with the hill. Where those are small enough to be recoverable they are documented below; otherwise replace that read with your own fixture or call the scoring function directly.

## Solution in this repo

_Not yet — this folder is a task specification only._

## Provenance

- Hill page: https://app.autolab.ai/hills/ottogin/kernel-opt
- Fetched automatically from the AutoLab public API (`/api/v1/hills/<slug>/files`); the files under `hill/` are the hill author's originals, unmodified.
