"""Harness-agnostic backend interface for the swarm orchestrator.

A backend turns "run a one-shot subagent against this prompt" into a
process invocation against whatever AI harness the user has installed
(Claude Code, opencode, codex, etc.). The orchestrator (`tools.swarm.loop`)
spawns these in a thread pool and emits viz events around them.

Each backend produces:
- An `agent_id` that's stable for the duration of the run, so the viz can
  attribute `agent_activity` to the right sprite.
- A final result with the agent's last message + a coarse status (matched,
  stuck, error, etc.).

Activity tracing (the speech-bubbles) requires the harness to emit hook-
style events. If the harness doesn't, the orchestrator just won't emit
`agent_activity` for that backend's runs.
"""
from __future__ import annotations

import abc
import dataclasses
import uuid
from typing import Optional


@dataclasses.dataclass
class AgentResult:
    """Summary of a finished subagent run.

    `last_message` is what the orchestrator surfaces in the log feed and
    `outcome` is a coarse classification used for backoff / retry logic.
    The actual decomp lifecycle (match/stuck/queued) is determined by
    `permute.py` events, not by the harness's wrap-up text.
    """
    agent_id: str
    last_message: str
    duration_s: float
    ok: bool
    error: Optional[str] = None


class Backend(abc.ABC):
    """Implement this for each AI harness."""

    name: str = "abstract"

    def new_agent_id(self) -> str:
        """Generate a stable id for one subagent invocation. Used as the
        attribution key for `agent_activity` events emitted via hooks.
        Most harnesses give us their own id; for those, override and return
        it from the launch call. The default is a UUID."""
        return "a" + uuid.uuid4().hex[:16]

    @abc.abstractmethod
    def run_attempter(self, func: str, prompt: str, timeout_s: int) -> AgentResult:
        """Run a one-shot subagent against `prompt`. Blocks until the
        subagent terminates or `timeout_s` elapses.

        Implementations should:
        1. Generate an agent_id (or use the harness's native id) and emit
           `dispatch` + `agent_link` events for it.
        2. Spawn the harness CLI/SDK with the prompt, working directory at
           the repo root, and hooks configured (if the harness supports
           them) to mirror tool calls into the viz event stream.
        3. Wait for completion, capture last assistant message.
        4. Emit `agent_done` and return.
        """

    def supports_activity_trace(self) -> bool:
        """True if this backend's harness can emit `agent_activity` for
        nested tool calls. Drives whether the orchestrator advertises
        speech-bubble support to the viz."""
        return False
