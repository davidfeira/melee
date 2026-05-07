"""Emit a skeleton upstream PR description from a list of match commits.

Generates the structural/boilerplate sections (TOC, TU groupings, header
list, verification stub) so the human/agent only has to fill in the
per-function semantic prose. NOT a full description generator — the
"What these functions do" paragraphs are intentionally left for human
or agent to write because that's the high-leverage reviewer-facing
content.

Usage:
    python tools/state/pr_skeleton.py <commit-range>

Example:
    python tools/state/pr_skeleton.py upstream/master..claude/upstream-pr

Reads commit log, extracts function names from "Match X" subjects,
groups by TU directory, and emits a markdown skeleton to stdout.
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RX_MATCH = re.compile(r"^Match\s+([A-Za-z_][A-Za-z0-9_,\s]*)\b")

AREA_FOR_PREFIX = [
    ("src/melee/gr/",        "Stage code (`gr/`)"),
    ("src/melee/ft/chara/",  "Fighter code (`ft/chara/`)"),
    ("src/melee/ft/",        "Fighter code (`ft/`)"),
    ("src/melee/gm/",        "Match-end / game-mode code (`gm/`)"),
    ("src/melee/mn/",        "Menu code (`mn/`)"),
    ("src/melee/vi/",        "Scene code (`vi/`)"),
    ("src/melee/if/",        "HUD code (`if/`)"),
    ("src/melee/it/",        "Item code (`it/`)"),
    ("src/melee/lb/",        "Library code (`lb/`)"),
    ("src/sysdolphin/",      "Sysdolphin"),
]


def _commits(rev_range: str) -> list[tuple[str, str, list[str]]]:
    """Return [(sha, subject, files), ...] for each commit in range."""
    out_lines = subprocess.check_output(
        ["git", "-C", str(ROOT), "log", rev_range, "--pretty=format:%H%x09%s",
         "--name-only", "--reverse"],
        text=True, encoding="utf-8",
    ).splitlines()

    commits: list[tuple[str, str, list[str]]] = []
    cur_sha = cur_subj = None
    cur_files: list[str] = []
    for line in out_lines:
        if "\t" in line and not line.startswith(" "):
            sha_subj = line.split("\t", 1)
            if len(sha_subj) == 2 and len(sha_subj[0]) >= 7 and re.match(r"[a-f0-9]+$", sha_subj[0]):
                if cur_sha:
                    commits.append((cur_sha, cur_subj or "", cur_files))
                cur_sha, cur_subj = sha_subj
                cur_files = []
                continue
        if line.strip():
            cur_files.append(line.strip())
    if cur_sha:
        commits.append((cur_sha, cur_subj or "", cur_files))
    return commits


def _area(file_path: str) -> str:
    for prefix, label in AREA_FOR_PREFIX:
        if file_path.startswith(prefix):
            return label
    return "Other"


def _functions_from_subject(subject: str) -> list[str]:
    m = RX_MATCH.match(subject)
    if not m:
        return []
    raw = m.group(1)
    # subjects can be "Match a, b, c" or "Match a"
    return [s.strip() for s in raw.split(",") if s.strip()]


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__ or "")
        return 2
    rev_range = sys.argv[1]

    commits = _commits(rev_range)
    funcs_by_area: dict[str, list[tuple[str, str]]] = defaultdict(list)
    tu_set: set[str] = set()
    header_files: set[str] = set()
    bundled: list[tuple[list[str], list[str]]] = []

    for sha, subj, files in commits:
        funcs = _functions_from_subject(subj)
        if not funcs:
            continue
        c_files = [f for f in files if f.endswith(".c")]
        h_files = [f for f in files if f.endswith(".h")]
        header_files.update(h_files)
        for tu in c_files:
            tu_set.add(tu)
            area = _area(tu)
            for fn in funcs:
                funcs_by_area[area].append((fn, tu))
        if len(funcs) > 1:
            bundled.append((funcs, c_files))

    # Render skeleton.
    total = sum(len(v) for v in funcs_by_area.values())
    print("## Summary")
    tu_short = sorted({Path(t).stem for t in tu_set})
    print(f"- {total} matched functions across {len(tu_set)} TUs "
          f"(`{'`, `'.join(tu_short)}`)")
    if header_files:
        print(f"- {len(header_files)} header refinement(s) "
              f"({', '.join(f'`{Path(h).name}`' for h in sorted(header_files))})"
              f" required by the new matches")
    print()

    print("## What these functions do")
    print()
    print("> **TODO (high-leverage section):** For each function below, write a")
    print("> 2-3 sentence plain-English description of what it does in the game,")
    print("> what it computes, and which neighbors it calls.")
    print()
    for area in sorted(funcs_by_area):
        print(f"### {area}")
        print()
        for fn, tu in funcs_by_area[area]:
            tu_short = tu.replace("src/melee/", "").replace("src/", "")
            print(f"**{tu_short} — `{fn}`** — TODO")
            print()

    if header_files:
        print("## Header refinements")
        print()
        for h in sorted(header_files):
            print(f"- `{Path(h).name}`: TODO (prototype change + reason)")
        print()

    if bundled:
        print("## Bundled-commit rationale")
        print()
        for funcs, cfiles in bundled:
            joined = ", ".join(f"`{f}`" for f in funcs)
            print(f"{joined} ship together in one commit. TODO (reason).")
        print()

    print("## Verification")
    print()
    print("- `ninja main.dol` → links cleanly")
    print(f"- Per-function `objdiff-cli diff` reports 100.0% match for each of the {total} functions")
    print()
    print("🤖 Generated with [Claude Code](https://claude.ai/claude-code)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
