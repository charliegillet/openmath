"""Exact blank-tape evaluator for six-state, two-symbol Busy Beaver candidates."""

from __future__ import annotations

import json
from pathlib import Path


HILL = Path(__file__).resolve().parent
STATES = ("A", "B", "C", "D", "E", "F")
HALT = "H"
MAX_BYTES = 16_384


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _load_machine(submission: Path):
    path = Path(submission) / "solution.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("submission must contain a regular solution.json")
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError(f"solution.json exceeds the {MAX_BYTES}-byte size limit")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"transitions"} or not isinstance(data["transitions"], dict):
        raise ValueError('solution.json must contain only a "transitions" object')
    transition_rows = data["transitions"]
    if set(transition_rows) != set(STATES):
        raise ValueError("transitions must define exactly states A through F")
    machine = {}
    for state in STATES:
        row = transition_rows[state]
        if not isinstance(row, dict) or set(row) != {"0", "1"}:
            raise ValueError(f"transitions.{state} must define exactly symbols 0 and 1")
        for symbol_text in ("0", "1"):
            entry = row[symbol_text]
            if not isinstance(entry, list) or len(entry) != 3:
                raise ValueError(f"transitions.{state}.{symbol_text} must be [write, move, next_state]")
            write, move, next_state = entry
            if type(write) is not int or write not in (0, 1):
                raise ValueError(f"transitions.{state}.{symbol_text}.write must be 0 or 1")
            if move not in ("L", "R") or next_state not in {*STATES, HALT}:
                raise ValueError(f"transitions.{state}.{symbol_text} contains an invalid move or state")
            machine[(state, int(symbol_text))] = (write, move, next_state)
    return machine


def _private_limit(final: bool) -> int:
    filename = "test.json" if final else "validation.json"
    data = json.loads((HILL / "private" / filename).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"step_limit"} or type(data["step_limit"]) is not int:
        raise ValueError("private execution-budget schema is invalid")
    if not 10 <= data["step_limit"] <= 2_000_000:
        raise ValueError("private execution budget is outside safe limits")
    return data["step_limit"]


def _run(machine, step_limit: int):
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
            return {"halted": True, "steps": steps, "ones": len(tape), "tape_span": rightmost - leftmost + 1, "reached": reached}
        state = next_state
        reached.add(state)
    return {"halted": False, "steps": step_limit, "ones": len(tape), "tape_span": rightmost - leftmost + 1, "reached": reached}


def _config(final: bool):
    return [
        {"name": "machine_model", "value": "6-state-2-symbol-standard-tm", "primary": True},
        {"name": "initial_tape", "value": "bi-infinite-zero", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]


def eval(submission: Path, *, final: bool = False) -> dict:
    config = _config(final)
    try:
        machine = _load_machine(submission)
        run = _run(machine, _private_limit(final))
        if not run["halted"]:
            raise ValueError("machine did not halt within the private execution budget")
        missing = sorted(set(STATES) - run["reached"])
        if missing:
            raise ValueError(f"machine halted without reaching all six states; missing {', '.join(missing)}")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, RecursionError) as error:
        return {"passed": False, "metrics": [], "config": config, "details": {"error": str(error)[:400]}}
    return {
        "passed": True,
        "metrics": [
            {"name": "steps", "value": run["steps"], "direction": "max"},
            {"name": "ones", "value": run["ones"], "direction": "max"},
            {"name": "tape_span", "value": run["tape_span"], "direction": "max"},
        ],
        "config": config,
        "details": {"halting_verified": True, "states_reached": len(run["reached"])},
    }
