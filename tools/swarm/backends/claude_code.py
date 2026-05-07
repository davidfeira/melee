"""Claude Code backend — uses the `claude` CLI in headless mode.

The hooks in `.claude/settings.local.json` already mirror tool calls and
SubagentStop into `tools/viz/events.jsonl`, so we get rich `agent_activity`
and `agent_done` for free. Our job here is just to spawn the subagent
prompt and wait for it.

Headless invocation:
    claude -p --append-system-prompt "<match-attempter prompt>" \
           --output-format json \
           "<the actual user prompt>"

The CLI returns a JSON object on stdout including the final assistant
message and the agent's session id.
"""
from __future__ import annotations

import json
import subprocess
import time

from ..backend import Backend, AgentResult


SYSTEM_PROMPT_PATH = ".claude/agents/match-attempter.md"


class ClaudeCodeBackend(Backend):
    name = "claude-code"

    def __init__(self, cli: str = "claude"):
        self.cli = cli

    def run_attempter(self, func: str, prompt: str, timeout_s: int) -> AgentResult:
        agent_id = self.new_agent_id()
        t0 = time.time()
        # `-p` = print mode (non-interactive). `--output-format json` returns
        # a JSON envelope so we can pull last_message reliably.
        argv = [
            self.cli, "-p",
            "--output-format", "json",
            "--append-system-prompt", _read_system_prompt(),
            prompt,
        ]
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True,
                timeout=timeout_s, encoding="utf-8", errors="replace",
            )
        except subprocess.TimeoutExpired:
            return AgentResult(agent_id=agent_id, last_message="(timeout)",
                               duration_s=time.time() - t0, ok=False,
                               error="timeout")
        last_msg = ""
        try:
            envelope = json.loads(proc.stdout)
            last_msg = (envelope.get("result") or "")[:240]
        except json.JSONDecodeError:
            last_msg = (proc.stdout or "")[:240]
        return AgentResult(
            agent_id=agent_id,
            last_message=last_msg,
            duration_s=time.time() - t0,
            ok=(proc.returncode == 0),
            error=None if proc.returncode == 0 else (proc.stderr or "")[:240],
        )

    def supports_activity_trace(self) -> bool:
        return True  # via the existing PreToolUse hook


def _read_system_prompt() -> str:
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / SYSTEM_PROMPT_PATH
    return p.read_text(encoding="utf-8") if p.exists() else ""
