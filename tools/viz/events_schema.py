"""Canonical event-name constants — mirror of `tools/viz/EVENTS.md`.

Producers (`tools/permute.py`, `tools/state/verify.py`, `tools/viz/emit.py`,
`tools/viz/new_session.py`) and consumers (`tools/viz/serve.py`,
`tools/viz/state.py`, `tools/viz/town.html`) all reference these constants
instead of hard-coding the strings, so renames stay coherent.

EVENTS.md is the human-readable spec; this module is its machine mirror.
If you add a new event here, document it in EVENTS.md too.
"""
from __future__ import annotations

# --- Agent lifecycle ---------------------------------------------------------
DISPATCH = "dispatch"            # parent kicked off a subagent
AGENT_LINK = "agent_link"        # backgrounded subagent now running
AGENT_DONE = "agent_done"        # subagent finished
AGENT_ACTIVITY = "agent_activity"  # subagent invoked a tool
MAMA_ACTIVITY = "mama_activity"  # main-thread tool call

# --- Decomp lifecycle --------------------------------------------------------
MATCH = "match"                  # function reached 100% and was committed
STUCK = "stuck"                  # function log-stuck'd
PERMUTER_START = "permuter_start"
PERMUTER_STATE = "permuter_state"
PERMUTER_STOP = "permuter_stop"

# --- Picker / discovery ------------------------------------------------------
BRIEF = "brief"                  # agent ran permute.py prep / compact-brief
PICKED = "picked"                # lighter-weight discovery event

# --- System / session --------------------------------------------------------
SESSION_START = "session_start"  # written by tools/viz/new_session.py
VERIFY = "verify"                # written by tools/state/verify.py

# Categories used for /sessions stats so a single source decides what counts
# as a "match" vs "near" vs "stuck" vs "queued" outcome.

OUTCOME_BUCKETS = {
    # event_name -> (bucket_key, predicate(event)->bool)
    # Predicate gets the full event dict for events that need extra fields
    # (e.g. match's strict% to distinguish real matches from near-misses).
    MATCH: (
        "matches",
        lambda ev: _strict_at_least(ev, 100.0),
    ),
    "match_near": (  # synthetic: same source event as MATCH, different bucket
        "near",
        lambda ev: not _strict_at_least(ev, 100.0),
    ),
    STUCK: ("stuck", lambda ev: True),
    PERMUTER_START: ("queued", lambda ev: True),
    DISPATCH: ("dispatches", lambda ev: True),
}


def _strict_at_least(ev: dict, threshold: float) -> bool:
    s = ev.get("strict")
    if s in (None, ""):
        return True  # no strict reported -> trust the producer
    try:
        return float(s) >= threshold
    except (TypeError, ValueError):
        return True


def classify(ev: dict) -> str | None:
    """Return the outcome bucket key for an event, or None if it doesn't
    contribute to per-session counts."""
    name = ev.get("event")
    if name == MATCH:
        # Special case: same event, two possible buckets.
        if _strict_at_least(ev, 100.0):
            return "matches"
        return "near"
    rule = OUTCOME_BUCKETS.get(name)
    if rule is None:
        return None
    bucket, predicate = rule
    return bucket if predicate(ev) else None
