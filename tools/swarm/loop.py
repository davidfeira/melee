"""Mama-Claude-as-a-script — runs the swarm orchestration loop against
any registered backend. Lets non-Claude harnesses drive the same workflow
that the visualizer represents.

Usage:
    python -m tools.swarm.loop --backend claude-code --concurrent 3 \
        --mode untouched --limit 10

What it does:
1. Pulls candidates from `permute.py picker`.
2. Spawns up to `--concurrent` subagents in parallel via the chosen
   backend, each running the match-attempter prompt against one func.
3. Emits `dispatch` / `agent_link` / `agent_done` events to the viz
   around each backend invocation.
4. Loops until `--limit` funcs have been processed (or Ctrl-C).

The decomp-side events (`match`, `stuck`, `permuter_*`) come from the
agents calling `permute.py` themselves — orchestrator doesn't need to
emit those. Same for `agent_activity` (driven by the harness's hooks).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from viz.emit import emit  # type: ignore  # noqa: E402

from .backend import Backend  # noqa: E402


def _picker(mode: str, limit: int) -> list[str]:
    """Shell out to permute.py picker and return func names."""
    out = subprocess.run(
        ["python", "tools/permute.py", "picker", "--mode", mode, "--limit", str(limit)],
        capture_output=True, text=True, cwd=ROOT,
        encoding="utf-8", errors="replace",
    ).stdout
    funcs: list[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("instructions"):
            continue
        # picker rows: "<insns>  <pct>%  <name>  (<tu>)"
        parts = line.split()
        if len(parts) >= 3:
            funcs.append(parts[2])
    return funcs


def _attempter_prompt(func: str) -> str:
    """The same prompt template Mama Claude uses when dispatching an
    Agent tool call. Single source of truth — keep in sync with the
    instructions in `.claude/agents/match-attempter.md`."""
    return (
        f"Target function: `{func}`. Untouched.\n\n"
        "1. `python tools/permute.py prep " + func + " -q --m2c --similar 3 --examples 2`\n"
        "2. Write the C decomp at the right insertion point in the appropriate src/ file.\n"
        "3. `python tools/permute.py diff " + func + "`.\n"
        "4. Standard 2-attempt cap → commit-match / hand off / log-stuck.\n"
    )


def _run_one(backend: Backend, func: str, timeout_s: int) -> None:
    tool_use_id = backend.new_agent_id()  # used as our dispatch key
    emit("mama", "dispatch", subagent="match-attempter",
         func=func, description=f"Attempt {func}",
         tool_use_id=tool_use_id)
    result = backend.run_attempter(func, _attempter_prompt(func), timeout_s)
    emit("mama", "agent_link",
         tool_use_id=tool_use_id, agent_id=result.agent_id)
    emit("mama", "agent_done",
         agent_id=result.agent_id, last_message=result.last_message)
    if not result.ok:
        emit("mama", "agent_error",
             agent_id=result.agent_id, error=result.error or "")


def _load_backend(name: str) -> Backend:
    if name == "claude-code":
        from .backends.claude_code import ClaudeCodeBackend
        return ClaudeCodeBackend()
    if name == "codex":
        from .backends.codex import CodexBackend
        return CodexBackend()
    if name == "opencode":
        from .backends.opencode import OpencodeBackend
        return OpencodeBackend()
    raise SystemExit(f"unknown backend: {name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="claude-code",
                    choices=["claude-code", "codex", "opencode"])
    ap.add_argument("--mode", default="untouched",
                    choices=["untouched", "in_progress", "all"])
    ap.add_argument("--concurrent", type=int, default=3,
                    help="max parallel subagents (default 3)")
    ap.add_argument("--limit", type=int, default=10,
                    help="how many funcs to process before exiting")
    ap.add_argument("--timeout-min", type=int, default=30,
                    help="per-subagent wall-clock cap")
    args = ap.parse_args()

    backend = _load_backend(args.backend)
    funcs = _picker(args.mode, args.limit)
    if not funcs:
        print(f"no candidates for mode={args.mode}", file=sys.stderr)
        return
    print(f"[swarm] backend={backend.name} concurrent={args.concurrent} "
          f"funcs={len(funcs)}", file=sys.stderr)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as pool:
        futures = [pool.submit(_run_one, backend, f, args.timeout_min * 60)
                   for f in funcs]
        for fut in concurrent.futures.as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                print(f"[swarm] subagent crashed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
