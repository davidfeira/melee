"""verify-and-commit: compile, objdiff, label commit truthfully.

Usage:
  python3 tools/state/verify.py <function_name> [--commit] [--note KEY=VALUE]

Steps:
  1. Look up function's TU via report.json (must be present in build/GALE01/report.json).
  2. Compile build/GALE01/src/<tu>.o (or build-linux/... if --linux).
  3. Run objdiff-cli against build/GALE01/obj/<tu>.o.
  4. Read match_percent for the named function.
  5. Print result.  If --commit: stage modified .c/.h files for the TU and commit
     with auto-generated message.
  6. Update notes.jsonl with last_pct + any --note flags.

Commit message format (auto-generated):
  match_percent == 100.0       Match <name>
  100 > pct >= 95              Improve <name> to NN.NN%, log permuter-queued
  pct < 95                     WIP <name> at NN.NN%

Exit codes:
  0 success (regardless of match%)
  2 function not found / no TU mapping
  3 build failed
  4 objdiff failed
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# tools/ first so `from state import state` finds tools/state/state.py and
# not tools/viz/state.py (both modules are named `state.py`).
sys.path.insert(0, str(ROOT / "tools" / "viz"))
sys.path.insert(0, str(ROOT / "tools"))

from state import state as state_mod  # noqa: E402
import events_schema  # noqa: E402

REPORT = ROOT / "build" / "GALE01" / "report.json"
OBJDIFF = ROOT / "build" / "tools" / "objdiff-cli.exe"
VIZ_EVENTS = ROOT / "tools" / "viz" / "events.jsonl"


def _emit_viz_event(name: str, pct: float | None, action: str) -> None:
    """Append an event to tools/viz/events.jsonl so the master-log
    'this session' filter includes functions touched via verify.py.
    """
    import time
    ev = {
        "t": time.time(),
        "actor": "verify",
        "event": events_schema.VERIFY,
        "func": name,
        "match_percent": pct,
        "action": action,
    }
    try:
        VIZ_EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with VIZ_EVENTS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev) + "\n")
    except OSError:
        pass  # Don't fail the verify just because we couldn't log.


def _build_dir(linux: bool) -> Path:
    return ROOT / ("build-linux" if linux else "build") / "GALE01"


def _find_tu(name: str) -> str | None:
    """Return TU path (e.g. melee/gr/grkongo.c) for a function, or None.

    report.json uses 'main/melee/.../foo' format (no extension).  We normalize
    to 'melee/.../foo.c' which matches the on-disk src/ layout.
    """
    if not REPORT.exists():
        return None
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    for unit in data.get("units", []):
        for fn in unit.get("functions", []):
            if fn.get("name") == name:
                raw = unit.get("name", "")
                # Drop 'main/' prefix; add .c suffix.
                if raw.startswith("main/"):
                    raw = raw[len("main/"):]
                return raw + ".c"
    return None


def _ninja(target: str, linux: bool) -> None:
    cmd = ["ninja", target]
    if linux:
        # On Windows host, ninja runs under WSL Ubuntu.
        cmd = ["wsl", "-d", "Ubuntu", "--"] + cmd
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(3)


def _objdiff_all(tu: str, linux: bool) -> dict[str, float | None]:
    """Run objdiff once for the whole TU and return {fn_name: match_percent}.

    Captures every function in the .o, not just the target — lets the caller
    detect regressions in *neighboring* functions when an edit's side effects
    (e.g. const reorder, struct change, header signature update) ripple out.
    """
    bd = _build_dir(linux)
    obj_o = bd / "obj" / tu.replace(".c", ".o")
    src_o = bd / "src" / tu.replace(".c", ".o")
    if not obj_o.exists():
        sys.stderr.write(f"reference .o missing: {obj_o}\n")
        raise SystemExit(4)
    if not src_o.exists():
        sys.stderr.write(f"compiled .o missing: {src_o}\n")
        raise SystemExit(4)

    out_path = ROOT / "build" / "GALE01" / "_verify.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(OBJDIFF), "diff", "-1", str(obj_o), "-2", str(src_o), "-o", str(out_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(4)

    diff = json.loads(out_path.read_text(encoding="utf-8"))
    out: dict[str, float | None] = {}
    for sym in diff.get("left", {}).get("symbols", []):
        # Skip data-section pseudo-symbols (flags & 2 == data).
        if sym.get("flags", 0) & 2:
            continue
        name = sym.get("name")
        if not name:
            continue
        pct = sym.get("match_percent")
        out[name] = float(pct) if isinstance(pct, (int, float)) else None
    return out


def _objdiff_match_percent(tu: str, fname: str, linux: bool) -> float | None:
    """Convenience: scan whole TU and return target function's match%."""
    all_fns = _objdiff_all(tu, linux)
    return all_fns.get(fname)


