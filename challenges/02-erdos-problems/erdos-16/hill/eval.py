"""Evaluator for a Lean proof hill.

The hill fixes the theorem in statement.lean (which ends at ``:=``). The
submission provides only the proof that follows. They are concatenated,
``#print axioms hill`` is appended, and the file is checked with Lean inside the
hill's image (environment.image), against the formal-conjectures project's
Mathlib. A proof counts only if it compiles, uses no ``sorry``, and depends on
no axioms beyond Lean and Mathlib's standard three.

The evaluator narrates each step to stdout and streams Lean's own output as it
arrives, so the run log shows what is happening during the ~1-2 min compile
instead of sitting blank.
"""

import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

HILL = Path(__file__).resolve().parent
PROJECT = os.environ.get("LEAN_PROJECT", "/opt/formal-conjectures")
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
LEAN_TIMEOUT_S = 1500


def _say(msg):
    """A progress line in the run log."""
    print(f"[lean] {msg}", flush=True)


def _config():
    return [
        {"name": "prover", "value": "lean4", "primary": True},
        {"name": "toolchain", "value": "v4.33.1", "primary": True},
    ]


def _fail(error, **extra):
    _say(f"FAILED: {error}")
    return {"passed": False, "metrics": [], "config": _config(), "details": {"error": error, **extra}}


def _tail(text, n=40):
    return "\n".join(text.strip().splitlines()[-n:])


def _axioms(output):
    if "does not depend on any axioms" in output:
        return set()
    match = re.search(r"depends on axioms:\s*\[([^\]]*)\]", output, re.S)
    if not match:
        return None
    return {a.strip() for a in match.group(1).split(",") if a.strip()}


def _run_lean(check_file, workdir, env):
    """Run Lean, streaming its combined output to stdout as it arrives, and
    return (output, returncode, timed_out). A watchdog thread kills the whole
    process group if Lean overruns ``LEAN_TIMEOUT_S``."""
    proc = subprocess.Popen(
        ["lean", str(check_file)],
        cwd=str(workdir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    timed_out = {"hit": False}

    def _kill():
        timed_out["hit"] = True
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass

    timer = threading.Timer(LEAN_TIMEOUT_S, _kill)
    timer.start()
    lines = []
    try:
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            lines.append(line)
    finally:
        proc.wait()
        timer.cancel()
    return "".join(lines), proc.returncode, timed_out["hit"]


def eval(submission, *, final=False):
    proof = submission / "solution.lean"
    if not proof.is_file():
        return _fail("submission must contain solution.lean (the proof after the theorem's ':=')")
    statement = (HILL / "statement.lean").read_text().rstrip()
    proof_text = proof.read_text().strip()
    source = statement + "\n" + proof_text + "\n\n#print axioms hill\n"

    _say(f"theorem: {statement.splitlines()[-1].strip()}")
    _say(f"submission: {len(proof_text.splitlines())} line(s) of proof")

    scratch = os.environ.get("HILLS_RUN_DIR") or None
    workdir = Path(tempfile.mkdtemp(prefix="lean-", dir=scratch))
    check_file = workdir / "Check.lean"
    check_file.write_text(source)
    env = dict(os.environ)
    env["HOME"] = str(workdir)
    lake = Path(PROJECT) / ".lake"
    libs = [lake / "build" / "lib" / "lean", *sorted((lake / "packages").glob("*/.lake/build/lib/lean"))]
    env["LEAN_PATH"] = ":".join(str(p) for p in libs if p.is_dir())

    _say("compiling with Lean 4 (v4.33.1) + Mathlib; this usually takes 1-2 minutes...")
    try:
        output, returncode, timed_out = _run_lean(check_file, workdir, env)
    except FileNotFoundError:
        return _fail("lean was not found on PATH inside the image")
    if timed_out:
        return _fail(f"lean did not finish within {LEAN_TIMEOUT_S}s")

    if "sorryAx" in output or "declaration uses 'sorry'" in output:
        return _fail("the proof uses sorry", output=_tail(output))
    if returncode != 0:
        return _fail("the proof did not compile", output=_tail(output))
    axioms = _axioms(output)
    if axioms is None:
        return _fail("could not read the axiom list Lean printed", output=_tail(output))
    extra = axioms - ALLOWED_AXIOMS
    if extra:
        return _fail(
            f"the proof depends on non-standard axioms: {sorted(extra)}", output=_tail(output)
        )

    _say(f"PROVED. axioms: {sorted(axioms)}")
    return {
        "passed": True,
        "metrics": [{"name": "proved", "value": 1.0, "direction": "max"}],
        "config": _config(),
        "details": {"axioms": sorted(axioms)},
    }
