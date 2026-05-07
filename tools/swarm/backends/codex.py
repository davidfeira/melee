"""Codex CLI backend (stub).

Once the codex CLI's headless prompt + hook surface is settled, this
module should:

1. Spawn `codex --headless --prompt "<full match-attempter prompt + target>"`
   (or whatever the equivalent is in the version you've installed).
2. Capture the agent's final stdout / "result" field.
3. If codex exposes a hook system, register hooks pointing at
   `tools/viz/adapters/codex.py` (write that adapter to translate codex's
   tool-call payloads into our event vocabulary — see EVENTS.md).

Until then, this raises so the orchestrator falls back gracefully.
"""
from __future__ import annotations

from ..backend import Backend, AgentResult


class CodexBackend(Backend):
    name = "codex"

    def run_attempter(self, func: str, prompt: str, timeout_s: int) -> AgentResult:
        raise NotImplementedError(
            "codex backend isn't wired up yet — see tools/swarm/backends/codex.py"
        )
