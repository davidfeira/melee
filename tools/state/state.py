"""Function state: report.json + annotations layer.

Source of truth:
  build/GALE01/report.json  — per-function fuzzy_match_percent (compiled from src/)
  tools/state/notes.jsonl   — our annotations (status, permuter, blocker, etc.)

Joined on function name. Annotations are append-only events; latest event wins per (function, key).

Status enum (derived, not stored):
  matched          — match_percent == 100.0
  near             — 95.0 <= match_percent < 100.0
  partial          — 0 < match_percent < 95.0
  not_started      — function not yet attempted (no .c body, only stub)
  blocked          — note marks this explicitly (data layout, sibling chain, etc.)
  ready_to_ship    — note marks this; usually implies matched + isolated TU

Operations:
  load_state()                          → list[FunctionState]
  add_note(name, key, value, **meta)    → append to notes.jsonl
  get_state(name)                       → FunctionState | None
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "build" / "GALE01" / "report.json"
NOTES_PATH = ROOT / "tools" / "state" / "notes.jsonl"

# Annotation keys we recognize.  Adding a new key is fine; readers just ignore unknowns.
KEY_STATUS = "status"            # value in {permuter-queued, blocked, ready-to-ship, ignored}
KEY_BLOCKER = "blocker"          # human-readable reason (sibling-WIP, data-layout, etc.)
KEY_LAST_PERCENT = "last_pct"    # last observed match percent (mirror of report)
KEY_REVIEWED = "reviewed"        # when a human signed off

VALID_STATUSES = frozenset({"permuter-queued", "blocked", "ready-to-ship", "ignored"})


@dataclass
class FunctionState:
    name: str
    tu: str                           # unit name, e.g. "melee/gr/grkongo.c"
    match_percent: float | None       # from report.json; None means "not in report"
    size: int | None
    notes: dict[str, Any] = field(default_factory=dict)  # latest value per key

    @property
    def derived_status(self) -> str:
        if "status" in self.notes:
            return self.notes["status"]
        if self.match_percent is None:
            return "not_started"
        if self.match_percent >= 100.0:
            return "matched"
        if self.match_percent >= 95.0:
            return "near"
        return "partial"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tu": self.tu,
            "match_percent": self.match_percent,
            "size": self.size,
            "notes": self.notes,
            "status": self.derived_status,
        }


def _read_notes() -> dict[str, dict[str, Any]]:
    """Replay notes.jsonl; latest event per (function, key) wins."""
    notes: dict[str, dict[str, Any]] = {}
    if not NOTES_PATH.exists():
        return notes
    with NOTES_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = ev.get("name")
            key = ev.get("key")
            if not name or not key:
                continue
            notes.setdefault(name, {})[key] = ev.get("value")
    return notes


def _read_report() -> dict[str, tuple[str, float | None, int | None]]:
    """Returns {function_name: (tu, match_percent, size)}."""
    if not REPORT_PATH.exists():
        return {}
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, float | None, int | None]] = {}
    for unit in data.get("units", []):
        tu = unit.get("name", "")
        for fn in unit.get("functions", []):
            name = fn.get("name")
            if not name:
                continue
            try:
                size = int(fn.get("size", 0))
            except (TypeError, ValueError):
                size = None
            out[name] = (tu, fn.get("fuzzy_match_percent"), size)
    return out


def load_state() -> list[FunctionState]:
    report = _read_report()
    notes = _read_notes()

    seen = set()
    states: list[FunctionState] = []

    for name, (tu, pct, size) in report.items():
        states.append(
            FunctionState(
                name=name,
                tu=tu,
                match_percent=pct,
                size=size,
                notes=notes.get(name, {}),
            )
        )
        seen.add(name)

    # Annotations for functions not in report (e.g. removed but tracked).
    for name, ann in notes.items():
        if name in seen:
            continue
        states.append(
            FunctionState(
                name=name,
                tu=ann.get("tu", "?"),
                match_percent=None,
                size=None,
                notes=ann,
            )
        )

    return states


def get_state(name: str) -> FunctionState | None:
    for s in load_state():
        if s.name == name:
            return s
    return None


def add_note(name: str, key: str, value: Any, **meta: Any) -> None:
    """Append a single annotation event."""
    if key == KEY_STATUS and value not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}; got {value!r}")
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    event: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name,
        "key": key,
        "value": value,
    }
    event.update(meta)
    with NOTES_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def summarize(states: Iterable[FunctionState]) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in states:
        out[s.derived_status] = out.get(s.derived_status, 0) + 1
    return out


if __name__ == "__main__":
    states = load_state()
    summary = summarize(states)
    total = sum(summary.values())
    print(f"{total} functions tracked")
    for status in sorted(summary, key=lambda k: -summary[k]):
        print(f"  {status:>16}: {summary[status]:>5}")
