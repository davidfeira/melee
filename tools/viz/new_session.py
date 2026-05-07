"""Rotate events.jsonl to start a new viz session.

Archives the current `tools/viz/events.jsonl` to
`tools/viz/sessions/YYYYMMDD-HHMM[-name].jsonl` and seeds a fresh
events.jsonl with a single `session_start` event so the viz front-end
can detect the boundary and clear in-memory state.

Usage:
    python tools/viz/new_session.py
    python tools/viz/new_session.py --name overnight-2026-05-08
    python tools/viz/new_session.py --note "Trying surgical extraction"

Idempotent for the case of an already-empty events.jsonl: just writes
the new session_start event without creating an empty archive.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "events.jsonl"
SESSIONS_DIR = ROOT / "sessions"


def _archive(label: str | None) -> Path | None:
    """Copy events.jsonl → sessions/<stamp>[-label].jsonl, then truncate the
    original. Use copy-then-truncate (not rename) so this works on Windows
    even when another process (the viz server) has the file open for read.
    """
    if not EVENTS.exists() or EVENTS.stat().st_size == 0:
        return None
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    name = f"{stamp}.jsonl" if not label else f"{stamp}-{label}.jsonl"
    out = SESSIONS_DIR / name
    counter = 1
    while out.exists():
        name = f"{stamp}-{counter}.jsonl" if not label else f"{stamp}-{label}-{counter}.jsonl"
        out = SESSIONS_DIR / name
        counter += 1
    out.write_bytes(EVENTS.read_bytes())
    # Truncate in place so file handles in other processes stay valid.
    EVENTS.write_text("", encoding="utf-8")
    return out


def _seed(label: str | None, note: str | None, archived: Path | None) -> None:
    EVENTS.touch()
    event = {
        "t": datetime.now(timezone.utc).timestamp(),
        "actor": "system",
        "event": "session_start",
        "label": label or "",
        "note": note or "",
        "previous_archive": archived.name if archived else "",
    }
    # Append (don't overwrite) — _archive already truncated. Append-mode also
    # plays nice with any reader that might still hold the file open.
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=None, help="optional session label")
    ap.add_argument("--note", default=None, help="freeform note")
    args = ap.parse_args()

    archived = _archive(args.name)
    _seed(args.name, args.note, archived)

    if archived:
        size_kb = archived.stat().st_size // 1024
        print(f"archived previous session: {archived.relative_to(ROOT.parent)} ({size_kb} KB)")
    print(f"new session started: events.jsonl seeded with session_start")
    if args.name:
        print(f"  label: {args.name}")
    if args.note:
        print(f"  note:  {args.note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
