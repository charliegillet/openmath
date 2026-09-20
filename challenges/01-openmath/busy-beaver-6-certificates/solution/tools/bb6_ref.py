"""Exact re-implementation of alejandrozu/busy-beaver-6-certificates eval.py _run().

Ground truth for verifying candidates offline. Usage:
    python3 bb6_ref.py <spec.bbch> [step_limit]     # spec form: 1RB1RA_1RC1RZ_...
    python3 bb6_ref.py --json <solution.json> [step_limit]
"""
import json, sys
from pathlib import Path

STATES = ("A", "B", "C", "D", "E", "F")
HALT = "H"


def load_spec(spec):
    """bbch 'A0A1_B0B1_...' -> {(state,symbol): (write, move, next_state)}"""
    machine = {}
    groups = spec.split("_")
    assert len(groups) == 6, "need 6 groups"
    for si, g in enumerate(groups):
        state = STATES[si]
        assert len(g) == 6, g
        for k in (0, 1):
            w = int(g[k * 3])
            mv = g[k * 3 + 1]
            nx = g[k * 3 + 2]
            nx = "H" if nx in ("Z", "H", "-") else nx
            machine[(state, k)] = (w, mv, nx)
    return machine


def load_json(path):
    data = json.loads(Path(path).read_text(), object_pairs_hook=lambda pairs: dict(pairs))
    machine = {}
    for state in STATES:
        for sym in ("0", "1"):
            w, mv, nx = data["transitions"][state][sym]
            machine[(state, int(sym))] = (w, mv, nx)
    return machine


def run(machine, step_limit):
    tape = {}
    state, head, steps = "A", 0, 0
    reached = {state}
    leftmost = rightmost = head
    while steps < step_limit:
        symbol = tape.get(head, 0)
        write, move, next_state = machine[(state, symbol)]
        if write:
            tape[head] = 1
        else:
            tape.pop(head, None)
        steps += 1
        head += -1 if move == "L" else 1
        leftmost, rightmost = min(leftmost, head), max(rightmost, head)
        if next_state == HALT:
            return {"halted": True, "steps": steps, "ones": len(tape),
                    "tape_span": rightmost - leftmost + 1, "reached": reached}
        state = next_state
        reached.add(state)
    return {"halted": False, "steps": step_limit, "ones": len(tape),
            "tape_span": rightmost - leftmost + 1, "reached": reached}


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == "--json":
        machine = load_json(args[1]); rest = args[2:]
    else:
        machine = load_spec(args[0]); rest = args[1:]
    # default: run with the TRUE validation budget
    limit = int(rest[0]) if rest else 250000
    r = run(machine, limit)
    missing = sorted(set(STATES) - r["reached"])
    print(json.dumps({
        "halted": r["halted"], "steps": r["steps"], "ones": r["ones"],
        "tape_span": r["tape_span"], "states_reached": len(r["reached"]),
        "missing": missing,
        "passes_validation_250k": r["halted"] and not missing,
    }, indent=2))
