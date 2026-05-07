"""Append a JSONL event to events.jsonl.

Library:
    from tools.viz.emit import emit
    emit("permuter", "permuter_start", func="fn_xxx")

CLI:
    python tools/viz/emit.py <actor> <event> [k=v ...]
    python tools/viz/emit.py --from-hook    # parses Claude Code hook JSON on stdin

Failures are silent — viz must never break a real workflow.
"""
import json
import re
import sys
import time
from pathlib import Path

EVENTS = Path(__file__).parent / "events.jsonl"

_FUNC_RX = re.compile(r"\b(fn_[0-9A-Fa-f]{4,}|[A-Za-z_][A-Za-z0-9_]*_8[0-9A-Fa-f]{7})\b")


def emit(actor: str, event: str, **fields) -> None:
    rec = {"t": time.time(), "actor": actor, "event": event}
    for k, v in fields.items():
        if v is not None:
            rec[k] = v
    try:
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def _from_hook() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
    except Exception:
        return
    # Debug capture: every hook payload is appended to hook_payloads.jsonl so we
    # can inspect what Claude Code actually sends. Best-effort, never fatal.
    try:
        dbg = Path(__file__).parent / "hook_payloads.jsonl"
        with open(dbg, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.time(), "raw": payload}) + "\n")
    except Exception:
        pass
    evt = payload.get("hook_event_name", "")
    tool = payload.get("tool_name", "")
    tin = payload.get("tool_input", {}) or {}
    tool_use_id = payload.get("tool_use_id")
    if evt == "PreToolUse" and tool == "Agent":
        sub = tin.get("subagent_type") or "subagent"
        desc = (tin.get("description") or "")[:80]
        prompt = tin.get("prompt") or ""
        m = _FUNC_RX.search(desc) or _FUNC_RX.search(prompt)
        emit("mama", "dispatch", subagent=sub, description=desc,
             func=(m.group(1) if m else None),
             tool_use_id=tool_use_id)
    elif evt == "PostToolUse" and tool == "Agent":
        tr = payload.get("tool_response") or {}
        status = tr.get("status")
        agent_id = tr.get("agentId")
        if status == "async_launched":
            # Background — agent is now running. Record the
            # tool_use_id <-> agent_id bridge so the eventual SubagentStop
            # (which only carries agent_id) can match the right viz agent.
            emit("mama", "agent_link",
                 tool_use_id=tool_use_id, agent_id=agent_id)
        else:
            # Foreground — agent has finished. PostToolUse fires AFTER
            # SubagentStop for foreground, so we retire here (SubagentStop's
            # agent_id won't be in the bridge yet, so it'll no-op).
            emit("mama", "agent_done",
                 tool_use_id=tool_use_id, agent_id=agent_id)
    elif evt == "SubagentStop":
        # Background agents only — for foreground, PostToolUse already
        # retired (SubagentStop fires first but with no bridge entry, the
        # viz no-ops). For background, this is the terminal signal.
        emit("mama", "agent_done",
             agent_id=payload.get("agent_id"),
             last_message=(payload.get("last_assistant_message") or "")[:240])
    elif evt == "PreToolUse":
        # Tool-use trail. Subagent calls have an `agent_id` field; main-thread
        # (mama Claude) calls don't.
        agent_id = payload.get("agent_id")
        summary = _summarize_tool(tool, tin)
        if agent_id:
            emit("mama", "agent_activity",
                 agent_id=agent_id, tool=tool, summary=summary)
        else:
            # Skip the meta-noise: mama's emit calls themselves shouldn't
            # show up in mama's status bubble (they're how the bubble is fed).
            if tool == "Bash" and "tools/viz/emit.py" in (tin.get("command") or ""):
                return
            emit("mama", "mama_activity", tool=tool, summary=summary)


def _summarize_tool(tool: str, tin: dict) -> str:
    """Produce a one-line, non-sensitive summary of the tool call for the viz.
    Truncates aggressively — the bunny's speech bubble is small.
    """
    if tool == "Bash":
        cmd = tin.get("command") or ""
        return _trim(cmd, 80)
    if tool in ("Read", "Edit", "Write"):
        p = tin.get("file_path") or ""
        return f"{tool.lower()} {_trim(_basename(p), 60)}"
    if tool == "Glob":
        return f"glob {_trim(tin.get('pattern') or '', 60)}"
    if tool == "Grep":
        return f"grep {_trim(tin.get('pattern') or '', 60)}"
    return tool


def _basename(path: str) -> str:
    if not path:
        return ""
    p = path.replace("\\", "/")
    return p.rsplit("/", 1)[-1]


def _trim(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _kvs(args):
    out = {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            out[k] = v
    return out


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--from-hook":
        _from_hook()
        return
    if len(sys.argv) < 3:
        sys.exit("usage: emit.py <actor> <event> [k=v ...]  |  --from-hook")
    emit(sys.argv[1], sys.argv[2], **_kvs(sys.argv[3:]))


if __name__ == "__main__":
    main()