_BASELINE_PATH = ROOT / "tools" / "state" / "baseline.json"
_BASELINE_CACHE: dict | None = None


def _load_baseline() -> dict:
    """Load tools/state/baseline.json — upstream/master per-fn pcts snapshot.

    Generated by `tools/state/baseline.py --all`. This is the truthful
    reference for regression detection. Comparing against notes.jsonl
    `last_pct` is unreliable because those values came from backfilled
    commit messages (the same mislabeled "Match" claims that prompted
    this whole subsystem).
    """
    global _BASELINE_CACHE
    if _BASELINE_CACHE is not None:
        return _BASELINE_CACHE
    if _BASELINE_PATH.exists():
        try:
            _BASELINE_CACHE = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
        except Exception:
            _BASELINE_CACHE = {}
    else:
        _BASELINE_CACHE = {}
    return _BASELINE_CACHE


def _baseline_pct(name: str, tu: str | None = None) -> float | None:
    """Truthful baseline match% for a function. Prefers baseline.json
    (snapshot of upstream/master) and falls back to notes.jsonl `last_pct`
    when the baseline file is missing or doesn't cover this TU."""
    baseline = _load_baseline()
    if tu and tu in baseline and name in baseline[tu]:
        return float(baseline[tu][name])
    try:
        st = state_mod.get_state(name)
    except Exception:
        return None
    if st is None:
        return None
    last = st.notes.get(state_mod.KEY_LAST_PERCENT)
    if isinstance(last, (int, float)):
        return float(last)
    if isinstance(st.match_percent, (int, float)):
        return float(st.match_percent)
    return None


def _scan_regressions(current: dict[str, float | None],
                       target: str,
                       tu: str | None = None) -> tuple[list[str], list[str], list[str]]:
    """Compare the TU's current match% against each function's recorded
    baseline. Returns (regressions, improvements, unchanged) — each a list
    of human-readable lines. Excludes the target function itself."""
    reg: list[str] = []
    imp: list[str] = []
    unch: list[str] = []
    for name, pct in current.items():
        if name == target:
            continue
        if pct is None:
            continue
        baseline = _baseline_pct(name, tu)
        if baseline is None:
            continue
        delta = pct - baseline
        # 0.01% threshold to ignore floating-point noise.
        if delta < -0.01:
            reg.append(f"  {name}: {baseline:.4f}% -> {pct:.4f}%  ({delta:+.4f})")
        elif delta > 0.01:
            imp.append(f"  {name}: {baseline:.4f}% -> {pct:.4f}%  ({delta:+.4f})")
        else:
            unch.append(name)
    return reg, imp, unch


def _commit_message(name: str, pct: float | None) -> str:
    if pct is None:
        return f"WIP {name} (objdiff returned no match% — function not in compiled .o)"
    if pct >= 100.0:
        return f"Match {name}"
    if pct >= 95.0:
        return f"Improve {name} to {pct:.2f}%, log permuter-queued"
    return f"WIP {name} at {pct:.2f}%"


