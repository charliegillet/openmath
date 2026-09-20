# Kobon triangles: 18 lines, 93 faces

`solution.json` is an exact integer-line certificate for the AutoLab
`kobon-triangles` hill with its default parameter `n = 18`.

The equations use AutoLab's `[a, b, c]` representation of
`a*x + b*y + c = 0`. The construction is recovered from Johannes Bader's
published 18-line arrangement. `recover_bader.py` converts the published SVG
endpoints to small integer equations and implements the hill's exact
consecutive-arrangement-vertex face counter.

Sources:

- [AutoLab Kobon hill](https://app.autolab.ai/hills/alejandrozu/kobon-triangles)
- [LineOrder Kobon gallery](https://zegalur.github.io/line-order/gallery/kobon.html)
- [OEIS A006066](https://oeis.org/A006066)

Run the local exact check with:

```sh
python3 kobon/recover_bader.py
```

Expected first result:

```text
digits=0 triangles=93 max_coefficient=461387
```
