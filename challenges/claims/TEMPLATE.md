# Claim: <hill slug>

worker: <your GitHub handle>
started: <YYYY-MM-DD>
status: in-progress        # in-progress | done | stalled | abandoned
branch: hill/<hill-slug>

## Approach

One or two lines on what you are actually trying. Be concrete — "seeded mutation
search over known long-runtime machines, capped at the recovered step budget", not
"working on it".

## Result

Verified metric values, verbatim from the hill's own `eval.py`, plus the exact
command that produced them. Leave as `pending` until you have them.

```
command: <exact command>
output:  <verbatim>
```

## Limitations

What this does NOT prove. Unknowns, unverified steps, and anything you gave up on.
