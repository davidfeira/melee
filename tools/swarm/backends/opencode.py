"""opencode CLI backend (stub).

opencode (https://github.com/sst/opencode) supports headless one-shot mode.
TODO once the project's installed:

1. Spawn `opencode run "<prompt>"` (verify exact flag).
2. Capture the assistant's final response.
3. Wire opencode's hook/event system (if any) into
   tools/viz/adapters/opencode.py so tool calls flow into the event log.

Falls through to NotImplementedError until then.
"""
from __future__ import annotations

from ..backend import Backend, AgentResult


class OpencodeBackend(Backend):
    name = "opencode"

    def run_attempter(self, func: str, prompt: str, timeout_s: int) -> AgentResult:
        raise NotImplementedError(
            "opencode backend isn't wired up yet — see tools/swarm/backends/opencode.py"
        )
