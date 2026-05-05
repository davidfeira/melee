#!/usr/bin/env python3
"""Analyze overlap between our local matches and upstream/master.

For each `Match <FuncName>` commit since the last common ancestor with
upstream/master, check whether upstream still has `INCLUDE_ASM(..., FuncName)`
for that function (= they haven't matched it; our work is unique) or has the
function defined (= they matched it independently; possible overlap).

Run: python tools/upstream_overlap.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> str:
    # Read as bytes and decode with replace to survive non-UTF-8 bytes in source files
    # (some upstream .c files contain shift-JIS comments). cp1252 default would crash.
    r = subprocess.run(cmd, capture_output=True, check=False, cwd=ROOT)
    return r.stdout.decode("utf-8", errors="replace")


def main() -> None:
    base = run(["git", "merge-base", "master", "upstream/master"]).strip()
    if not base:
        sys.exit("could not determine merge base with upstream/master")

    # All our local-only commits whose subject starts with "Match "
    log = run(["git", "log", "--format=%H\t%s", f"{base}..master"])
    match_commits: list[tuple[str, str]] = []
    follow_ups: dict[str, list[str]] = {}  # function -> [SHAs] of header/static-h follow-ups
    for line in log.splitlines():
        if not line:
            continue
        sha, _, subject = line.partition("\t")
        if subject.startswith("Match "):
            match_commits.append((sha, subject))
            continue
        # Heuristic: any commit message mentioning a known function name
        # that touches a .h/.static.h file is likely a header follow-up.
        files = run(["git", "show", "--name-only", "--format=", sha]).splitlines()
        if any(f.endswith(".h") or f.endswith(".static.h") for f in files):
            for token in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*_[0-9a-fA-F]{8,})\b", subject):
                follow_ups.setdefault(token, []).append(sha)

    # For each commit, extract function name + the .c file touched
    # The function name is the first token after "Match ".
    # The file is from `git show --name-only`.
    upstream_unique = []   # we matched, upstream still has INCLUDE_ASM
    overlap_pre = []       # already matched in upstream at merge base — we redid it
    overlap_concurrent = []  # upstream matched after merge base — independent overlap
    indeterminate = []     # couldn't determine
    by_tu: dict[str, list[str]] = defaultdict(list)

    def_pattern_for = lambda fn: re.compile(
        r"^\s*(?:static\s+|inline\s+|extern\s+)*"
        r"[A-Za-z_][A-Za-z0-9_*\s]*\s\*?\s*"
        + re.escape(fn) + r"\s*\(",
        re.MULTILINE,
    )

    def file_at(rev: str, path: str) -> str:
        return run(["git", "show", f"{rev}:{path}"])

    for sha, subject in match_commits:
        m = re.match(r"^Match\s+([A-Za-z_][A-Za-z0-9_]*)", subject)
        if not m:
            indeterminate.append((sha, subject, "couldn't parse function name"))
            continue
        func = m.group(1)

        # Find the .c file the commit touched (excluding .h)
        files = run(["git", "show", "--name-only", "--format=", sha]).splitlines()
        c_files = [f for f in files if f.endswith(".c")]
        if not c_files:
            indeterminate.append((sha, subject, f"no .c file in commit"))
            continue
        c_file = c_files[0]
        by_tu[c_file].append(func)

        # Look at upstream's version of that file
        upstream_content = run(["git", "show", f"upstream/master:{c_file}"])
        if not upstream_content:
            # File doesn't exist upstream yet — it's purely ours.
            upstream_unique.append((sha, func, c_file, "file not in upstream"))
            continue

        # Check upstream/master for INCLUDE_ASM or doldecomp placeholder comment
        include_asm_pattern = re.compile(
            r"INCLUDE_ASM\([^)]*,\s*" + re.escape(func) + r"\s*\)"
        )
        # Doldecomp convention: `/// #funcName` placed where the unmatched function would go.
        placeholder_pattern = re.compile(
            r"^\s*///\s*#\s*" + re.escape(func) + r"\s*$",
            re.MULTILINE,
        )
        if include_asm_pattern.search(upstream_content):
            upstream_unique.append((sha, func, c_file, "still INCLUDE_ASM upstream"))
            continue
        if placeholder_pattern.search(upstream_content):
            upstream_unique.append((sha, func, c_file, "/// # placeholder (unmatched upstream)"))
            continue

        # Upstream has matched it. Was it matched BEFORE our merge base, or AFTER?
        # If before → we worked on an already-solved problem (sync hygiene issue).
        # If after → independent concurrent overlap.
        def_pat = def_pattern_for(func)
        if not def_pat.search(upstream_content):
            # Name appears but no definition — likely just a call/reference.
            if re.search(r"\b" + re.escape(func) + r"\b", upstream_content):
                upstream_unique.append((sha, func, c_file, "only referenced (not defined)"))
            else:
                indeterminate.append((sha, subject, f"name not found in upstream {c_file}"))
            continue

        # Definition exists upstream. Check merge base.
        base_content = file_at(base, c_file)
        if base_content and def_pat.search(base_content):
            overlap_pre.append((sha, func, c_file))
        else:
            overlap_concurrent.append((sha, func, c_file))

    print(f"# Match-commit overlap analysis vs upstream/master")
    print(f"# Merge base: {base[:10]}")
    print(f"# Total `Match *` commits since base: {len(match_commits)}")
    print()
    print(f"## Likely OURS-ONLY ({len(upstream_unique)})")
    print(f"   (upstream still has INCLUDE_ASM or doesn't have the file at all — clear contribution candidates)")
    print()
    for sha, func, c_file, reason in upstream_unique[:50]:
        line = f"  {sha[:10]}  {func:50s}  {c_file}  [{reason}]"
        if func in follow_ups:
            line += f"  +header-followups: {','.join(s[:8] for s in follow_ups[func])}"
        print(line)
    if len(upstream_unique) > 50:
        print(f"  ... and {len(upstream_unique) - 50} more")
    print()
    print(f"## REDID-ALREADY-DONE ({len(overlap_pre)})")
    print(f"   (already matched upstream at merge base — pure sync-hygiene loss; nothing to PR)")
    print()
    for sha, func, c_file in overlap_pre[:50]:
        print(f"  {sha[:10]}  {func:50s}  {c_file}")
    if len(overlap_pre) > 50:
        print(f"  ... and {len(overlap_pre) - 50} more")
    print()
    print(f"## CONCURRENT-OVERLAP ({len(overlap_concurrent)})")
    print(f"   (upstream matched after merge base — they got there first; nothing to PR but not stale work either)")
    print()
    for sha, func, c_file in overlap_concurrent[:50]:
        print(f"  {sha[:10]}  {func:50s}  {c_file}")
    if len(overlap_concurrent) > 50:
        print(f"  ... and {len(overlap_concurrent) - 50} more")
    print()
    if indeterminate:
        print(f"## INDETERMINATE ({len(indeterminate)})")
        for sha, subject, reason in indeterminate[:20]:
            print(f"  {sha[:10]}  {subject[:60]}  [{reason}]")
        print()

    # Top TUs by our match count (useful for grouping PRs)
    print(f"## Top TUs by our match count")
    for tu, funcs in sorted(by_tu.items(), key=lambda kv: -len(kv[1]))[:15]:
        print(f"  {len(funcs):4d}  {tu}")


if __name__ == "__main__":
    main()
