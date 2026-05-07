"""Backfill tools/state/notes.jsonl from existing commit history.

Scans `git log upstream/master..origin/master` and seeds annotation events for
every "Improve X to NN.NN%" / "Match X" / "Log X stuck" commit. Combined with
the truthful state from report.json, this gives the operator full visibility
into what's been worked on and what state it's in — without needing the viz
to scrape commit messages on every page load.

Idempotent: re-running won't duplicate entries (we de-dupe by (name, key, value)).

Usage:
    python tools/state/backfill.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from state import state as state_mod  # noqa: E402

# Match patterns:
#   Match Foo
#   Improve Foo to 87.42%
#   Improve Foo to 87.42%, log permuter-queued
#   Improve Foo to 87.42%, log permuter-queued (commit-match blocked by sibling WIP)
#   Log Foo stuck (data-layout blocker)
#
# Use raw subject line; tolerate trailing context in parens.

RX_MATCH = re.compile(r"^Match\s+([A-Za-z_][A-Za-z0-9_]*)\b")
RX_IMPROVE = re.compile(
    r"^Improve\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+to\s+([\d.]+)%)?(?:.*?(permuter-queued|permuter-ready|permuter-dispatched))?(?:.*?\((.*?)\))?",
)
# "fn_name: 0% -> 93.5% + permuter-queued [+ header]"  — alternate format
RX_PROGRESS = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)(?:_OnEnter|_OnExit|_OnLoad|_OnStart)?\s*:\s*[\d.]+%\s*->\s*([\d.]+)%\s*(?:\+.*?(permuter-queued|permuter-ready|permuter-dispatched))?",
)
RX_STUCK = re.compile(r"^Log\s+([A-Za-z_][A-Za-z0-9_]*)\s+stuck(?:\s*\((.*?)\))?", re.I)


def _existing_keys() -> set[tuple[str, str, str]]:
    """Read notes.jsonl, return (name, key, str(value)) tuples already recorded."""
    out: set[tuple[str, str, str]] = set()
    if not state_mod.NOTES_PATH.exists():
        return out
    for line in state_mod.NOTES_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        out.add((ev.get("name") or "", ev.get("key") or "", json.dumps(ev.get("value"))))
    return out


def _git_log() -> list[tuple[str, int, str]]:
    """Return [(sha, ts_unix, subject), ...] for upstream/master..origin/master."""
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "log",
            "upstream/master..origin/master",
            "--pretty=format:%H\t%at\t%s",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return []
    out: list[tuple[str, int, str]] = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        sha, ts, subj = parts
        try:
            out.append((sha, int(ts), subj))
        except ValueError:
            continue
    return out


def _emit(events: list[dict], dry_run: bool) -> None:
    if dry_run:
        for e in events:
            print(json.dumps(e))
        return
    state_mod.NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with state_mod.NOTES_PATH.open("a", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seen = _existing_keys()
    log = _git_log()
    print(f"scanning {len(log)} commits on upstream/master..origin/master", file=sys.stderr)

    new_events: list[dict] = []
    counts = {"match_seen": 0, "improve_seen": 0, "stuck_seen": 0, "appended": 0}

    for sha, ts, subj in log:
        ts_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")

        if m := RX_STUCK.match(subj):
            name, reason = m.group(1), m.group(2) or ""
            counts["stuck_seen"] += 1
            evk = (name, "status", json.dumps("blocked"))
            if evk in seen:
                continue
            new_events.append(
                {
                    "ts": ts_iso,
                    "name": name,
                    "key": "status",
                    "value": "blocked",
                    "source_commit": sha[:9],
                    "blocker_reason": reason,
                }
            )
            seen.add(evk)
            counts["appended"] += 1
            continue

        if m := RX_IMPROVE.match(subj):
            name, pct, perm_tag, paren = m.group(1), m.group(2), m.group(3), m.group(4)
            counts["improve_seen"] += 1
            try:
                pct_f = float(pct) if pct else None
            except ValueError:
                pct_f = None

            if pct_f is not None:
                evk = (name, "last_pct", json.dumps(pct_f))
                if evk not in seen:
                    new_events.append(
                        {
                            "ts": ts_iso,
                            "name": name,
                            "key": "last_pct",
                            "value": pct_f,
                            "source_commit": sha[:9],
                        }
                    )
                    seen.add(evk)
                    counts["appended"] += 1

            if perm_tag:
                evk = (name, "status", json.dumps("permuter-queued"))
                if evk not in seen:
                    extra = {"blocker_reason": paren} if paren else {}
                    new_events.append(
                        {
                            "ts": ts_iso,
                            "name": name,
                            "key": "status",
                            "value": "permuter-queued",
                            "source_commit": sha[:9],
                            **extra,
                        }
                    )
                    seen.add(evk)
                    counts["appended"] += 1
            continue

        if m := RX_PROGRESS.match(subj):
            name, pct, perm_tag = m.group(1), m.group(2), m.group(3)
            counts["improve_seen"] += 1
            try:
                pct_f = float(pct) if pct else None
            except ValueError:
                pct_f = None

            if pct_f is not None:
                evk = (name, "last_pct", json.dumps(pct_f))
                if evk not in seen:
                    new_events.append(
                        {"ts": ts_iso, "name": name, "key": "last_pct",
                         "value": pct_f, "source_commit": sha[:9]}
                    )
                    seen.add(evk)
                    counts["appended"] += 1

            if perm_tag:
                evk = (name, "status", json.dumps("permuter-queued"))
                if evk not in seen:
                    new_events.append(
                        {"ts": ts_iso, "name": name, "key": "status",
                         "value": "permuter-queued", "source_commit": sha[:9]}
                    )
                    seen.add(evk)
                    counts["appended"] += 1
            continue

        if m := RX_MATCH.match(subj):
            name = m.group(1)
            counts["match_seen"] += 1
            # Hand-typed "Match X" doesn't itself prove 100%. The truthful
            # match% comes from report.json. We just note that the user
            # claimed it as a match, so mismatches are detectable later.
            evk = (name, "user_claimed_match", json.dumps(sha[:9]))
            if evk not in seen:
                new_events.append(
                    {
                        "ts": ts_iso,
                        "name": name,
                        "key": "user_claimed_match",
                        "value": sha[:9],
                    }
                )
                seen.add(evk)
                counts["appended"] += 1

    _emit(new_events, args.dry_run)
    print(f"counts: {counts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
