"""Snapshot upstream/master's per-function match% as the regression baseline.

`tools/state/verify.py --allow-regression` compares the post-edit TU build
against this baseline. Without it, the regression scan would compare against
`notes.jsonl` (annotations populated from commit messages, which are
unreliable — the whole reason we built the truthful state system).

What this does:
  1. For each TU passed on the command line (or all TUs we have notes for),
     check out upstream/master's version of that .c file (and its .h if present)
  2. Build the .o under build-linux/GALE01/src/...
  3. Run objdiff vs the prebuilt obj/.../*.o reference
  4. Record per-function match% to tools/state/baseline.json
  5. Restore the working-tree state when done

Usage:
  python tools/state/baseline.py <tu> [<tu> ...]      # specific TUs
  python tools/state/baseline.py --all                # every TU we touch
  python tools/state/baseline.py --refresh            # alias for --all

Output: tools/state/baseline.json — {tu_name: {function_name: match_percent}}.
The file lives in git so collaborators share the same reference.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "viz"))
sys.path.insert(0, str(ROOT / "tools"))

BASELINE_PATH = ROOT / "tools" / "state" / "baseline.json"
OBJDIFF = ROOT / "build" / "tools" / "objdiff-cli.exe"


def _load() -> dict[str, dict[str, float]]:
    if BASELINE_PATH.exists():
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {}


def _save(data: dict[str, dict[str, float]]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True), encoding="utf-8"
    )


def _objdiff_all(tu: str, linux: bool = True) -> dict[str, float]:
    bd = ROOT / ("build-linux" if linux else "build") / "GALE01"
    obj_o = bd / "obj" / tu.replace(".c", ".o")
    src_o = bd / "src" / tu.replace(".c", ".o")
    out_path = ROOT / "build" / "GALE01" / "_baseline.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(OBJDIFF), "diff", "-1", str(obj_o), "-2", str(src_o), "-o", str(out_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        return {}
    diff = json.loads(out_path.read_text(encoding="utf-8"))
    out: dict[str, float] = {}
    for sym in diff.get("left", {}).get("symbols", []):
        if sym.get("flags", 0) & 2:
            continue
        name = sym.get("name")
        pct = sym.get("match_percent")
        if name and isinstance(pct, (int, float)):
            out[name] = float(pct)
    return out


def _ninja(target: str, linux: bool = True) -> bool:
    cmd = ["ninja", target]
    if linux:
        cmd = ["wsl", "-d", "Ubuntu", "--"] + cmd
    return subprocess.run(cmd, cwd=ROOT).returncode == 0


def _files_for_tu(tu: str) -> list[Path]:
    """The .c file plus any header in the same directory with the same stem."""
    src_c = ROOT / "src" / tu
    files = [src_c]
    src_h = src_c.with_suffix(".h")
    if (ROOT / src_h.relative_to(ROOT)).exists():
        files.append(src_h)
    return files


def snapshot_tu(tu: str) -> dict[str, float] | None:
    """Build upstream/master's version of `tu` and return per-fn pcts."""
    files = _files_for_tu(tu)
    rels = [str(f.relative_to(ROOT)) for f in files]

    # Stash current state of these files only (not the whole tree).
    # We use `git stash push -- <paths>` so we don't fight with .venv etc.
    stash_proc = subprocess.run(
        ["git", "-C", str(ROOT), "stash", "push", "--keep-index", "--",] + rels,
        capture_output=True, text=True,
    )
    stashed = "Saved working directory" in stash_proc.stdout
    try:
        subprocess.run(
            ["git", "-C", str(ROOT), "checkout", "upstream/master", "--"] + rels,
            check=False, capture_output=True,
        )
        target = f"build-linux/GALE01/src/{tu.replace('.c', '.o')}"
        if not _ninja(target):
            return None
        return _objdiff_all(tu)
    finally:
        # Restore the file from index/HEAD.
        subprocess.run(
            ["git", "-C", str(ROOT), "checkout", "HEAD", "--"] + rels,
            check=False, capture_output=True,
        )
        if stashed:
            subprocess.run(
                ["git", "-C", str(ROOT), "stash", "pop"],
                check=False, capture_output=True,
            )
        # Recompile so the .o reflects the working tree, not upstream.
        subprocess.run(
            ["wsl", "-d", "Ubuntu", "--", "ninja",
             f"build-linux/GALE01/src/{tu.replace('.c', '.o')}"],
            cwd=ROOT, check=False, capture_output=True,
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tus", nargs="*", help="TU paths like melee/gr/grzebes.c")
    ap.add_argument("--all", action="store_true",
                    help="snapshot every TU referenced in tools/state/notes.jsonl")
    ap.add_argument("--refresh", action="store_true", help="alias for --all")
    args = ap.parse_args()

    tus = list(args.tus)
    if args.all or args.refresh:
        # Pull TU set from notes.jsonl events.
        notes = ROOT / "tools" / "state" / "notes.jsonl"
        if notes.exists():
            seen = set()
            for line in notes.read_text(encoding="utf-8").splitlines():
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                tu = ev.get("tu")
                if tu and tu not in seen:
                    seen.add(tu)
                    tus.append(tu)

    if not tus:
        ap.print_help()
        return 2

    baseline = _load()
    for tu in tus:
        print(f"snapshot {tu}", file=sys.stderr)
        snap = snapshot_tu(tu)
        if snap is None:
            print(f"  failed", file=sys.stderr)
            continue
        baseline[tu] = snap
        print(f"  recorded {len(snap)} functions", file=sys.stderr)

    _save(baseline)
    print(f"wrote {BASELINE_PATH.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
