"""Upstream-state check for a function: are we about to redo work?

Before starting a function attempt, ask `upstream-check` whether
github.com/doldecomp/melee already has it matched (or stubbed). If matched,
abort — it's pure waste. If still INCLUDE_ASM or `/// #funcname` placeholder,
proceed.

Hooked into `permute.py prep` automatically; pass `--skip-upstream-check` to
bypass (e.g., when intentionally re-working an upstream match for a sibling).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional


_THIS_DIR = Path(__file__).resolve().parent
_ROOT = _THIS_DIR.parent
_FETCH_TIMESTAMP = _ROOT / "build-linux" / ".upstream-fetch-timestamp"
_FETCH_STALE_SEC = 24 * 3600  # 24h


def _run_git(args: list[str]) -> str:
    r = subprocess.run(
        ["git", *args], capture_output=True, check=False, cwd=_ROOT,
    )
    return r.stdout.decode("utf-8", errors="replace")


def _upstream_remote() -> Optional[str]:
    """Return the name of the doldecomp upstream remote, or None if missing."""
    out = _run_git(["remote", "-v"])
    for line in out.splitlines():
        if "doldecomp/melee" in line:
            return line.split()[0]
    return None


def _is_fetch_stale() -> bool:
    if not _FETCH_TIMESTAMP.exists():
        return True
    return time.time() - _FETCH_TIMESTAMP.stat().st_mtime > _FETCH_STALE_SEC


def _stamp_fetch() -> None:
    _FETCH_TIMESTAMP.parent.mkdir(parents=True, exist_ok=True)
    _FETCH_TIMESTAMP.touch()


def fetch_upstream(quiet: bool = False) -> bool:
    """Fetch upstream/master. Return True if fetch succeeded."""
    remote = _upstream_remote()
    if remote is None:
        if not quiet:
            print("[upstream-check] no upstream remote configured (looked for doldecomp/melee)", file=sys.stderr)
        return False
    r = subprocess.run(
        ["git", "fetch", remote, "master"],
        capture_output=True, check=False, cwd=_ROOT,
    )
    if r.returncode != 0:
        if not quiet:
            err = r.stderr.decode("utf-8", errors="replace")
            print(f"[upstream-check] fetch failed: {err}", file=sys.stderr)
        return False
    _stamp_fetch()
    return True


def check_upstream(func: str, c_file: Optional[Path] = None,
                   *, find_c_file: Optional[Callable] = None) -> dict:
    """Look up `func` against upstream/master.

    Returns {'state': str, 'detail': str, 'path': str or None} where state is:
      - 'matched'           — upstream has a real definition AND our local file is still
                              an INCLUDE_ASM/placeholder stub (we'd be retyping their work)
      - 'matched-divergent' — upstream has a real def AND we also have a real def, but
                              they differ (regression after upstream edit; safe to attempt)
      - 'unmatched'         — upstream has INCLUDE_ASM or /// # placeholder (safe to attempt)
      - 'unknown-tu'        — upstream doesn't have the .c file at all (likely safe; new TU)
      - 'unknown-func'      — file exists upstream but no trace of the function name
      - 'no-upstream'       — no doldecomp upstream remote configured
    """
    remote = _upstream_remote()
    if remote is None:
        return {"state": "no-upstream", "detail": "no doldecomp/melee remote configured", "path": None}

    if c_file is None:
        if find_c_file is None:
            return {"state": "unknown-func", "detail": "c_file not provided and no resolver", "path": None}
        try:
            c_file = find_c_file(func)
        except SystemExit:
            return {"state": "unknown-tu", "detail": "could not resolve function to a .c file locally", "path": None}

    rel_path = c_file.relative_to(_ROOT).as_posix() if c_file.is_absolute() else str(c_file)

    upstream_content = _run_git(["show", f"{remote}/master:{rel_path}"])
    if not upstream_content:
        return {"state": "unknown-tu", "detail": f"{rel_path} not in upstream/master", "path": rel_path}

    # 1) INCLUDE_ASM(..., func) — definitively not matched upstream
    if re.search(r"INCLUDE_ASM\([^)]*,\s*" + re.escape(func) + r"\s*\)", upstream_content):
        return {"state": "unmatched", "detail": "INCLUDE_ASM upstream", "path": rel_path}

    # 2) /// #func placeholder — doldecomp's "still pending" comment
    if re.search(r"^\s*///\s*#\s*" + re.escape(func) + r"\s*$",
                 upstream_content, re.MULTILINE):
        return {"state": "unmatched", "detail": "/// # placeholder upstream", "path": rel_path}

    # 3) Real definition signature
    def_pat = re.compile(
        r"^\s*(?:static\s+|inline\s+|extern\s+)*"
        r"[A-Za-z_][A-Za-z0-9_*\s]*\s\*?\s*"
        + re.escape(func) + r"\s*\(",
        re.MULTILINE,
    )
    if def_pat.search(upstream_content):
        # Upstream has a real definition. Check if we still have a stub locally
        # (real duplicate-of-upstream-work) or also have a real def that diverged
        # (regression case — safe to attempt, the source needs nudging back).
        local_path = c_file if c_file.is_absolute() else (_ROOT / c_file)
        try:
            local_content = local_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            local_content = ""
        local_stub = (
            re.search(r"INCLUDE_ASM\([^)]*,\s*" + re.escape(func) + r"\s*\)", local_content)
            or re.search(r"^\s*///\s*#\s*" + re.escape(func) + r"\s*$",
                         local_content, re.MULTILINE)
        )
        if local_stub:
            return {"state": "matched", "detail": "definition exists upstream",
                    "path": rel_path}
        if def_pat.search(local_content):
            return {"state": "matched-divergent",
                    "detail": "upstream matched; local def diverged (regression)",
                    "path": rel_path}
        return {"state": "matched", "detail": "definition exists upstream", "path": rel_path}

    # 4) Name appears but not as definition — likely just a call/extern
    if re.search(r"\b" + re.escape(func) + r"\b", upstream_content):
        return {"state": "unknown-func", "detail": "referenced but no definition signature found", "path": rel_path}

    return {"state": "unknown-func", "detail": "name not found in upstream file", "path": rel_path}


def format_result(func: str, result: dict) -> str:
    """Format a check_upstream result for human display."""
    state = result["state"]
    detail = result["detail"]
    path = result.get("path") or "(unknown)"
    icons = {
        "matched": "STOP",
        "matched-divergent": "OK",
        "unmatched": "OK",
        "unknown-tu": "ok",
        "unknown-func": "?",
        "no-upstream": "?",
    }
    icon = icons.get(state, "?")
    return f"[upstream-check] {icon}  {func}  state={state}  ({detail})  path={path}"


def cmd_upstream_check(args: argparse.Namespace) -> None:
    """`upstream-check <func>` subcommand."""
    if args.fetch or (args.fetch_if_stale and _is_fetch_stale()):
        ok = fetch_upstream()
        if not ok and args.fetch:
            sys.exit(1)

    deps = getattr(cmd_upstream_check, "_deps", {})
    find_c_file = deps.get("find_c_file")
    result = check_upstream(args.func, find_c_file=find_c_file)
    print(format_result(args.func, result))

    if result["state"] == "matched":
        sys.exit(2)  # exit code 2: matched upstream (waste-of-time signal)
    if result["state"] in ("unmatched", "unknown-tu", "matched-divergent"):
        sys.exit(0)
    sys.exit(1)  # unknown — caller should investigate


def _set_deps(*, find_c_file: Callable) -> None:
    cmd_upstream_check._deps = {"find_c_file": find_c_file}


def add_subcommands(sub: "argparse._SubParsersAction") -> None:
    pu = sub.add_parser(
        "upstream-check",
        help="check whether a function is already matched/stubbed in upstream/master",
        description=(
            "Pre-flight: ask doldecomp/melee whether this function is already done.\n"
            "Exit codes: 0=safe to attempt, 1=unknown, 2=already matched upstream."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    pu.add_argument("func")
    pu.add_argument("--fetch", action="store_true",
                    help="fetch upstream/master before checking (slow but fresh)")
    pu.add_argument("--fetch-if-stale", action="store_true", dest="fetch_if_stale",
                    help="fetch only if last fetch was >24h ago")
    pu.set_defaults(handler=cmd_upstream_check)