def _commit(tu: str, msg: str) -> None:
    # Stage everything under the TU's directory plus the matching header dir.
    src_path = ROOT / "src" / tu
    files = [src_path]
    # Include the matching header if present.
    h_path = src_path.with_suffix(".h")
    if h_path.exists():
        files.append(h_path)

    rels = [str(p.relative_to(ROOT)) for p in files]
    subprocess.run(["git", "add"] + rels, cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="function symbol")
    ap.add_argument("--commit", action="store_true", help="git-add + git-commit on success")
    ap.add_argument("--linux", action="store_true", help="use build-linux/ via WSL Ubuntu")
    ap.add_argument(
        "--note",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="append annotation; KEY in {status,blocker} (repeatable)",
    )
    ap.add_argument(
        "--auto-permute",
        action="store_true",
        help="if match%% < 100, hand off to `tools/permute.py dispatch` automatically",
    )
    ap.add_argument(
        "--allow-regression",
        action="store_true",
        help="proceed even if a neighboring function in the TU regressed below "
             "its previously-recorded match%% (otherwise the commit step is "
             "blocked — this is the local equivalent of upstream's diff CI)",
    )
    args = ap.parse_args()

    tu = _find_tu(args.name)
    if not tu:
        sys.stderr.write(f"no TU found for {args.name} in report.json\n")
        return 2

    # Compile the TU.
    bd_prefix = "build-linux" if args.linux else "build"
    target = f"{bd_prefix}/GALE01/src/{tu.replace('.c', '.o')}"
    print(f"[1/4] compile {target}")
    _ninja(target, args.linux)

    # Diff the whole TU — captures the target function AND every neighbor.
    print(f"[2/4] objdiff full TU vs reference")
    all_fns = _objdiff_all(tu, args.linux)
    pct = all_fns.get(args.name)
    label = "?" if pct is None else f"{pct:.2f}%"
    print(f"      target {args.name}: {label}")

    # Local mirror of upstream's diff CI: scan every other function in the TU
    # for regressions against its previously-recorded match%.  Catches edits
    # whose side effects ripple beyond the named function (e.g. const reorder,
    # struct change, header signature change).
    print(f"[3/4] regression scan ({len(all_fns)-1} neighbors)")
    regressions, improvements, _ = _scan_regressions(all_fns, args.name, tu)
    if improvements:
        print("      improvements:")
        for line in improvements:
            print(line)
    if regressions:
        print("      !! REGRESSIONS:")
        for line in regressions:
            print(line)

    # Persist last_pct only for the TARGET function. Updating every neighbor
    # would erase the regression baseline (we'd be saying "current state is
    # the reference now") — defeats the purpose. Use baseline.py to refresh
    # the canonical upstream snapshot when needed.
    state_mod.add_note(args.name, state_mod.KEY_LAST_PERCENT, pct, tu=tu)

    # Emit to viz so the master-log "this session" filter sees it.
    _emit_viz_event(args.name, pct, "verify")
    for note in args.note:
        if "=" not in note:
            sys.stderr.write(f"--note must be KEY=VALUE; got {note!r}\n")
            return 2
        k, v = note.split("=", 1)
        state_mod.add_note(args.name, k, v, tu=tu)

    # Block the commit if we caused a regression (unless explicitly overridden).
    if regressions and not args.allow_regression:
        print(f"[4/4] commit BLOCKED — {len(regressions)} regression(s) above")
        print("      pass --allow-regression to override (and then explain in")
        print("      the commit message why the regression is acceptable)")
        return 5

    # Commit if asked.
    msg = _commit_message(args.name, pct)
    if args.commit:
        print(f"[4/4] commit: {msg}")
        _commit(tu, msg)
    else:
        print(f"[4/4] would-commit: {msg}  (rerun with --commit to apply)")

    # Auto-permute hand-off: if match is incomplete, queue for permuter.
    if args.auto_permute and pct is not None and pct < 100.0:
        print(f"[+] auto-permute: dispatching {args.name} to permuter cluster")
        rc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "permute.py"), "dispatch", args.name],
            cwd=ROOT,
        ).returncode
        state_mod.add_note(
            args.name, "auto_permute_dispatched", rc == 0, tu=tu, exit_code=rc
        )
        if rc != 0:
            print(f"[!] permute dispatch returned {rc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
