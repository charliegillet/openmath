# OpenMath foundational Lean proof

This is a minimal Lean 4 project pinned to Lean `v4.34.0`.

```sh
lake build
```

The project builds a foundational proof in `OpenMath/Foundation.lean`. That
module imports nothing—not even Lean's standard prelude. It defines its own
equality and Peano numbers, then starts from an addition operation and its two
defining Peano axioms.

```lean
theorem one_plus_one_is_two : Same (plus one one) two :=
  same_trans
    (plus_next one Peano.zero)
    (next_respects_same (plus_zero one))
```

Run only the foundational proof, including its axiom audit, with:

```sh
lake env lean OpenMath/Foundation.lean
```

The same result is proved using Lean's standard library in
`OpenMath/Standard.lean`:

```lean
theorem one_plus_one_is_two : 1 + 1 = 2 := by
  rfl
```

Run that proof independently with:

```sh
lake env lean OpenMath/Standard.lean
```

The Kobon construction is also independently checked in Lean:

```sh
lake env lean OpenMath/Kobon.lean
```

Lean computes all exact rational intersections and proves that the 18 submitted
lines have exactly 93 bounded triangular faces under AutoLab's face rule.

For 18 lines, 93 is the current published lower bound and 94 is the known upper
bound. This repository verifies the known 93-face construction; it does not
claim a new record or prove optimality.

## challenges/

`challenges/` is an archive of 45 [AutoLab](https://app.autolab.ai) hills from four public lists, each in its own folder with the hill's own unmodified source under `hill/`, a plain-language README (what it is, what to prove, how to run) and — where solved — a verified `solution/`.

The six curated hills from [`alejandrozu/openmath`](https://app.autolab.ai/lists/alejandrozu/openmath) live in `challenges/01-openmath/`. See `challenges/README.md` for the index.

Hill sources are public and are re-fetched through the AutoLab REST API; the API key is read only from the `AUTOLAB_API_KEY` environment variable and is never stored in this repository.
