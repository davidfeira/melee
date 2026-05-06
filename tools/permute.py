#!/usr/bin/env python3
"""Per-function asm + permuter helper for the interactive decomp loop.

This is separate from tools/decomp.py (which runs m2c via the project's
--non-matching asm/obj split). This tool works against the regular matched
build: dtk-disasm a built .o, extract one function's asm, and (optionally)
import it into decomp-permuter.

Subcommands:
  prep <func>     Build the matched .o (WSL ninja), disassemble it, and
                  extract just <func>'s asm. Prints the asm to stdout.
  check           Run ninja and report SHA1 status.
  permute <func>  Set up nonmatchings/<func>/, fix the compile.sh quirk,
                  and print the permuter run command. Requires `prep` first
                  (or runs it implicitly).

Runs from Windows. Shells into WSL Ubuntu for the build and permuter
toolchain (see memory/project_permuter_setup.md for the topology).
"""
from __future__ import annotations

import argparse
import contextlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Ensure unicode output works on Windows console (em-dashes, arrows, etc.)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
BUILD_LINUX = ROOT / "build-linux"
DTK = ROOT / "build" / "tools" / "dtk.exe"
EXTRACTOR = ROOT / "tools" / "extract_asm_for_permuter.py"

WSL_ROOT = "/mnt/c/Users/david/projects/melee"
WSL_DISTRO = "Ubuntu"


def wsl(cmd: str, *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["wsl", "-d", WSL_DISTRO, "--", "bash", "-lc", f"cd {WSL_ROOT} && {cmd}"],
        capture_output=capture,
        text=True,
        check=False,
    )


# Concurrent ninja invocations from many subagents thrash WSL/wibo. Cap with
# a file-based semaphore so all permute.py callers serialize through N slots.
# Override via env: PERMUTE_NINJA_SLOTS (default 3).
NINJA_SLOTS = int(os.environ.get("PERMUTE_NINJA_SLOTS", "3"))
_NINJA_LOCK_DIR = ROOT / "build-linux" / ".ninja-locks"
_NINJA_LOCK_STALE_SEC = 1800  # 30 min: locks older than this are stale


_SWARM_EVENT_LOG = ROOT / "build-linux" / "swarm-events.jsonl"


def _log_event(event_type: str, **fields) -> None:
    """Append a JSONL event to the swarm event log. Best-effort — never raises.

    Used by compact-brief / commit-match / log-stuck to record dispatch outcomes
    so `permute.py events` can aggregate run-time + outcome statistics over time.
    """
    import json as _json
    import time as _time
    try:
        _SWARM_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": _time.time(), "event": event_type}
        rec.update(fields)
        with _SWARM_EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(_json.dumps(rec) + "\n")
    except OSError:
        pass


def _is_pid_alive(pid: int) -> bool:
    """Cheap cross-platform liveness check for a numeric pid."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        # tasklist is reliable but slow (~200ms); use signal 0 fallback first
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


@contextlib.contextmanager
def _ninja_slot():
    """Wait for a free ninja slot before yielding. Caps concurrent ninja
    runs across all permute.py processes at NINJA_SLOTS. Polls every 2s.

    Stale locks are reclaimed when (a) the recorded pid is dead, or (b)
    the file is older than _NINJA_LOCK_STALE_SEC (fallback for races).
    Without pid-liveness, a crashed subagent could block a slot for up to
    30 min.
    """
    import time
    _NINJA_LOCK_DIR.mkdir(parents=True, exist_ok=True)
    pid = os.getpid()
    waited = 0.0
    while True:
        # Reap stale locks: prefer pid-liveness; fall back to mtime.
        now = time.time()
        for lock in _NINJA_LOCK_DIR.glob("slot-*.pid"):
            try:
                content = lock.read_text(encoding="utf-8", errors="replace").strip()
                holder_pid = int(content) if content.isdigit() else 0
                stale_by_age = now - lock.stat().st_mtime > _NINJA_LOCK_STALE_SEC
                stale_by_pid = holder_pid > 0 and not _is_pid_alive(holder_pid)
                if stale_by_age or stale_by_pid:
                    lock.unlink(missing_ok=True)
            except (OSError, ValueError):
                # Best-effort: try mtime-only on read errors
                try:
                    if now - lock.stat().st_mtime > _NINJA_LOCK_STALE_SEC:
                        lock.unlink(missing_ok=True)
                except OSError:
                    pass
        # Try to claim a slot via exclusive-create
        for i in range(NINJA_SLOTS):
            lock_path = _NINJA_LOCK_DIR / f"slot-{i}.pid"
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, f"{pid}\n".encode())
                finally:
                    os.close(fd)
                if waited > 0:
                    print(f"[ninja-slot] acquired slot {i} after {waited:.0f}s wait")
                try:
                    yield i
                finally:
                    try:
                        lock_path.unlink()
                    except OSError:
                        pass
                return
            except FileExistsError:
                continue
        # All slots busy — wait. After 60s log a heads-up so user knows why.
        if waited == 0:
            print(f"[ninja-slot] all {NINJA_SLOTS} slots busy, waiting…")
        time.sleep(2)
        waited += 2


def wsl_ninja(target_args: str = "", *, capture: bool = False) -> subprocess.CompletedProcess:
    """Run `ninja <target_args>` in WSL, gated by the ninja-slot semaphore.

    Use this in place of `wsl(f"ninja ...")` so concurrent callers serialize
    through the slot pool instead of thrashing wibo/mwcc.
    """
    with _ninja_slot():
        return wsl(f"ninja {target_args}".rstrip(), capture=capture)


_SYMBOL_CACHE_PATH = ROOT / "build-linux" / "permute_symbol_cache.json"


def _build_symbol_cache(obj_root: Path) -> dict[str, str]:
    """Walk obj_root, return a dict mapping function name -> .c file repo-rel path."""
    from elftools.elf.elffile import ELFFile
    from elftools.elf.sections import SymbolTableSection

    cache: dict[str, str] = {}
    for o_path in obj_root.rglob("*.o"):
        try:
            with open(o_path, "rb") as f:
                elf = ELFFile(f)
                sym = elf.get_section_by_name(".symtab")
                if not isinstance(sym, SymbolTableSection):
                    continue
                rel_o = o_path.relative_to(obj_root)
                c_rel = (Path("src") / rel_o.with_suffix(".c")).as_posix()
                if not (ROOT / c_rel).exists():
                    continue
                for s in sym.iter_symbols():
                    if s["st_info"]["type"] == "STT_FUNC" and s.name:
                        cache.setdefault(s.name, c_rel)
        except Exception:
            continue
    return cache


def _load_or_build_symbol_cache() -> dict[str, str]:
    """Cache obj/ symbol→.c mapping in build-linux/permute_symbol_cache.json.

    Invalidated when any obj/ .o is newer than the cache file. Saves ~500ms
    per `prep` invocation since we don't have to walk ~1000 .o files each time.
    """
    import json

    obj_roots = [
        BUILD_LINUX / "GALE01" / "obj",
        ROOT / "build" / "GALE01" / "obj",
    ]
    obj_root = next((r for r in obj_roots if r.is_dir()), None)
    if obj_root is None:
        return {}

    # Trust the cache once it exists. Walking ~1000 .o files to check
    # staleness costs ~500ms — more than the cache saves. Delete the cache
    # file manually after a major build to force a rebuild.
    if _SYMBOL_CACHE_PATH.exists():
        try:
            return json.loads(_SYMBOL_CACHE_PATH.read_text())
        except Exception:
            pass

    cache = _build_symbol_cache(obj_root)
    _SYMBOL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SYMBOL_CACHE_PATH.write_text(json.dumps(cache))
    return cache


def _find_c_file_by_symbol(func: str) -> Path | None:
    try:
        cache = _load_or_build_symbol_cache()
    except ImportError:
        return None
    rel_path = cache.get(func)
    return ROOT / rel_path if rel_path else None


def _find_c_file_by_text(func: str) -> Path | None:
    """Fallback: scan .c files for a definition or placeholder mentioning `func`."""
    def_pattern = re.compile(rf"^\s*\S[^;/]*\b{re.escape(func)}\s*\(")
    placeholder_rx = re.compile(rf"^/// #(?:\w+\s+)?{re.escape(func)}\s*$")
    matches: set[Path] = set()
    for c in SRC.rglob("*.c"):
        try:
            text = c.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if placeholder_rx.match(stripped):
                matches.add(c)
                break
            if not stripped or stripped.startswith(("//", "*", "/*", "#")):
                continue
            if def_pattern.match(line) and not line.rstrip().endswith(";"):
                matches.add(c)
                break
    matches_sorted = sorted(matches)
    return matches_sorted[0] if len(matches_sorted) == 1 else None


def find_c_file(func: str) -> Path:
    # Prefer symbol-table lookup: works for both decompiled & undecompiled
    by_sym = _find_c_file_by_symbol(func)
    if by_sym is not None:
        return by_sym
    by_text = _find_c_file_by_text(func)
    if by_text is not None:
        return by_text
    sys.exit(f"no .c file owns {func!r} (checked obj/ symbol tables and src/ text)")


def rel(p: Path) -> Path:
    return p.resolve().relative_to(ROOT)


def ensure_o(c_file: Path) -> Path:
    """Build the matched .o on the WSL side and return its repo-relative path."""
    rel_o = Path("build-linux") / "GALE01" / rel(c_file).with_suffix(".o")
    print(f"  [build] {rel_o.as_posix()}", flush=True)
    rc = wsl_ninja(rel_o.as_posix()).returncode
    if rc != 0:
        sys.exit(f"ninja failed (exit {rc})")
    if not (ROOT / rel_o).exists():
        sys.exit(f"build claimed success but {rel_o} missing")
    return rel_o


def _presplit_asm(c_file: Path) -> Path | None:
    """Return the pre-split asm for c_file's translation unit, if it exists.

    The project's dtk split produces these at build/GALE01/asm/<rel>.s and
    build-linux/GALE01/asm/<rel>.s. They have all functions in the TU,
    including ones that are still INCLUDE_ASM (undecompiled).
    """
    rel_s = rel(c_file).relative_to("src").with_suffix(".s")
    for base in (BUILD_LINUX / "GALE01" / "asm", ROOT / "build" / "GALE01" / "asm"):
        candidate = base / rel_s
        if candidate.exists():
            return candidate
    return None


def disasm_and_extract(c_file: Path, func: str) -> tuple[Path, str]:
    """Returns (asm_path, asm_text).

    Strategy:
    1. If the pre-split asm exists for this TU and contains `func`, extract
       from it. This handles both undecompiled functions (only place they
       live) and decompiled ones (still listed there if asm wasn't deleted).
    2. Otherwise, build the matched .o on the WSL side and dtk-disasm it.
       This is the fallback for fully-decompiled functions whose asm was
       removed from the pre-split file.
    """
    BUILD_LINUX.mkdir(exist_ok=True)
    asm_out = BUILD_LINUX / f"{func}.s"

    presplit = _presplit_asm(c_file)
    if presplit is not None:
        # Quick check whether `func` is present (asm files may contain SJIS bytes)
        text = presplit.read_text(encoding="utf-8", errors="replace")
        if re.search(rf"^\.fn\s+{re.escape(func)},", text, re.MULTILINE):
            print(f"  [extract] from {rel(presplit).as_posix()}")
            proc = subprocess.run(
                [sys.executable, str(EXTRACTOR), str(presplit), func],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                asm_out.write_text(proc.stdout)
                return asm_out, proc.stdout
            # Fall through to disasm path on extractor failure

    # Disasm path: build .o, then disasm
    rel_o = Path("build-linux") / "GALE01" / rel(c_file).with_suffix(".o")
    if not (ROOT / rel_o).exists():
        rel_o = ensure_o(c_file)
    disasm_path = BUILD_LINUX / f"{rel_o.stem}.disasm.s"
    print(f"  [disasm] {rel(disasm_path).as_posix()}")
    rc = subprocess.run(
        [str(DTK), "elf", "disasm", str(rel_o), str(disasm_path)],
        cwd=ROOT,
    ).returncode
    if rc != 0:
        sys.exit(f"dtk failed (exit {rc})")

    proc = subprocess.run(
        [sys.executable, str(EXTRACTOR), str(disasm_path), func],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"extractor failed: {proc.stderr.strip()}")

    asm_out.write_text(proc.stdout)
    print(f"  [extract] from {rel(disasm_path).as_posix()}")
    return asm_out, proc.stdout


_BL_RX = re.compile(r"\bbl\s+([A-Za-z_][A-Za-z0-9_]*)")
_REF_RX = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)@(?:ha|h|l)\b")


def collect_referenced_symbols(asm_text: str) -> list[str]:
    """Return external symbols referenced by branch+link or @ha/@l relocations."""
    syms: set[str] = set()
    for line in asm_text.splitlines():
        # Strip the `/* ... */` byte-comment prefix dtk emits
        body = re.sub(r"^/\*[^*]*\*/", "", line).strip()
        for rx in (_BL_RX, _REF_RX):
            for m in rx.finditer(body):
                syms.add(m.group(1))
    return sorted(syms)


_DECL_INDEX_PATH = ROOT / "build-linux" / "permute_decl_index.json"
# Match a typical C declaration: identifier name followed by `(` or terminating `;`.
# Captures the leading identifier-like token so we key the index by it.
_DECL_TOKEN_RX = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")


_LEADING_COMMENT_RX = re.compile(r"^\s*(?:/\*[^*]*\*/\s*)*")


def _looks_like_declaration(line: str, symbol: str) -> bool:
    """Heuristic: does `line` declare `symbol` (vs use it in a call/expression)?

    Strips leading whitespace and `/* ... */` doc comments; the remainder of a
    declaration starts with a return type / storage class, not the symbol
    itself. So if the first identifier-like token after stripping IS the
    symbol, we treat it as a call site and reject it.
    """
    rest = _LEADING_COMMENT_RX.sub("", line)
    m = _DECL_TOKEN_RX.search(rest)
    if m is None:
        return False
    return m.group(1) != symbol


def _build_decl_index() -> dict[str, str]:
    """Index every function/global declaration in src/ + extern/ by symbol."""
    found: dict[str, str] = {}
    search_roots = [SRC, ROOT / "extern" / "dolphin" / "include"]
    for ext in (".h", ".c"):
        for root_dir in search_roots:
            if not root_dir.is_dir():
                continue
            for path in root_dir.rglob(f"*{ext}"):
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for ln, line in enumerate(text.splitlines(), 1):
                    if not ("(" in line or "extern" in line or line.rstrip().endswith(";")):
                        continue
                    for tok in _DECL_TOKEN_RX.findall(line):
                        if tok in found:
                            continue
                        if not re.search(rf"\b{re.escape(tok)}\s*(\(|\[|;)", line):
                            continue
                        if not _looks_like_declaration(line, tok):
                            continue
                        label = f"{path.relative_to(ROOT).as_posix()}:{ln}"
                        found[tok] = f"{label}  {line.strip()}"
    return found


def _load_or_build_decl_index() -> dict[str, str]:
    import json
    if _DECL_INDEX_PATH.exists():
        try:
            return json.loads(_DECL_INDEX_PATH.read_text())
        except Exception:
            pass
    idx = _build_decl_index()
    _DECL_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DECL_INDEX_PATH.write_text(json.dumps(idx))
    return idx


def grep_symbols(symbols: list[str]) -> dict[str, str]:
    """Look up each symbol's declaration line via the cached index."""
    if not symbols:
        return {}
    idx = _load_or_build_decl_index()
    return {sym: idx[sym] for sym in symbols if sym in idx}


def run_m2c(func: str) -> str | None:
    """Run the project's tools/decomp.py to get an m2c starting decompilation.

    Returns the m2c output, or None if it couldn't run (e.g. asm split missing).
    Skips ctx regeneration if a fresh-enough build/ctx.c already exists, which
    saves ~5s per call.
    """
    decomp = ROOT / "tools" / "decomp.py"
    if not decomp.exists():
        return None
    args = [sys.executable, str(decomp)]
    # ctx.c is invalidated when any header changes; reuse if it's newer than
    # all .h files we'd preprocess. decomp.py uses argparse REMAINDER, so
    # --no-context must come BEFORE the positional function name.
    ctx_c = ROOT / "build" / "ctx.c"
    if ctx_c.exists():
        ctx_mtime = ctx_c.stat().st_mtime
        try:
            stale = any(
                h.stat().st_mtime > ctx_mtime for h in SRC.rglob("*.h")
            )
        except OSError:
            stale = True
        if not stale:
            args.append("--no-context")
    args.append(func)
    proc = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def find_similar_via_embeddings(asm_path: Path, n: int, exclude: str | None = None) -> list[str]:
    """Use the embeddings index to find top-N most similar matched functions.

    Returns a list of function names ordered by similarity. Falls back to
    empty list if the index doesn't exist or the embeddings venv is missing.
    """
    index_path = BUILD_LINUX / "embeddings.npz"
    venv_dir = ROOT / ".venv-embeddings"
    embed_script = ROOT / "tools" / "embed_index.py"
    if not index_path.exists():
        return []
    # The venv was created from inside WSL; its binaries are Linux ELFs that
    # Windows file APIs can refuse to stat. So only check that the dir exists.
    if not venv_dir.is_dir():
        return []

    asm_wsl = WSL_ROOT + "/" + rel(asm_path).as_posix()
    # Ask for n+1 in case the top hit is the function itself
    proc = subprocess.run(
        [
            "wsl", "-d", WSL_DISTRO, "--", "bash", "-c",
            f".venv-embeddings/bin/python tools/embed_index.py query {asm_wsl} --top {n + 1}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    names: list[str] = []
    for line in proc.stdout.splitlines():
        parts = line.strip().split("\t")
        if len(parts) == 2 and parts[1] != exclude:
            names.append(parts[1])
    return names[:n]


def _extract_function_pair(name: str) -> tuple[str, str] | None:
    """Find a matched function by name and return (asm, c_body) or None."""
    c_file = _find_c_file_by_symbol(name)
    if c_file is None:
        return None
    presplit = _presplit_asm(c_file)
    if presplit is None:
        return None
    asm_text = presplit.read_text(encoding="utf-8", errors="replace")
    asm_match = re.search(
        rf"^\.fn\s+{re.escape(name)},\s*\w+\s*\n(.*?)^\.endfn\s+{re.escape(name)}",
        asm_text,
        re.DOTALL | re.MULTILINE,
    )
    if not asm_match:
        return None
    asm_body = asm_match.group(1).strip()
    asm_lines = asm_body.splitlines()
    if len(asm_lines) > 30:
        asm_lines = asm_lines[:30] + [f"  (... {len(asm_lines) - 30} more lines)"]
    asm_short = "\n".join(asm_lines)

    c_text = c_file.read_text(encoding="utf-8", errors="replace")
    fn_def_rx = re.compile(
        rf"^[a-zA-Z_][\w\s\*]*?\b{re.escape(name)}\s*\([^;)]*\)\s*\n?\s*\{{",
        re.MULTILINE,
    )
    m = fn_def_rx.search(c_text)
    if not m:
        return (asm_short, "(C definition not found)")
    body_start = c_text.find("{", m.end() - 1)
    if body_start < 0:
        return (asm_short, "(C definition unparseable)")
    depth = 0
    for i in range(body_start, len(c_text)):
        if c_text[i] == "{":
            depth += 1
        elif c_text[i] == "}":
            depth -= 1
            if depth == 0:
                return (asm_short, c_text[m.start():i + 1])
    return (asm_short, "(C definition unterminated)")


def find_examples(c_file: Path, target_func: str, n: int = 3) -> list[tuple[str, str]]:
    """Find up to `n` already-decompiled function pairs (asm, C) from the same TU.

    Strategy: parse the .c file for function definitions, parse the corresponding
    pre-split asm for matching `.fn` blocks. Skip the target function. Return
    pairs in source order.
    """
    pairs: list[tuple[str, str]] = []
    try:
        c_text = c_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return pairs

    presplit = _presplit_asm(c_file)
    if presplit is None:
        return pairs
    asm_text = presplit.read_text(encoding="utf-8", errors="replace")

    fn_def_rx = re.compile(
        r"^[a-zA-Z_][\w\s\*]*?\b([a-zA-Z_]\w*)\s*\([^;)]*\)\s*\n?\s*\{",
        re.MULTILINE,
    )
    asm_rx_template = r"^\.fn\s+{name},\s*\w+\s*\n(.*?)^\.endfn\s+{name}"

    for m in fn_def_rx.finditer(c_text):
        name = m.group(1)
        if name == target_func or name in {p[0].split("\n", 1)[0] for p in pairs}:
            continue
        # Pull the C body
        start = m.start()
        depth = 0
        body_start = c_text.find("{", m.end() - 1)
        if body_start < 0:
            continue
        i = body_start
        while i < len(c_text):
            ch = c_text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    body_end = i + 1
                    break
            i += 1
        else:
            continue
        c_body = c_text[start:body_end]

        # Pull the asm
        asm_match = re.search(
            asm_rx_template.format(name=re.escape(name)),
            asm_text,
            re.DOTALL | re.MULTILINE,
        )
        if not asm_match:
            continue
        asm_body = asm_match.group(1).strip()
        # Trim asm to instructions only (drop the byte-comment prefix is fine,
        # but truncate to ~50 lines to keep examples compact)
        asm_lines = asm_body.splitlines()
        if len(asm_lines) > 30:
            asm_lines = asm_lines[:30] + [f"  (... {len(asm_lines) - 30} more lines)"]
        asm_short = "\n".join(asm_lines)

        pairs.append((name, f"; asm\n{asm_short}\n\n; c\n{c_body}"))
        if len(pairs) >= n:
            break
    return pairs


def cmd_prep(args: argparse.Namespace) -> None:
    func = args.func
    c_file = find_c_file(func)
    print(f"function: {func}")
    print(f"source:   {rel(c_file).as_posix()}")

    # Pre-flight: is this function already matched upstream? If so, refuse —
    # we'd be redoing work. Pass --skip-upstream-check to bypass.
    if not getattr(args, "skip_upstream_check", False):
        # Auto-fetch upstream if our data is >24h stale, so the check is reliable.
        if permute_upstream._is_fetch_stale():
            print("[upstream-check] upstream data is stale (>24h); fetching…")
            permute_upstream.fetch_upstream(quiet=True)
        result = check_upstream(func, c_file=c_file)
        print(_format_upstream_result(func, result))
        if result["state"] == "matched":
            sys.exit(
                f"\n[prep] REFUSING: {func} is already matched in upstream/master.\n"
                f"        Pull upstream and skip this function, or pass --skip-upstream-check\n"
                f"        if you're intentionally re-working it (e.g., for a sibling refactor)."
            )

    asm_path, asm_text = disasm_and_extract(c_file, func)
    n_instructions = sum(1 for line in asm_text.splitlines() if "*/" in line)
    print(f"asm:      {rel(asm_path).as_posix()} ({n_instructions} instructions)")

    # Compact context: list symbols referenced, with one-line signature each
    if args.context:
        refs = collect_referenced_symbols(asm_text)
        if refs:
            sigs = grep_symbols(refs)
            print()
            print("# referenced symbols:")
            for sym in refs:
                line = sigs.get(sym)
                if line:
                    print(f"  {sym:30s} ->{line}")
                else:
                    print(f"  {sym:30s} ->(not found in src/)")

    if args.m2c:
        print()
        print("# m2c starting decompilation:")
        out = run_m2c(func)
        if out is None:
            print("  (m2c failed — needs build/GALE01/asm/ + build/ctx.c)")
        else:
            # Strip the double blank lines m2c emits
            sys.stdout.write(re.sub(r"\n{2,}", "\n", out).rstrip() + "\n")

    if args.examples > 0:
        examples = find_examples(c_file, func, n=args.examples)
        if examples:
            print()
            print(f"# {len(examples)} example(s) of already-matched functions in same TU:")
            for name, body in examples:
                print()
                print(f"## {name}")
                print(body)

    if args.similar > 0:
        similar_names = find_similar_via_embeddings(asm_path, args.similar, exclude=func)
        if not similar_names:
            print()
            print("# (--similar requested but no embeddings index found — run `python tools/permute.py index-embeddings` first)")
        else:
            print()
            print(f"# {len(similar_names)} most similar matched function(s) by embedding:")
            for name in similar_names:
                pair = _extract_function_pair(name)
                if pair is None:
                    print(f"\n## {name} (asm/.c lookup failed)")
                    continue
                asm_short, c_body = pair
                print()
                print(f"## {name}")
                print(f"; asm\n{asm_short}\n\n; c\n{c_body}")

    if not args.quiet:
        print()
        print(asm_text)


OBJDIFF_CLI = ROOT / "build" / "tools" / "objdiff-cli.exe"


def _attempts_path(func: str) -> Path:
    return ROOT / "nonmatchings" / func / ".attempts.json"


def _read_attempts(func: str) -> dict:
    """Read .attempts.json for func, returning {'attempts': [...]} or empty default."""
    import json as _json
    p = _attempts_path(func)
    if not p.exists():
        return {"attempts": []}
    try:
        return _json.loads(p.read_text(encoding="utf-8"))
    except (OSError, _json.JSONDecodeError):
        return {"attempts": []}


def _write_attempts(func: str, data: dict) -> None:
    import json as _json
    p = _attempts_path(func)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        p.write_text(_json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def _enforce_attempts_cap(func: str, c_file: Path) -> bool:
    """Phase 2: refuse cmd_diff if 2 unproductive variants already recorded
    AND the .c has been modified again. Returns True if caller should proceed.

    A "variant" is a c_file modification → diff cycle. We compare each
    recorded mismatch_count against the baseline (first attempt). After 2
    unproductive ones, the 3rd attempt is blocked unless the user runs
    `reset-attempts <func>`.
    """
    state = _read_attempts(func)
    attempts = state.get("attempts", [])
    try:
        c_mtime = c_file.stat().st_mtime
    except OSError:
        return True
    last_mtime = attempts[-1].get("c_mtime", 0) if attempts else 0
    new_variant = not attempts or c_mtime > last_mtime + 1
    if not new_variant:
        return True  # Re-running diff on same source state, allow
    if len(attempts) >= 3:
        # Baseline + 2 recorded variants. If neither dropped, block the 3rd.
        baseline_count = attempts[0].get("mismatch_count", 0)
        recent = [a.get("mismatch_count", baseline_count) for a in attempts[1:3]]
        if all(c >= baseline_count for c in recent):
            sys.stderr.write(
                f"\n[STOP CRITERIA] 2 unproductive variants on {func} "
                f"(baseline {baseline_count} mismatches, attempts {recent}).\n"
                f"  -> Run `python tools/permute.py log-stuck {func} ...` and exit.\n"
                f"  -> Genuine new approach? Reset with `python tools/permute.py reset-attempts {func}`.\n"
            )
            sys.exit(2)
    return True


def _record_attempt(func: str, c_file: Path, mismatch_count: int) -> None:
    """Record this diff's outcome. Appends a new entry if .c has been
    modified since the last record; otherwise updates the latest entry."""
    state = _read_attempts(func)
    attempts = state.get("attempts", [])
    try:
        c_mtime = c_file.stat().st_mtime
    except OSError:
        return
    last_mtime = attempts[-1].get("c_mtime", 0) if attempts else 0
    new_variant = not attempts or c_mtime > last_mtime + 1
    if new_variant:
        attempts.append({"c_mtime": c_mtime, "mismatch_count": mismatch_count})
    else:
        attempts[-1]["mismatch_count"] = mismatch_count
    state["attempts"] = attempts
    _write_attempts(func, state)


def cmd_reset_attempts(args: argparse.Namespace) -> None:
    p = _attempts_path(args.func)
    if p.exists():
        try:
            p.unlink()
            print(f"[reset-attempts] cleared {p}")
        except OSError as e:
            sys.exit(f"failed to remove {p}: {e}")
    else:
        print(f"[reset-attempts] no record at {p}")


def cmd_diff(args: argparse.Namespace) -> None:
    import json

    func = args.func
    c_file = find_c_file(func)
    _enforce_attempts_cap(func, c_file)
    rel_c = rel(c_file)
    rel_base = Path("build-linux") / "GALE01" / "src" / rel_c.relative_to("src").with_suffix(".o")
    rel_target = Path("build-linux") / "GALE01" / "obj" / rel_c.relative_to("src").with_suffix(".o")
    print(f"function: {func}")
    print(f"target:   {rel_target.as_posix()}")
    print(f"base:     {rel_base.as_posix()}")

    # By default, build only the .o (fast, ~5-10s) and show objdiff strict.
    # Subagents iterate using strict %; final verification via commit-match
    # which forces a report.json rebuild for the authoritative fuzzy %.
    # Pass --with-fuzzy to also rebuild report.json (slower, ~30s).
    if args.with_fuzzy:
        print("[diff] building base + report.json…")
        rc = wsl_ninja(f"{rel_base.as_posix()} build-linux/GALE01/report.json").returncode
    else:
        print("[diff] building base (.o only — pass --with-fuzzy for report.json)…")
        rc = wsl_ninja(rel_base.as_posix()).returncode
    if rc != 0:
        sys.exit(f"build failed (exit {rc})")

    if not (ROOT / rel_target).exists():
        sys.exit(f"target object missing: {rel_target} — run a full ninja first")

    # objdiff JSON for the function
    proc = subprocess.run(
        [
            str(OBJDIFF_CLI), "diff",
            "-1", str(rel_target),
            "-2", str(rel_base),
            func,
            "--format", "json",
            "-o", "-",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"objdiff failed: {proc.stderr.strip()}")

    data = json.loads(proc.stdout)

    # Symbols live at top-level data["left"]/["right"]["symbols"], not inside sections
    target_syms = data.get("left", {}).get("symbols") or []
    base_syms = data.get("right", {}).get("symbols") or []
    target_sym = next((s for s in target_syms if s.get("name") == func), None)
    base_sym = next((s for s in base_syms if s.get("name") == func), None)

    if target_sym is None:
        sys.exit(f"function {func} not found in target object {rel_target}")
    if base_sym is None:
        print(f"\nmatch: 0% (function not yet in base — needs an implementation in {rel(c_file).as_posix()})")
        return

    pct = target_sym.get("match_percent")
    if pct is None:
        # objdiff sometimes returns None for trivially-matching cases; check base too
        pct = base_sym.get("match_percent")

    # report.json's fuzzy_match_percent is the official dashboard metric and is
    # more lenient than objdiff CLI's per-instruction match. Only read it when
    # --with-fuzzy was passed (and we just rebuilt report.json) — otherwise it's
    # stale and would mislead. Subagents iterate using strict; commit-match
    # always rebuilds report.json for the authoritative fuzzy verdict.
    fuzzy_pct = None
    if args.with_fuzzy:
        for report_path in (BUILD_LINUX / "GALE01" / "report.json", ROOT / "build" / "GALE01" / "report.json"):
            if report_path.exists():
                try:
                    rep = json.loads(report_path.read_text())
                    for u in rep.get("units", []):
                        for fn in (u.get("functions") or []):
                            if fn.get("name") == func:
                                fuzzy_pct = fn.get("fuzzy_match_percent")
                                break
                        if fuzzy_pct is not None:
                            break
                    break
                except (OSError, json.JSONDecodeError):
                    continue

    if fuzzy_pct is not None and fuzzy_pct != pct:
        print(f"\nmatch: {fuzzy_pct}% (fuzzy, dashboard metric)")
        print(f"       {pct}% (objdiff strict per-instruction)")
    else:
        print(f"\nmatch: {pct}%")

    # If fuzzy is 100, function is matched — even if strict objdiff disagrees.
    if fuzzy_pct == 100.0 or pct == 100.0:
        return

    target_ins = target_sym.get("instructions") or []
    base_ins = base_sym.get("instructions") or []
    mismatches: list[str] = []
    for t, b in zip(target_ins, base_ins):
        kind = t.get("diff_kind", "NONE")
        if kind in ("NONE", "EQUAL"):
            continue
        addr = t.get("instruction", {}).get("address", "?")
        text_t = t.get("instruction", {}).get("formatted", "?")
        text_b = b.get("instruction", {}).get("formatted", "?")
        mismatches.append(f"  @ {addr:>6}  [{kind}]\n      target: {text_t}\n      base:   {text_b}")

    # Insertions/deletions where one side is empty
    if len(target_ins) != len(base_ins):
        mismatches.append(f"  (size mismatch: target={len(target_ins)} base={len(base_ins)} instructions)")

    if mismatches:
        print(f"mismatches ({len(mismatches)}):")
        for m in mismatches[:25]:
            print(m)
        if len(mismatches) > 25:
            print(f"  ... and {len(mismatches) - 25} more")

    # Phase 2: record this variant's outcome for the attempts cap
    _record_attempt(func, c_file, len(mismatches))

    # Auto-launch permuter in the background if we're close (configurable threshold)
    # and the user passed --auto-permute. We don't kick it off unconditionally
    # because permuter only helps for true near-misses; far-off code is wasted CPU.
    if (
        getattr(args, "auto_permute", False)
        and pct is not None
        and pct < 100.0
        and len(mismatches) <= args.permute_threshold
    ):
        # Classify mismatches: refuse to dispatch when the diff is dominated by
        # reloc-symbol / numerical-offset false positives. The permuter scorer
        # treats these as equivalent (post-link bytes match) so the run returns
        # "already 100%" and the slot is wasted. log-stuck is the right action.
        reloc_count = 0
        instr_count = 0
        for t, b in zip(target_ins, base_ins):
            kind = t.get("diff_kind", "NONE")
            if kind in ("NONE", "EQUAL"):
                continue
            text_t = t.get("instruction", {}).get("formatted", "")
            text_b = b.get("instruction", {}).get("formatted", "")
            klass = _classify_mismatch(text_t, text_b)
            if klass in ("reloc-symbol", "numerical-offset"):
                reloc_count += 1
            else:
                instr_count += 1
        if instr_count == 0 and reloc_count > 0:
            print(
                f"\n[diff] REFUSING --auto-permute: all {reloc_count} mismatches are reloc-symbol/"
                f"numerical-offset class.\n"
                f"       The permuter scorer treats these as equivalent and will return 'already 100%'.\n"
                f"       Run `permute.py log-stuck {func} --tags=permuter-false-positive,...` instead."
            )
        elif not getattr(args, "force_permute", False) and reloc_count > 0 and instr_count <= 2:
            print(
                f"\n[diff] REFUSING --auto-permute: {reloc_count} reloc + only {instr_count} real-instruction "
                f"mismatches.\n"
                f"       Permuter run is likely to plateau (the scorer ignores the reloc class).\n"
                f"       Pass --force-permute to dispatch anyway."
            )
        else:
            active = list_active_permuters()
            max_concurrent = getattr(args, "max_concurrent", DEFAULT_MAX_CONCURRENT_PERMUTERS)
            use_cluster = getattr(args, "cluster", False)
            local_active = [(f, p) for f, p, c in active if not c]
            if any(f == func for f, _, _ in active):
                print(f"\n[diff] permuter for {func} already running (skipping)")
            elif not use_cluster and len(local_active) >= max_concurrent:
                print(
                    f"\n[diff] near-miss but {len(local_active)}/{max_concurrent} local permuters running — not launching."
                    f"\n       pass --cluster to dispatch to the p@h cluster instead, or"
                    f"\n       run `python tools/permute.py budget` to see them."
                )
            else:
                where = "cluster" if use_cluster else "local"
                print(f"\n[diff] near-miss ({len(mismatches)} insns off, {instr_count} real + {reloc_count} reloc) — launching {where} permuter in background")
                _launch_permuter_background(c_file, func, cluster=use_cluster)


def _launch_permuter_background(c_file: Path, func: str, cluster: bool = False) -> None:
    """Set up nonmatchings/<func>/ if not present, then launch permuter
    in the background. Logs go to build-linux/permuter-<func>.log.

    cluster=True dispatches to the local p@h cluster (vendored decomp-permuter
    `-J` mode), which uses near-zero local CPU. Use this when the subagent
    wants to fire-and-forget a permuter-territory near-miss without burning
    the local CPU budget. A `permuter-<func>.cluster` marker file is created
    so `budget` and `permute-stop` can distinguish cluster jobs from local.
    """
    nm_dir = ROOT / "nonmatchings" / func
    if not nm_dir.exists():
        # Run import.py to set up the dir (similar to cmd_permute)
        asm_path = BUILD_LINUX / f"{func}.s"
        if not asm_path.exists():
            disasm_and_extract(c_file, func)
        rel_c = rel(c_file).as_posix()
        rel_asm = rel(asm_path).as_posix()
        cmd = (
            'PERMUTER_AS="$(pwd)/build-linux/binutils/powerpc-eabi-as -mgekko -mregnames" '
            "vendor/decomp-permuter/.venv-linux/bin/python vendor/decomp-permuter/import.py "
            f"{rel_c} {rel_asm}"
        )
        rc = wsl(cmd, capture=True).returncode
        if rc != 0:
            print(f"[permute] import.py failed (exit {rc}); not launching", file=sys.stderr)
            return
        # Rename whatever import.py created (might be -2, -3 etc) to canonical name
        candidates = sorted(
            (p for p in (ROOT / "nonmatchings").iterdir() if p.is_dir() and p.name.startswith(func)),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates and candidates[0] != nm_dir:
            try:
                candidates[0].rename(nm_dir)
            except OSError:
                nm_dir = candidates[0]
        fix_compile_sh(nm_dir / "compile.sh")

    log_path = BUILD_LINUX / f"permuter-{func}.log"
    pid_path = BUILD_LINUX / f"permuter-{func}.pid"
    runner_path = BUILD_LINUX / f"permuter-{func}-runner.sh"
    log_wsl = WSL_ROOT + "/" + rel(log_path).as_posix()
    pid_wsl = WSL_ROOT + "/" + rel(pid_path).as_posix()
    runner_wsl = WSL_ROOT + "/" + rel(runner_path).as_posix()

    # Self-contained runner script: redirects its own output INSIDE WSL so
    # the log keeps being written even after Python's wsl.exe parent exits.
    if cluster:
        # Cluster mode: -J tells permuter.py to use the p@h controller.
        # PATH includes pah-shims (per tools/pah/run-distributed-permuter.ps1).
        permuter_args = "-J --show-errors"
        path_export = (
            'export PATH="$(pwd)/build-linux/pah-shims:$(pwd)/build-linux/binutils:$PATH"\n'
        )
    else:
        permuter_args = "-j 4 --show-errors"
        path_export = 'export PATH="$(pwd)/build-linux/binutils:$PATH"\n'

    runner_script = (
        "#!/usr/bin/env bash\n"
        f"exec > {shlex_quote(log_wsl)} 2>&1 < /dev/null\n"
        f"echo $$ > {shlex_quote(pid_wsl)}\n"
        f"cd {WSL_ROOT}\n"
        + path_export
        + f"exec vendor/decomp-permuter/.venv-linux/bin/python vendor/decomp-permuter/permuter.py "
        f"{rel(nm_dir).as_posix()}/ {permuter_args}\n"
    )
    runner_path.write_bytes(runner_script.encode())

    # Cluster marker — read by `budget` and `permute-stop` to distinguish
    # cluster jobs (don't count against local CPU cap) from local ones.
    cluster_marker = BUILD_LINUX / f"permuter-{func}.cluster"
    if cluster:
        cluster_marker.write_text("")
    else:
        cluster_marker.unlink(missing_ok=True)

    if pid_path.exists():
        pid_path.unlink()

    # Spawn wsl as a Popen child of this Python process. Runner script handles
    # its own log redirection inside WSL, so we don't need stdio plumbing here.
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    flags = 0
    if sys.platform == "win32":
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        [
            "wsl", "-d", WSL_DISTRO, "--", "bash", "-c",
            f"chmod +x {runner_wsl} && exec {runner_wsl}",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )

    # Give the runner script a moment to write the WSL-side pidfile
    import time
    for _ in range(30):
        if pid_path.exists() and pid_path.read_text().strip():
            break
        time.sleep(0.1)
    wsl_pid = pid_path.read_text().strip() if pid_path.exists() else "?"
    # Also stash the Windows-side wsl.exe PID — needed to kill the parent
    (BUILD_LINUX / f"permuter-{func}.winpid").write_text(str(proc.pid))
    print(f"[permute] launched permuter (wsl pid {wsl_pid}, win pid {proc.pid})")
    print(f"[permute] logs: {rel(log_path).as_posix()}")
    print(f"[permute] stop with: python tools/permute.py permute-stop {func}")


def shlex_quote(s: str) -> str:
    """Single-quote `s` for safe inclusion in a bash command."""
    return "'" + s.replace("'", "'\"'\"'") + "'"


DEFAULT_MAX_CONCURRENT_PERMUTERS = 2


def list_active_permuters() -> list[tuple[str, str, bool]]:
    """Return [(func_name, wsl_pid, is_cluster)] for each running permuter."""
    out: list[tuple[str, str, bool]] = []
    for pidfile in BUILD_LINUX.glob("permuter-*.pid"):
        if pidfile.name.endswith(".winpid"):
            continue
        func = pidfile.stem.removeprefix("permuter-")
        try:
            pid = pidfile.read_text().strip()
        except OSError:
            continue
        # Verify the process is actually still alive
        check = wsl(f"kill -0 {pid} 2>/dev/null && echo alive", capture=True)
        if "alive" in check.stdout:
            is_cluster = (BUILD_LINUX / f"permuter-{func}.cluster").exists()
            out.append((func, pid, is_cluster))
        else:
            # Reap stale pidfiles
            pidfile.unlink(missing_ok=True)
            (BUILD_LINUX / f"permuter-{func}.winpid").unlink(missing_ok=True)
            (BUILD_LINUX / f"permuter-{func}.cluster").unlink(missing_ok=True)
    return out


def cmd_budget(args: argparse.Namespace) -> None:
    """Print active permuters and current CPU budget status."""
    active = list_active_permuters()
    local = [(f, p) for f, p, c in active if not c]
    cluster = [(f, p) for f, p, c in active if c]
    print(f"active permuters: {len(local)} local / {args.max_concurrent} cap, {len(cluster)} cluster (uncapped)")
    for func, pid, is_cluster in active:
        log = BUILD_LINUX / f"permuter-{func}.log"
        last = ""
        if log.exists():
            try:
                tail = log.read_text(encoding="utf-8", errors="replace").splitlines()
                last = tail[-1][:120] if tail else ""
            except OSError:
                pass
        tag = "[cluster]" if is_cluster else "[local]  "
        print(f"  {tag} {func}  pid={pid}  {last}")
    if not active:
        print("  (no active permuters)")
    free = max(0, args.max_concurrent - len(local))
    print(f"\ncan launch {free} more local (cluster jobs are uncapped)")


def cmd_commit_improvements(args: argparse.Namespace) -> None:
    """Phase 5: scan working tree for non-match source improvements and commit
    them as `improve <func> from B% to C% fuzzy` non-match commits.

    Heuristic: per-function attempts state in nonmatchings/<func>/.attempts.json
    holds baseline + most-recent mismatch counts. If baseline > current AND the
    function's .c is modified in working tree, this is a real improvement
    worth banking.

    --threshold N (default 1): minimum mismatch_count drop to commit.
    --dry-run: preview without committing.
    --max N: at most N commits per invocation (default 5).
    """
    import json as _json
    threshold = getattr(args, "threshold", 1)
    dry_run = getattr(args, "dry_run", False)
    max_commits = getattr(args, "max", 5)

    # 1) Modified .c files in working tree
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
    modified_cs: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line or len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if path.endswith(".c") and (line[0] == "M" or line[1] == "M"):
            modified_cs.add(path)

    if not modified_cs:
        print("[commit-improvements] no modified .c files; nothing to commit")
        return

    # 2) Walk attempts.json files, filter to improvements
    nm_root = ROOT / "nonmatchings"
    candidates: list[dict] = []  # {func, c_file, baseline, current, drop}
    if nm_root.is_dir():
        for nm in nm_root.iterdir():
            ap = nm / ".attempts.json"
            if not ap.exists():
                continue
            try:
                state = _json.loads(ap.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                continue
            attempts = state.get("attempts", [])
            if len(attempts) < 2:
                continue
            baseline = attempts[0].get("mismatch_count", 0)
            current = attempts[-1].get("mismatch_count", baseline)
            drop = baseline - current
            if drop < threshold:
                continue
            func = nm.name
            try:
                c_file = find_c_file(func)
            except SystemExit:
                continue
            c_rel = rel(c_file).as_posix()
            if c_rel not in modified_cs:
                continue
            candidates.append({
                "func": func, "c_file": c_file, "c_rel": c_rel,
                "baseline": baseline, "current": current, "drop": drop,
            })

    if not candidates:
        print(f"[commit-improvements] no improvements >= {threshold} mismatches in modified files")
        return

    # 3) Group by .c file. We can only commit per-file (not per-function).
    # If multiple functions changed in one file: only commit if ALL improved.
    by_file: dict[str, list[dict]] = {}
    for c in candidates:
        by_file.setdefault(c["c_rel"], []).append(c)

    # For each file, ALSO check if there are modified funcs WITHOUT improvement:
    # if so, skip this file (don't risk committing a regression).
    print(f"[commit-improvements] {len(candidates)} improvement(s) across {len(by_file)} file(s)\n")
    committed = 0
    for c_rel, items in by_file.items():
        if committed >= max_commits:
            print(f"[commit-improvements] hit --max={max_commits}; stopping")
            break
        items.sort(key=lambda x: -x["drop"])
        names = [i["func"] for i in items]
        msg_funcs = ", ".join(names[:3]) + (f" (+{len(names)-3} more)" if len(names) > 3 else "")
        details = "; ".join(f"{i['func']}: {i['baseline']}->{i['current']}" for i in items[:5])
        msg = f"improve {msg_funcs}\n\nMismatch drops: {details}"
        print(f"  {c_rel}: {len(items)} func(s), drops {[i['drop'] for i in items]}")
        if dry_run:
            print(f"    (dry-run) would commit with message: {msg.splitlines()[0]}")
            continue
        # Stage and commit
        add = subprocess.run(["git", "add", c_rel], cwd=ROOT)
        if add.returncode != 0:
            print(f"    git add failed; skipping")
            continue
        commit = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=ROOT, capture_output=True, text=True,
        )
        if commit.returncode != 0:
            print(f"    git commit failed: {commit.stderr.strip()}")
            continue
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True,
        ).stdout.strip()
        print(f"    committed: {sha}")
        committed += 1

    print(f"\n[commit-improvements] committed {committed} file(s)")


def cmd_commit_match(args: argparse.Namespace) -> None:
    """Verify <func> is at 100% match (in both objdiff and report.json), then
    commit the touching .c file with a focused message. Refuses if not 100%.

    Subagents call this instead of raw `git commit` so a wrong claim of
    100% match can't slip through.
    """
    import json

    _sweep_stale_ninja_locks()
    func = args.func
    c_file = find_c_file(func)

    # 1) Build the .o AND refresh report.json. We gate on
    # fuzzy_match_percent below; if it's stale, a true match looks like
    # a near-miss and we'd refuse to commit.
    rel_base = Path("build-linux") / "GALE01" / "src" / rel(c_file).relative_to("src").with_suffix(".o")
    rel_target = Path("build-linux") / "GALE01" / "obj" / rel(c_file).relative_to("src").with_suffix(".o")
    rc = wsl_ninja(f"{rel_base.as_posix()} build-linux/GALE01/report.json").returncode
    if rc != 0:
        sys.exit(f"build failed; refusing to commit (exit {rc})")

    # 2) Per-function objdiff
    proc = subprocess.run(
        [str(OBJDIFF_CLI), "diff", "-1", str(rel_target), "-2", str(rel_base),
         func, "--format", "json", "-o", "-"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"objdiff failed: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    target_sym = next((s for s in data.get("left", {}).get("symbols", []) if s.get("name") == func), None)
    if target_sym is None:
        sys.exit(f"function {func} not in target object; refusing to commit")
    objdiff_pct = target_sym.get("match_percent")

    # 3) report.json
    report_path = next((p for p in (BUILD_LINUX / "GALE01" / "report.json", ROOT / "build" / "GALE01" / "report.json") if p.exists()), None)
    if report_path is None:
        sys.exit("no report.json found; refusing to commit (run a full ninja first)")
    rep = json.loads(report_path.read_text())
    rep_pct = None
    for u in rep.get("units", []):
        for fn in (u.get("functions") or []):
            if fn.get("name") == func:
                rep_pct = fn.get("fuzzy_match_percent")
                break
        if rep_pct is not None:
            break

    print(f"[verify] objdiff per-function: {objdiff_pct}%")
    print(f"[verify] report.json fuzzy:   {rep_pct}%")

    # report.json's fuzzy_match_percent is the official dashboard metric. If
    # it says 100.0, the function is matched even if objdiff CLI's stricter
    # per-instruction view has false-positive 'mismatches' on identical
    # instructions (a known display artifact for some functions).
    if rep_pct != 100.0:
        sys.exit(
            f"REFUSING to commit: report.json says {rep_pct}% (not 100.0).\n"
            f"  objdiff per-function: {objdiff_pct}%\n"
            f"Either fix the function further or report back unmatched."
        )
    if objdiff_pct != 100.0:
        print(
            f"[verify] NOTE: objdiff CLI shows {objdiff_pct}% but report.json shows 100.0% "
            f"(known stricter-vs-fuzzy disagreement; report.json is authoritative)."
        )

    # 4) Commit the .c file with a focused message
    msg = args.message or f"Match {func}"
    add = subprocess.run(["git", "add", str(rel(c_file).as_posix())], cwd=ROOT)
    if add.returncode != 0:
        sys.exit("git add failed")
    commit = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(commit.stdout)
    sys.stderr.write(commit.stderr)
    if commit.returncode != 0:
        sys.exit("git commit failed (see above)")
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    print(f"\n[commit-match] OK: {sha} for {func}")
    _log_event("match", func=func, sha=sha, fuzzy=rep_pct, strict=objdiff_pct)

    if getattr(args, "with_header", False):
        _commit_header_followup(func, sha)


def _commit_header_followup(func: str, parent_sha: str) -> None:
    """After a successful commit-match, scan for modified .h/.static.h files
    that mention `func` and commit them as a follow-up. Verifies the build
    still passes before committing; rolls back staging if not.
    """
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print("[with-header] git status failed; skipping follow-up")
        return
    candidates: list[str] = []
    for line in proc.stdout.splitlines():
        if not line or len(line) < 4:
            continue
        status = line[:2]
        path = line[3:].strip().strip('"')
        if path.endswith(".h") and (status[0] == "M" or status[1] == "M"):
            candidates.append(path)

    if not candidates:
        return

    matching: list[str] = []
    for path in candidates:
        diff = subprocess.run(
            ["git", "diff", "--unified=0", "--", path],
            cwd=ROOT, capture_output=True, text=True,
        )
        if diff.returncode == 0 and re.search(rf"\b{re.escape(func)}\b", diff.stdout):
            matching.append(path)

    if not matching:
        return

    print(f"\n[with-header] staging {len(matching)} header(s) referencing {func}: {matching}")
    add = subprocess.run(["git", "add", "--"] + matching, cwd=ROOT)
    if add.returncode != 0:
        print("[with-header] git add failed; aborting follow-up")
        return

    # Verify build still passes after staging (the .c changes are committed,
    # so the .h must remain compatible). If `check` regresses, unstage and bail.
    print("[with-header] verifying build still passes...")
    check = wsl_ninja(capture=False).returncode
    if check != 0:
        print("[with-header] BUILD FAILED with header staged; unstaging and aborting follow-up")
        subprocess.run(["git", "reset", "HEAD", "--"] + matching, cwd=ROOT)
        return

    msg = f"{func}: header follow-up to {parent_sha}"
    commit = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=ROOT, capture_output=True, text=True,
    )
    if commit.returncode != 0:
        print(f"[with-header] git commit failed: {commit.stderr.strip()}")
        return
    sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    print(f"[with-header] header follow-up: {sha}")


def _kill_permuter(func: str) -> list[str]:
    """Kill a backgrounded permuter and clean up pidfiles + cluster marker.

    Returns descriptions of what was killed (empty list if there was nothing).
    Shared by cmd_permute_stop and cmd_reap.
    """
    pid_path = BUILD_LINUX / f"permuter-{func}.pid"
    winpid_path = BUILD_LINUX / f"permuter-{func}.winpid"
    killed = []
    if pid_path.exists():
        pid = pid_path.read_text().strip()
        wsl(f"kill {pid} 2>&1; pkill -P {pid} 2>&1; true", capture=True)
        killed.append(f"wsl pid {pid}")
        pid_path.unlink(missing_ok=True)
    if winpid_path.exists():
        winpid = winpid_path.read_text().strip()
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", winpid], capture_output=True)
        killed.append(f"win pid {winpid}")
        winpid_path.unlink(missing_ok=True)
    (BUILD_LINUX / f"permuter-{func}.cluster").unlink(missing_ok=True)
    return killed


def cmd_permute_stop(args: argparse.Namespace) -> None:
    """Kill a backgrounded permuter run started by `diff --auto-permute`."""
    killed = _kill_permuter(args.func)
    if not killed:
        sys.exit(f"no pidfiles for {args.func} — was permuter launched?")
    print(f"[permute-stop] killed {', '.join(killed)}")


def _newest_output_mtime(func: str) -> Optional[float]:
    """Return the mtime of the newest output-NN-K file in nonmatchings/<func>/.

    None if no outputs exist. Used as the "still making progress" signal —
    the permuter only writes a new output when it finds a candidate worth
    saving, so a stale newest-output mtime means real plateau.
    """
    nm = ROOT / "nonmatchings" / func
    if not nm.is_dir():
        return None
    outputs = list(nm.glob("output-*"))
    if not outputs:
        return None
    return max(o.stat().st_mtime for o in outputs)


def _best_output(func: str) -> Optional[tuple[int, Path]]:
    """Return (score, path) for the LOWEST-score output-NN-K dir.

    In permuter convention, lower score = better match. Score 0 = perfect.
    The directory name is `output-<score>-<seq>`, so we pick the smallest
    first number to find the closest-to-match candidate.
    """
    nm = ROOT / "nonmatchings" / func
    if not nm.is_dir():
        return None
    best: Optional[tuple[int, Path]] = None
    for p in nm.iterdir():
        m = re.match(r"output-(\d+)-(\d+)$", p.name)
        if m:
            score = int(m.group(1))
            if best is None or score < best[0]:
                best = (score, p)
    return best


# Defaults tuned for the cluster: cluster runs are cheap, so we let them
# run longer than local before reaping. Override via CLI flags.
DEFAULT_REAP_WALL_MIN = 60      # max wall-clock per permuter
DEFAULT_REAP_SILENT_MIN = 15    # max minutes since last output


def cmd_reap(args: argparse.Namespace) -> None:
    """Kill stuck/timed-out permuters.

    Two reasons to reap:
    - Wall-clock exceeded (`--wall-cap-min`, default 60): the run started
      a while ago, hasn't matched, time to give up so the slot frees up.
    - Silent (`--silent-cap-min`, default 15): no new output-NN-K files
      AND log file untouched for N minutes. Permuter is either stuck in a
      pathological state or the cluster connection died.

    Pass `--dry-run` to see what would be killed without acting.
    """
    import time
    now = time.time()
    active = list_active_permuters()
    if not active:
        print("[reap] no active permuters")
        return

    wall_cap = args.wall_cap_min * 60
    silent_cap = args.silent_cap_min * 60
    actions: list[tuple[str, str, bool]] = []  # (func, reason, did_kill)

    aggressive = getattr(args, "aggressive", False)

    for func, pid, is_cluster in active:
        pid_path = BUILD_LINUX / f"permuter-{func}.pid"
        log_path = BUILD_LINUX / f"permuter-{func}.log"
        wall_age = now - pid_path.stat().st_mtime if pid_path.exists() else 0.0
        log_age = now - log_path.stat().st_mtime if log_path.exists() else float("inf")
        out_mtime = _newest_output_mtime(func)
        out_age = (now - out_mtime) if out_mtime else float("inf")

        reason: Optional[str] = None
        if aggressive:
            cur_fuzzy = _current_fuzzy_pct(func)
            if cur_fuzzy is not None and cur_fuzzy >= 100.0:
                reason = "already-matched (report.json fuzzy=100%)"
        if reason is None and wall_age > wall_cap:
            reason = f"wall-clock {wall_age/60:.0f}min > {args.wall_cap_min}min cap"
        elif reason is None and log_age > silent_cap and out_age > silent_cap:
            reason = (f"silent {min(log_age, out_age)/60:.0f}min "
                      f"(no log + no new outputs)")

        if reason:
            tag = "[cluster]" if is_cluster else "[local]  "
            if args.dry_run:
                print(f"[reap] would kill {tag} {func}: {reason}")
                actions.append((func, reason, False))
            else:
                killed = _kill_permuter(func)
                kdesc = ", ".join(killed) if killed else "(no pidfiles)"
                print(f"[reap] killed {tag} {func}: {reason}  [{kdesc}]")
                actions.append((func, reason, True))

    if not actions:
        print(f"[reap] all {len(active)} permuters within budgets "
              f"(wall<{args.wall_cap_min}min, silent<{args.silent_cap_min}min)")

    # Aggressive: also clean up stale .dispatched markers for matched funcs
    if aggressive and not args.dry_run:
        nm_root = ROOT / "nonmatchings"
        cleaned = 0
        if nm_root.is_dir():
            for nm in nm_root.iterdir():
                marker = nm / ".dispatched"
                if not marker.exists():
                    continue
                cur_fuzzy = _current_fuzzy_pct(nm.name)
                if cur_fuzzy is not None and cur_fuzzy >= 100.0:
                    try:
                        marker.unlink()
                        cleaned += 1
                    except OSError:
                        pass
        if cleaned:
            print(f"[reap] cleaned {cleaned} stale .dispatched markers (matched funcs)")


def cmd_harvest(args: argparse.Namespace) -> None:
    """Report on permuter results: 100% matches, plateaued runs, in-progress.

    Walks every nonmatchings/<func>/ dir (whether a permuter is currently
    active or not) and classifies based on the best output-NN-K file:

    - HIT 100%: the permuter found a match. Manual step is still needed
      to translate the matching candidate from preprocessed base.c form
      back to src/<file>.c (the preprocessor inlines, we have to undo it).
      Harvest just FLAGS these — actual commit happens via commit-match
      after the source change is ported.
    - PLATEAU: best is < 100% and the newest output-NN-K is older than
      `--plateau-min` minutes. Worth re-dispatching a fresh subagent
      using this best as the new baseline.
    - PROGRESSING: best is < 100% and outputs are still arriving. Leave
      it alone.
    """
    import time
    now = time.time()
    plateau_cap = args.plateau_min * 60

    nm_root = ROOT / "nonmatchings"
    if not nm_root.is_dir():
        print("[harvest] no nonmatchings/ directory")
        return

    active_funcs = {f for f, _, _ in list_active_permuters()}
    notes = _parse_notes()
    # Tags that mean "permuter cannot finish this — TU-layout blocker."
    # If a func has any of these tags, score=0 outputs are presumed
    # false-positive (linker-equivalent but reloc-symbol mismatched).
    BLOCKER_TAGS = {"permuter-false-positive", "tu-data-osreport",
                    "tu-wide-data", "cross-tu-globals", "data-symbols-missing"}

    def func_blocker_tags(f: str) -> set[str]:
        e = notes.get(f)
        return e["tags"] & BLOCKER_TAGS if e else set()

    def func_in_notes(f: str) -> bool:
        return f in notes

    matched: list[tuple[str, int, Path, str]] = []
    false_pos: list[tuple[str, int, Path, set[str], str]] = []
    already_matched: list[tuple[str, str, bool]] = []  # (dir_func, report_func, is_active_permuter)
    plateau: list[tuple[str, int, float, bool, bool]] = []
    progressing: list[tuple[str, int, float, bool]] = []
    no_outputs: list[str] = []

    for nm in sorted(nm_root.iterdir()):
        if not nm.is_dir():
            continue
        func = nm.name
        report_func = _canonical_report_func(func)
        best = _best_output(func)
        if best is None:
            no_outputs.append(func)
            continue
        score, path = best
        newest = _newest_output_mtime(func) or 0
        age = now - newest
        is_active = func in active_funcs

        if score == 0:
            # If already at fuzzy=100, leftover nonmatchings dir from a
            # past run. Surface separately so the user can kill any
            # permuter still running on it.
            cur_fuzzy = _current_fuzzy_pct(report_func)
            if cur_fuzzy is not None and cur_fuzzy >= 100.0:
                already_matched.append((func, report_func, is_active))
                continue
            blockers = func_blocker_tags(report_func)
            if blockers and not args.show_false_positives:
                false_pos.append((func, score, path, blockers, report_func))
            else:
                matched.append((func, score, path, report_func))
        elif age > plateau_cap:
            plateau.append((func, score, age, is_active, func_in_notes(report_func)))
        else:
            progressing.append((func, score, age, is_active))

    if matched:
        print("=== HIT 100% (need source port + commit-match) ===")
        for func, score, path, report_func in matched:
            rel_path = path.relative_to(ROOT).as_posix()
            label = func if func == report_func else f"{func} (report: {report_func})"
            print(f"  {label}: {rel_path}")
            print(f"    diff against base.c, port the change to src/, then:")
            print(f"    python tools/permute.py commit-match {report_func}")

    if already_matched:
        print()
        print("=== ALREADY MATCHED — kill any active permuter on these ===")
        for func, report_func, is_active in already_matched:
            tag = "[active — kill it]" if is_active else "[idle — leftover dir]"
            cmd = f"  python tools/permute.py permute-stop {func}" if is_active else ""
            label = func if func == report_func else f"{func} (report: {report_func})"
            print(f"  {tag} {label}{('  →' + cmd) if cmd else ''}")

    if false_pos:
        print()
        print("=== SUPPRESSED HITS (known TU-layout blockers — score=0 doesn't translate to fuzzy=100) ===")
        for func, score, path, blockers, report_func in false_pos:
            label = func if func == report_func else f"{func} (report: {report_func})"
            print(f"  {label} [{', '.join(sorted(blockers))}]")
        print(f"  ({len(false_pos)} suppressed; pass --show-false-positives to see them anyway)")

    if plateau:
        print()
        print("=== PLATEAU (ready for re-dispatch) ===")
        for func, score, age, is_active, in_notes in plateau:
            tag = "[active]" if is_active else "[idle]  "
            note_marker = "  [in-notes]" if in_notes else ""
            print(f"  {tag} {func}: best={score}%  no improvement for {age/60:.0f}min{note_marker}")

    if progressing:
        print()
        print("=== STILL PROGRESSING ===")
        for func, score, age, is_active in progressing:
            tag = "[active]" if is_active else "[idle]  "
            print(f"  {tag} {func}: best={score}%  last improvement {age/60:.0f}min ago")

    if args.show_empty and no_outputs:
        print()
        print("=== NO OUTPUTS YET ===")
        for func in no_outputs:
            print(f"  {func}")

    print()
    print(f"summary: {len(matched)} matched, {len(false_pos)} false-positive (suppressed), "
          f"{len(plateau)} plateau, {len(progressing)} progressing, {len(no_outputs)} no-outputs")


# Notes-related code (CANONICAL_TAGS, _parse_notes, cmd_notes, cmd_log_stuck)
# lives in tools/permute_notes.py — extracted as the first step of a per-command-group
# split. The module is wired up via permute_notes._set_deps() in main(). Re-export here
# for backward compatibility (some tests / external callers may still import these).
import permute_notes
from permute_notes import (
    CANONICAL_TAGS,
    _validate_tags,
    _parse_frontmatter,
    _parse_notes,
    cmd_log_stuck,
    cmd_notes,
)
import permute_upstream
from permute_upstream import check_upstream, format_result as _format_upstream_result

_NOTES_PATH = permute_notes._NOTES_PATH
_NOTES_DIR = permute_notes._NOTES_DIR


def _current_fuzzy_pct(func: str) -> Optional[float]:
    """Fetch current fuzzy_match_percent for func from report.json, or None."""
    import json
    for report_path in (BUILD_LINUX / "GALE01" / "report.json", ROOT / "build" / "GALE01" / "report.json"):
        if not report_path.exists():
            continue
        try:
            rep = json.loads(report_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for u in rep.get("units", []):
            for fn in (u.get("functions") or []):
                if fn.get("name") == func:
                    return fn.get("fuzzy_match_percent")
    return None


def _canonical_report_func(func: str) -> str:
    """Map permuter collision dirs like `foo-2` back to report symbol `foo`."""
    if _current_fuzzy_pct(func) is not None:
        return func
    m = re.match(r"^(.+)-\d+$", func)
    if m and _current_fuzzy_pct(m.group(1)) is not None:
        return m.group(1)
    return func


# cmd_log_stuck is now defined in permute_notes.py and imported above.


# ---------------------------------------------------------------------------
# TU-refactor lock (Phase 1): exclusive multi-function-edit mode
# ---------------------------------------------------------------------------

_TU_LOCK_PATH = ROOT / "build-linux" / ".tu-refactor.lock"
_TU_LOCK_STALE_SEC = 2 * 60 * 60  # 2 hours


def _read_tu_lock() -> Optional[dict]:
    """Return {tu, pid, ts} if a live tu-refactor lock exists, else None.

    Locks are mtime-stale only (older than 2h). Pid-liveness is NOT checked
    because tu-lock is acquired by a subagent's python invocations across
    multiple short-lived processes — the pid in the lockfile is always
    "dead" by the next call.
    """
    if not _TU_LOCK_PATH.exists():
        return None
    import json as _json, time as _time
    try:
        data = _json.loads(_TU_LOCK_PATH.read_text(encoding="utf-8"))
        age = _time.time() - _TU_LOCK_PATH.stat().st_mtime
        if age > _TU_LOCK_STALE_SEC:
            try:
                _TU_LOCK_PATH.unlink()
            except OSError:
                pass
            return None
        return data
    except (OSError, ValueError, _json.JSONDecodeError):
        return None


def _acquire_tu_lock(tu_path: str) -> bool:
    """Atomically claim the global TU-refactor lock for `tu_path`.

    Returns True if acquired, False if another live lock exists. Reaps stale
    locks first.
    """
    import json as _json, time as _time
    existing = _read_tu_lock()
    if existing is not None:
        return existing.get("tu") == tu_path  # idempotent re-lock by same TU
    _TU_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(_TU_LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            payload = _json.dumps({"tu": tu_path, "pid": os.getpid(), "ts": _time.time()})
            os.write(fd, payload.encode())
        finally:
            os.close(fd)
        return True
    except FileExistsError:
        # Race with another acquire — re-check
        again = _read_tu_lock()
        return bool(again and again.get("tu") == tu_path)


def _release_tu_lock(tu_path: str) -> None:
    """Release the lock if it belongs to `tu_path`. No-op otherwise."""
    cur = _read_tu_lock()
    if cur is not None and cur.get("tu") == tu_path:
        try:
            _TU_LOCK_PATH.unlink()
        except OSError:
            pass


def cmd_tu_lock(args: argparse.Namespace) -> None:
    """Claim the global TU-refactor lock for `args.tu` (a .c source path)."""
    tu = args.tu
    if not (ROOT / tu).exists():
        sys.exit(f"TU not found: {tu}")
    if _acquire_tu_lock(tu):
        print(f"[tu-lock] acquired for {tu}")
    else:
        cur = _read_tu_lock()
        sys.exit(f"[tu-lock] FAILED — another lock active: {cur}")


def cmd_tu_unlock(args: argparse.Namespace) -> None:
    """Release the TU-refactor lock for `args.tu`."""
    _release_tu_lock(args.tu)
    print(f"[tu-unlock] released {args.tu}")


def cmd_tu_brief(args: argparse.Namespace) -> None:
    """Emit a TU-refactor brief: stuck functions in this TU grouped by blocker.

    Used by mama Claude to dispatch a multi-function refactor agent that
    fixes a TU-wide structural issue (e.g. sdata2 named-floats, BSS-anchor
    coalescing) all at once. The agent should hold a `tu-lock` while editing
    so single-function agents don't pick functions in this TU.
    """
    import json as _json
    tu = args.tu
    notes = _parse_notes()
    sym_cache = _load_or_build_symbol_cache()

    in_tu = []
    for fname, entry in notes.items():
        tu_for = sym_cache.get(fname)
        if tu_for == tu:
            in_tu.append((fname, entry))

    if not in_tu:
        print(f"# TU brief: {tu}")
        print(f"# No stuck-tagged functions in this TU. Pick a different TU or use compact-brief.")
        return

    # Group by tag
    from collections import defaultdict
    by_tag: dict[str, list[str]] = defaultdict(list)
    for fname, entry in in_tu:
        for tag in entry["tags"]:
            by_tag[tag].append(fname)

    # Read fuzzy% from report.json
    report_path = next((p for p in (BUILD_LINUX / "GALE01" / "report.json", ROOT / "build" / "GALE01" / "report.json") if p.exists()), None)
    fuzzy_for: dict[str, Optional[float]] = {}
    if report_path is not None:
        try:
            rep = _json.loads(report_path.read_text())
            for u in rep.get("units", []):
                for fn in (u.get("functions") or []):
                    name = fn.get("name")
                    if name in [n for n, _ in in_tu]:
                        fuzzy_for[name] = fn.get("fuzzy_match_percent")
        except (OSError, _json.JSONDecodeError):
            pass

    # Lock status
    cur_lock = _read_tu_lock()
    lock_str = "FREE"
    if cur_lock is not None:
        if cur_lock.get("tu") == tu:
            lock_str = f"HELD by this TU (pid {cur_lock.get('pid')})"
        else:
            lock_str = f"BLOCKED — another TU locked: {cur_lock.get('tu')}"

    print(f"# TU-refactor brief: {tu}")
    print(f"# Lock status: {lock_str}")
    print(f"# {len(in_tu)} stuck-tagged functions, grouped by shared blocker:")
    print()

    # Top tags by count
    SHARED_BLOCKER_TAGS = {
        "tu-wide-data", "tu-data-osreport", "cross-tu-globals", "data-symbols-missing",
        "permuter-false-positive", "bss-anchor", "sdata2-float", "sdata2-named-floats",
        "frame-size", "stack-offset", "paired-siblings", "rodata-typing",
    }
    relevant_tags = [(t, fns) for t, fns in by_tag.items() if t in SHARED_BLOCKER_TAGS and len(fns) >= 2]
    relevant_tags.sort(key=lambda x: -len(x[1]))

    if relevant_tags:
        print("## Shared blockers (2+ funcs):")
        for tag, fns in relevant_tags:
            print(f"  [{tag}] {len(fns)} funcs:")
            for f in fns[:10]:
                fuzzy = fuzzy_for.get(f)
                fpct = f"{fuzzy:.2f}%" if fuzzy is not None else "?"
                print(f"    {f}  fuzzy={fpct}")
            if len(fns) > 10:
                print(f"    ... and {len(fns) - 10} more")
            print()
    else:
        print("## No shared blockers found across 2+ functions in this TU.")
        print("## Functions and their tags:")
        for fname, entry in in_tu:
            tags_str = ", ".join(sorted(entry["tags"]))
            fuzzy = fuzzy_for.get(fname)
            fpct = f"{fuzzy:.2f}%" if fuzzy is not None else "?"
            print(f"  {fname}  fuzzy={fpct}  tags={tags_str}")
        print()

    # Recommendation
    if relevant_tags:
        top_tag, top_fns = relevant_tags[0]
        print(f"# Recommendation:")
        print(f"  1. `python tools/permute.py tu-lock {tu}` to claim exclusive edit access")
        print(f"  2. Tackle the `{top_tag}` cluster ({len(top_fns)} funcs) — likely shared root cause")
        print(f"  3. Read prior diagnoses: `python tools/permute.py notes {top_fns[0]}` and siblings")
        print(f"  4. Fix the structural blocker (TU-wide refactor — multiple functions + headers)")
        print(f"  5. `python tools/permute.py tu-unlock {tu}` when done")
        print(f"  6. Commit each function that reaches 100% via `commit-match --with-header`")


# _parse_frontmatter, _parse_notes, cmd_notes are defined in permute_notes.py
# and imported above.


def cmd_backlog(args: argparse.Namespace) -> None:
    """List functions worth re-dispatching to the cluster permuter.

    Two sources, both filtered against decomp-notes structural blockers:

    A) Plateau-from-harvest: had a permuter run before, plateaued with
       a low score (close to flip). These are the strongest candidates —
       the permuter already did the heavy exploration; more grinding has
       a real chance.

    B) Near-misses from report.json that never got a permuter dispatch.
       Filtered to instructions <= --max-mismatches (default 6) and
       fuzzy_match >= --min-fuzzy (default 99) so we focus on the close
       ones. Skipped if already in notes as a structural blocker.

    With --fire N, re-dispatches the top N (cluster mode).
    """
    import json
    import time

    notes = _parse_notes()
    BLOCKER_TAGS = {"permuter-false-positive", "tu-data-osreport",
                    "tu-wide-data", "cross-tu-globals", "data-symbols-missing"}

    def is_structural_blocker(f: str) -> bool:
        e = notes.get(f)
        return bool(e and (e["tags"] & BLOCKER_TAGS))

    # Per-TU stuck count for --ready / --no-stuck-tu filters
    sym_cache = _load_or_build_symbol_cache()
    tu_stuck_count: dict[str, int] = {}
    for nfunc in notes:
        tu_path = sym_cache.get(nfunc)
        if tu_path:
            tu_stuck_count[tu_path] = tu_stuck_count.get(tu_path, 0) + 1

    apply_tu_filter = getattr(args, "ready", False) or getattr(args, "no_stuck_tu", False)

    def in_stuck_tu(f: str) -> bool:
        if not apply_tu_filter:
            return False
        tu = sym_cache.get(f)
        return bool(tu and tu_stuck_count.get(tu, 0) >= 2)

    # TU-refactor lock check (--ready default ON): skip funcs whose TU is being refactored
    apply_tu_lock_filter = getattr(args, "ready", False) or getattr(args, "no_tu_locked", False)
    locked_tu = None
    if apply_tu_lock_filter:
        cur_lock = _read_tu_lock()
        if cur_lock is not None:
            locked_tu = cur_lock.get("tu")

    def in_locked_tu(f: str) -> bool:
        if not apply_tu_lock_filter or not locked_tu:
            return False
        return sym_cache.get(f) == locked_tu

    # Dispatch marker check (--ready only): skip funcs touched within last 60 min
    apply_dispatch_filter = getattr(args, "ready", False)
    DISPATCH_EXPIRY_SEC = 60 * 60

    def is_dispatched(f: str) -> bool:
        if not apply_dispatch_filter:
            return False
        marker = ROOT / "nonmatchings" / f / ".dispatched"
        if not marker.exists():
            return False
        try:
            age = time.time() - marker.stat().st_mtime
        except OSError:
            return False
        return age < DISPATCH_EXPIRY_SEC

    active_funcs = {f for f, _, _ in list_active_permuters()}
    nm_root = ROOT / "nonmatchings"

    # ---- A) Plateaued runs (per-function best score from output dir names)
    now = time.time()
    plateau_entries: list[tuple[str, int, float]] = []  # (func, best_score, age_min)
    if nm_root.is_dir():
        for nm in sorted(nm_root.iterdir()):
            if not nm.is_dir():
                continue
            func = nm.name
            if func in active_funcs:
                continue
            if is_structural_blocker(func):
                continue
            if in_stuck_tu(func):
                continue
            if in_locked_tu(func):
                continue
            if is_dispatched(func):
                continue
            # Skip if already matched in current build (a leftover nonmatchings/<func>/
            # dir from before commit-match doesn't mean there's still work to do).
            cur_fuzzy = _current_fuzzy_pct(func)
            if cur_fuzzy is not None and cur_fuzzy >= 100.0:
                continue
            best = _best_output(func)
            if best is None:
                continue
            score, _ = best
            # score == 0 = perfect match — already handled by harvest
            if score == 0:
                continue
            newest = _newest_output_mtime(func) or 0
            age_min = (now - newest) / 60
            # Only "plateau" if it's been quiet for a bit
            if age_min < args.plateau_min:
                continue
            plateau_entries.append((func, score, age_min))

    # Sort: highest scores first (closer to flip in this codebase's convention)
    # Lowest score first = closest to flip = most worth re-firing
    plateau_entries.sort(key=lambda x: (x[1], x[2]))

    # ---- B) Fresh near-misses from report.json that haven't been dispatched
    fresh: list[tuple[str, float, int]] = []  # (func, fuzzy_pct, mismatch_count)
    report_path = next((p for p in (BUILD_LINUX / "GALE01" / "report.json", ROOT / "build" / "GALE01" / "report.json") if p.exists()), None)
    if report_path is not None and not args.no_fresh:
        rep = json.loads(report_path.read_text())
        for u in rep.get("units", []):
            for fn in (u.get("functions") or []):
                name = fn.get("name")
                if not name:
                    continue
                fuzzy = fn.get("fuzzy_match_percent") or 0
                if fuzzy >= 100 or fuzzy < args.min_fuzzy:
                    continue
                if is_structural_blocker(name):
                    continue
                if in_stuck_tu(name):
                    continue
                if in_locked_tu(name):
                    continue
                if is_dispatched(name):
                    continue
                if name in active_funcs:
                    continue
                # Skip if it already has output dirs (covered in plateau list)
                nm_dir = nm_root / name
                if nm_dir.is_dir():
                    continue
                size_raw = fn.get("size", 0)
                try:
                    size = int(size_raw, 16) if isinstance(size_raw, str) else int(size_raw)
                except (TypeError, ValueError):
                    size = 0
                instr_count = size // 4 if size else 999
                # Estimate mismatches: if fuzzy is 99.x% on N instructions, mismatch ~= N*(1-fuzzy/100)
                est_mismatches = max(1, int(round(instr_count * (1 - fuzzy / 100))))
                if est_mismatches > args.max_mismatches:
                    continue
                fresh.append((name, fuzzy, est_mismatches))

    fresh.sort(key=lambda x: (x[2], -x[1]))

    # ---- Optional --reserve: atomically claim .dispatched markers as we print.
    # Race-safe: O_CREAT|O_EXCL ensures only one parallel mama call wins per func.
    apply_reserve = getattr(args, "reserve", False)
    reserved: set[str] = set()
    skipped_reserved: set[str] = set()

    def reserve(func: str) -> bool:
        if not apply_reserve:
            return True
        marker_dir = nm_root / func
        marker_dir.mkdir(parents=True, exist_ok=True)
        marker = marker_dir / ".dispatched"
        try:
            fd = os.open(str(marker), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            reserved.add(func)
            return True
        except FileExistsError:
            skipped_reserved.add(func)
            return False

    # ---- Print
    print(f"=== PLATEAU BACKLOG (had permuter, score=close, not blocked) ===")
    if not plateau_entries:
        print("  (empty)")
    else:
        printed = 0
        for func, score, age_min in plateau_entries:
            if printed >= args.limit:
                break
            if not reserve(func):
                continue
            note_marker = "  [in-notes]" if func in notes else ""
            res_marker = "  [RESERVED]" if apply_reserve else ""
            print(f"  {func:40s}  best-score={score}  age={age_min:.0f}min{note_marker}{res_marker}")
            printed += 1

    print()
    print(f"=== FRESH BACKLOG (close near-misses, never dispatched) ===")
    if not fresh:
        print("  (empty)")
    else:
        printed = 0
        for func, fuzzy, est in fresh:
            if printed >= args.limit:
                break
            if not reserve(func):
                continue
            note_marker = "  [in-notes]" if func in notes else ""
            res_marker = "  [RESERVED]" if apply_reserve else ""
            # Use 4 decimals so 99.99% doesn't round to 100.00% and look matched
            print(f"  {func:40s}  fuzzy={fuzzy:.4f}%  est-mismatches~={est}{note_marker}{res_marker}")
            printed += 1

    print()
    print(f"summary: {len(plateau_entries)} plateau + {len(fresh)} fresh "
          f"= {len(plateau_entries) + len(fresh)} candidates")
    if apply_reserve:
        print(f"reserved {len(reserved)} candidate(s) this call; skipped {len(skipped_reserved)} already reserved by parallel callers")

    # ---- Fire N to cluster
    if args.fire and (plateau_entries or fresh):
        # Combine: plateau first (already had compute), then fresh
        combined = [f for f, _, _ in plateau_entries] + [f for f, _, _ in fresh]
        to_fire = combined[:args.fire]
        print()
        print(f"=== FIRING {len(to_fire)} to cluster ===")
        for func in to_fire:
            try:
                c_file = find_c_file(func)
            except SystemExit as e:
                print(f"  [skip] {func}: {e}")
                continue
            # Touch .dispatched so subsequent --ready calls skip this func
            marker_dir = nm_root / func
            marker_dir.mkdir(parents=True, exist_ok=True)
            (marker_dir / ".dispatched").touch()
            print(f"  [fire] {func}")
            _launch_permuter_background(c_file, func, cluster=True)


_RELOC_MARKERS = ("@ha", "@l", "@sda21", "@sda2", "@sda",
                  "...bss.", "...data.", "...rodata.", "...sdata.")


def _classify_mismatch(target_text: str, base_text: str) -> str:
    """Classify a single mismatched instruction.

    Returns one of:
    - 'reloc-symbol': same opcode/regs, but reloc points to a different
      symbol (BSS-anchor, sdata2 float, .data.0 anchor). Permuter can't fix.
    - 'numerical-offset': same opcode/regs/symbols, only the numerical
      immediate (hex offset) differs. Almost always a consequence of a
      sibling reloc-symbol mismatch (offset = anchor_diff). Treated as
      reloc-derived for tier purposes.
    - 'instruction': real difference — different opcode/register, or
      a non-reloc-derived immediate. Permuter territory.
    """
    t_has_reloc = any(m in target_text for m in _RELOC_MARKERS)
    b_has_reloc = any(m in base_text for m in _RELOC_MARKERS)
    if t_has_reloc and b_has_reloc:
        # Strip the entire symbol-and-marker part. The format is
        # "<op> <regs>..., <SYMBOL>@<MARKER>(<reg>)?" — we want everything
        # before the comma that starts the symbol.
        def opcode_regs(s: str) -> str:
            last_marker = -1
            for m in _RELOC_MARKERS:
                i = s.rfind(m)
                if i > last_marker:
                    last_marker = i
            if last_marker < 0:
                return s.strip()
            prefix = s[:last_marker]
            last_comma = prefix.rfind(",")
            if last_comma >= 0:
                return prefix[:last_comma].strip()
            return prefix.strip()
        return "reloc-symbol" if opcode_regs(target_text) == opcode_regs(base_text) else "instruction"

    # No reloc markers on either side. Check if it's a numerical-offset-only diff.
    # Replace hex constants with IMM placeholder and compare.
    def imm_skeleton(s: str) -> str:
        return re.sub(r"0x[0-9a-fA-F]+", "IMM", s)
    if imm_skeleton(target_text) == imm_skeleton(base_text) and target_text != base_text:
        return "numerical-offset"
    return "instruction"


_BRIEF_CACHE_DIR = BUILD_LINUX / "briefs"


def _read_function_body(c_file: Path, func: str) -> str:
    """Extract the function body from a .c file. Returns C source or empty string."""
    try:
        c_text = c_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    fn_def_rx = re.compile(
        rf"^[a-zA-Z_][\w\s\*]*?\b{re.escape(func)}\s*\([^;)]*\)\s*\n?\s*\{{",
        re.MULTILINE,
    )
    m = fn_def_rx.search(c_text)
    if not m:
        return ""
    body_start = c_text.find("{", m.end() - 1)
    if body_start < 0:
        return ""
    depth = 0
    for i in range(body_start, len(c_text)):
        if c_text[i] == "{":
            depth += 1
        elif c_text[i] == "}":
            depth -= 1
            if depth == 0:
                return c_text[m.start():i + 1]
    return ""


def _classify_brief_mismatch(target_text: str, base_text: str) -> str:
    """Categorize a mismatched instruction for compact-brief.

    Categories:
    - permuter-false-positive: reloc-symbol diffs (post-link bytes match).
    - frame-size: stwu/stmw/lmw involving r1 (prologue/epilogue frame).
    - stack-offset: load/store with r1 base, different immediate offset.
    - regalloc: same opcode/immediate skeleton, different register numbers.
    - real: opcode choice / operand swap / non-r1 immediate diff.

    Order matters: r1-based diffs are checked before generic reloc/numerical-offset
    so a `stwu r1, -0x70` vs `-0x68` lands as frame-size, not permuter-false-positive.
    """
    # Reloc-symbol class (anchor split, named-vs-anonymous): only when reloc
    # markers actually present on both sides.
    if any(m in target_text for m in _RELOC_MARKERS) or any(m in base_text for m in _RELOC_MARKERS):
        cls = _classify_mismatch(target_text, base_text)
        if cls == "reloc-symbol":
            return "permuter-false-positive"

    # Frame-size: prologue/epilogue ops with r1
    t = target_text.lstrip()
    b = base_text.lstrip()
    for op in ("stwu", "stmw", "lmw"):
        if (t.startswith(op) and "r1" in target_text) or (b.startswith(op) and "r1" in base_text):
            return "frame-size"

    # Stack-offset: r1-based load/store with different immediate
    if "r1" in target_text and "r1" in base_text:
        def strip_r1_imm(s: str) -> str:
            return re.sub(r"-?0x[0-9a-fA-F]+\(r1\)", "(r1)", s)
        if strip_r1_imm(target_text) == strip_r1_imm(base_text) and target_text != base_text:
            return "stack-offset"

    # Numerical-offset that wasn't r1-based — usually reloc-derived
    if any(m in target_text for m in _RELOC_MARKERS) or any(m in base_text for m in _RELOC_MARKERS):
        cls = _classify_mismatch(target_text, base_text)
        if cls == "numerical-offset":
            return "permuter-false-positive"
    else:
        def imm_skeleton(s: str) -> str:
            return re.sub(r"0x[0-9a-fA-F]+", "IMM", s)
        if imm_skeleton(target_text) == imm_skeleton(base_text) and target_text != base_text:
            return "permuter-false-positive"

    # Register-allocation: same instruction skeleton, different reg numbers
    def reg_skeleton(s: str) -> str:
        return re.sub(r"\br(?:[0-9]|1[0-9]|2[0-9]|3[01])\b", "rN", s)
    if reg_skeleton(target_text) == reg_skeleton(base_text) and target_text != base_text:
        return "regalloc"

    return "real"


def _get_diff_summary(func: str, build: bool = True) -> dict:
    """Run objdiff for `func` and return a summary dict.

    Result keys: strict_pct, fuzzy_pct, mismatches (list of (kind, target, base)),
    c_file, rel_target, rel_base. On error returns dict with 'error' key.
    """
    import json as _json
    try:
        c_file = find_c_file(func)
    except SystemExit as e:
        return {"error": str(e), "c_file": None}
    rel_c = rel(c_file)
    rel_base = Path("build-linux") / "GALE01" / "src" / rel_c.relative_to("src").with_suffix(".o")
    rel_target = Path("build-linux") / "GALE01" / "obj" / rel_c.relative_to("src").with_suffix(".o")
    if build:
        rc = wsl_ninja(rel_base.as_posix()).returncode
        if rc != 0:
            return {"error": f"build failed (exit {rc})", "c_file": c_file}
    if not (ROOT / rel_base).exists():
        return {"error": f"base object missing: {rel_base}", "c_file": c_file}
    if not (ROOT / rel_target).exists():
        return {"error": f"target object missing: {rel_target}", "c_file": c_file}

    proc = subprocess.run(
        [str(OBJDIFF_CLI), "diff", "-1", str(rel_target), "-2", str(rel_base),
         func, "--format", "json", "-o", "-"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return {"error": f"objdiff: {proc.stderr.strip()}", "c_file": c_file}
    data = _json.loads(proc.stdout)
    target_sym = next((s for s in data.get("left", {}).get("symbols", []) if s.get("name") == func), None)
    base_sym = next((s for s in data.get("right", {}).get("symbols", []) if s.get("name") == func), None)
    if target_sym is None:
        return {"error": f"function {func} not in target object", "c_file": c_file}
    strict_pct = target_sym.get("match_percent")
    if strict_pct is None and base_sym is not None:
        strict_pct = base_sym.get("match_percent")

    fuzzy_pct = _current_fuzzy_pct(func)

    target_ins = target_sym.get("instructions") or []
    base_ins = (base_sym.get("instructions") if base_sym else []) or []
    mismatches = []
    for t, b in zip(target_ins, base_ins):
        kind = t.get("diff_kind", "NONE")
        if kind in ("NONE", "EQUAL"):
            continue
        text_t = t.get("instruction", {}).get("formatted", "?")
        text_b = b.get("instruction", {}).get("formatted", "?")
        mismatches.append((kind, text_t, text_b))

    return {
        "strict_pct": strict_pct, "fuzzy_pct": fuzzy_pct,
        "mismatches": mismatches, "c_file": c_file,
        "rel_target": rel_target, "rel_base": rel_base,
    }


def _sweep_stale_ninja_locks() -> int:
    """Best-effort cleanup of stale ninja-slot locks (dead pids).

    Run at the start of subagent-facing commands so a crashed permute.py
    doesn't leave a slot blocked for up to 30 min between the next
    acquire attempt.
    """
    if not _NINJA_LOCK_DIR.is_dir():
        return 0
    cleared = 0
    for lock in _NINJA_LOCK_DIR.glob("slot-*.pid"):
        try:
            content = lock.read_text(encoding="utf-8", errors="replace").strip()
            holder_pid = int(content) if content.isdigit() else 0
            if holder_pid > 0 and not _is_pid_alive(holder_pid):
                lock.unlink(missing_ok=True)
                cleared += 1
        except (OSError, ValueError):
            pass
    return cleared


def cmd_brief_compact(args: argparse.Namespace) -> None:
    """Emit a compact diagnostic for `func` (~3K of text vs prep's 25K).

    Outputs:
      - target/file/match status
      - mismatch classifier summary
      - top 'real' instruction-level mismatches
      - TU-stuck warning if 2+ siblings logged stuck
      - prior diagnosis line
      - recommended action + canned log-stuck command if applicable
      - function source body

    Cached at build-linux/briefs/<func>.txt, invalidated on .c or .o mtime change.
    """
    cleared = _sweep_stale_ninja_locks()
    if cleared:
        print(f"[brief] cleared {cleared} stale ninja-slot lock(s)", file=sys.stderr)
    func = args.func

    try:
        c_file = find_c_file(func)
    except SystemExit as e:
        print(f"target:   {func}\nERROR: {e}")
        return
    rel_c = rel(c_file)
    rel_target = Path("build-linux") / "GALE01" / "obj" / rel_c.relative_to("src").with_suffix(".o")

    cache_path = _BRIEF_CACHE_DIR / f"{func}.txt"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.no_cache and cache_path.exists():
        try:
            cache_mtime = cache_path.stat().st_mtime
            c_mtime = c_file.stat().st_mtime
            o_path = ROOT / rel_target
            o_mtime = o_path.stat().st_mtime if o_path.exists() else 0
            if cache_mtime >= max(c_mtime, o_mtime):
                sys.stdout.write(cache_path.read_text(encoding="utf-8"))
                return
        except OSError:
            pass

    summary = _get_diff_summary(func, build=not args.no_build)
    if "error" in summary:
        msg = f"target:   {func}\nERROR: {summary['error']}\n"
        sys.stdout.write(msg)
        return

    fuzzy = summary["fuzzy_pct"]
    strict = summary["strict_pct"]

    # Already-matched short-circuit
    if fuzzy == 100.0 or (fuzzy is None and strict == 100.0):
        out = (
            f"target:   {func}\n"
            f"file:     {rel(c_file).as_posix()}\n"
            f"status:   ALREADY MATCHED — skip dispatch.\n"
            f"  fuzzy={fuzzy}  strict={strict}\n"
        )
        sys.stdout.write(out)
        cache_path.write_text(out, encoding="utf-8")
        return

    classes: dict[str, int] = {}
    real_examples: list[tuple[str, str]] = []
    for _kind, t, b in summary["mismatches"]:
        cls = _classify_brief_mismatch(t, b)
        classes[cls] = classes.get(cls, 0) + 1
        if cls == "real" and len(real_examples) < 3:
            real_examples.append((t, b))

    total = sum(classes.values())
    fp = classes.get("permuter-false-positive", 0)
    real = classes.get("real", 0)
    regalloc = classes.get("regalloc", 0)
    frame_local = classes.get("frame-size", 0) + classes.get("stack-offset", 0)

    notes = _parse_notes()
    sym_cache = _load_or_build_symbol_cache()
    tu_stuck_count: dict[str, int] = {}
    for nfunc in notes:
        tu_path = sym_cache.get(nfunc)
        if tu_path:
            tu_stuck_count[tu_path] = tu_stuck_count.get(tu_path, 0) + 1
    cur_tu = sym_cache.get(func, str(rel_c))
    tu_stucks = tu_stuck_count.get(cur_tu, 0)
    direct_note = notes.get(func)

    # Decide recommendation
    rec_tags: list[str] = []
    if total == 0:
        recommendation = "match-attempt (no mismatches detected — re-check)"
    elif fp == total:
        recommendation = "log-stuck-immediately"
        rec_tags = ["permuter-false-positive"]
    elif tu_stucks >= 2 and (fp + frame_local) > real:
        recommendation = "log-stuck-immediately"
        rec_tags = ["permuter-false-positive", "tu-wide-data"] if fp else ["frame-size", "tu-wide-data"]
    elif fp == 0 and (regalloc + real) > 0 and total <= 8:
        recommendation = "permuter-territory (try --auto-permute --cluster after manual attempts)"
    elif fuzzy is not None and fuzzy >= 99.95 and total <= 3:
        recommendation = "match-attempt (high-quality near-miss)"
    else:
        recommendation = "match-attempt"

    body = _read_function_body(c_file, func)
    if len(body) > 4000:
        body = body[:4000] + "\n  ... (truncated)\n"

    lines: list[str] = []
    lines.append(f"target:   {func}")
    lines.append(f"file:     {rel(c_file).as_posix()}")
    if fuzzy is not None:
        lines.append(f"match:    fuzzy={fuzzy}%  strict={strict}%")
    else:
        lines.append(f"match:    strict={strict}%  (fuzzy unavailable — report.json stale)")

    lines.append("")
    lines.append(f"# diff classification ({total} mismatches):")
    for cname in ("permuter-false-positive", "frame-size", "stack-offset", "regalloc", "real"):
        if cname in classes:
            lines.append(f"  {classes[cname]:3d}  {cname}")

    if real_examples:
        lines.append("")
        lines.append("# top 'real' instruction-level mismatches:")
        for t, b in real_examples:
            lines.append(f"  target: {t}")
            lines.append(f"  base:   {b}")

    if tu_stucks >= 2:
        lines.append("")
        lines.append(f"# WARNING: TU '{cur_tu}' has {tu_stucks} logged stuck siblings — likely structural blocker.")

    if direct_note:
        lines.append("")
        lines.append(f"# prior diagnosis for {func}:")
        for bl in direct_note["body"].splitlines()[1:]:
            if bl.strip() and not bl.startswith("**"):
                lines.append(f"  {bl[:200]}")
                break
        lines.append(f"  tags: {', '.join(sorted(direct_note['tags']))}")

    lines.append("")
    lines.append(f"# recommended action: {recommendation}")

    if recommendation.startswith("match-attempt"):
        lines.append("")
        lines.append("# STOP CRITERIA (don't burn cycles on failed variants):")
        lines.append("# - After EACH variant: re-run `permute.py diff <func>` and check the")
        lines.append("#   strict mismatch count (e.g. '5 mismatches').")
        lines.append("# - If mismatch count DID NOT DROP vs baseline: variant is wrong direction.")
        lines.append("#   Revert immediately. Do NOT tweak the same variant — same shape won't")
        lines.append("#   suddenly work. Move to your second variant or log-stuck.")
        lines.append("# - If 2 variants attempted with no improvement: `log-stuck` and exit.")
        lines.append("#   Mama will revisit later with new TU context. Better to churn than spin.")
        lines.append("# - Total budget: ~5 min wall-clock for match-attempt. If you're past that")
        lines.append("#   without reducing mismatches, stop.")

    if recommendation.startswith("log-stuck-immediately"):
        tags_str = ",".join(rec_tags) if rec_tags else "permuter-false-positive"
        cls_summary = " + ".join(f"{n} {c}" for c, n in sorted(classes.items(), key=lambda x: -x[1]))
        diag = f"{total} mismatches: {cls_summary}."
        lines.append("# canned command:")
        lines.append(
            f"  python tools/permute.py log-stuck {func} "
            f"--tags={tags_str} "
            f"--diagnosis=\"{diag}\""
        )

    lines.append("")
    lines.append("# function source:")
    lines.append(body if body else "(could not extract function body from .c)")

    out = "\n".join(lines) + "\n"
    sys.stdout.write(out)
    cache_path.write_text(out, encoding="utf-8")
    _log_event(
        "brief",
        func=func, recommendation=recommendation,
        fuzzy=fuzzy, strict=strict, total_mismatches=total,
        classes=classes, tu_stucks=tu_stucks,
    )


def cmd_events(args: argparse.Namespace) -> None:
    """Aggregate the swarm event log into per-target lifecycles + summary stats.

    Schema of build-linux/swarm-events.jsonl:
      {ts, event: 'brief'|'match'|'stuck', func, ...details}

    For each target with a brief, computes time-to-outcome (brief -> match|stuck),
    then groups by recommendation to show which classifier verdicts pay off.
    """
    import json as _json
    import time as _time
    from collections import defaultdict

    if not _SWARM_EVENT_LOG.exists():
        print(f"no event log at {_SWARM_EVENT_LOG}")
        return

    events: list[dict] = []
    with _SWARM_EVENT_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(_json.loads(line))
            except _json.JSONDecodeError:
                continue

    # Per-func lifecycle: brief, then match or stuck
    by_func: dict[str, dict] = defaultdict(dict)
    for e in events:
        func = e.get("func")
        if not func:
            continue
        et = e["event"]
        if et == "brief":
            by_func[func]["brief"] = e
        elif et == "match":
            by_func[func]["match"] = e
        elif et == "stuck":
            by_func[func]["stuck"] = e

    now = _time.time()
    cutoff = now - (args.since_hours * 3600) if args.since_hours else 0
    rec_outcomes: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rec_durations: dict[str, list[float]] = defaultdict(list)
    untouched_briefs: dict[str, int] = defaultdict(int)
    matches: list[tuple[str, str, float]] = []  # (func, recommendation, brief->match seconds)

    for func, lc in by_func.items():
        brief = lc.get("brief")
        if not brief or brief["ts"] < cutoff:
            continue
        rec = brief.get("recommendation", "?").split(" ")[0]
        if "match" in lc:
            dur = lc["match"]["ts"] - brief["ts"]
            rec_outcomes[rec]["matched"] += 1
            rec_durations[rec].append(dur)
            matches.append((func, rec, dur))
        elif "stuck" in lc:
            dur = lc["stuck"]["ts"] - brief["ts"]
            rec_outcomes[rec]["stuck"] += 1
            rec_durations[rec].append(dur)
        else:
            untouched_briefs[rec] += 1

    print(f"# Swarm event analysis (last {args.since_hours}h)")
    print()
    print("Per recommendation:")
    print(f"  {'recommendation':28s}  {'matched':>8s}  {'stuck':>6s}  {'open':>6s}  {'avg_min':>8s}")
    for rec in sorted(set(list(rec_outcomes.keys()) + list(untouched_briefs.keys()))):
        m = rec_outcomes[rec]["matched"]
        s = rec_outcomes[rec]["stuck"]
        o = untouched_briefs.get(rec, 0)
        durs = rec_durations[rec]
        avg_min = (sum(durs) / len(durs) / 60) if durs else 0
        print(f"  {rec:28s}  {m:>8d}  {s:>6d}  {o:>6d}  {avg_min:>8.1f}")

    if matches:
        print()
        print(f"Recent matches ({len(matches)}):")
        matches.sort(key=lambda x: -x[2])
        for func, rec, dur in matches[:15]:
            print(f"  {dur/60:>6.1f}m  {rec:24s}  {func}")


def _recent_matched_funcs(limit: int = 100) -> list[str]:
    """Names of functions matched in the last N commits (parsed from 'Match X' subjects)."""
    proc = subprocess.run(
        ["git", "log", f"-n{limit}", "--pretty=format:%s"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return []
    out = []
    for line in proc.stdout.splitlines():
        m = re.match(r"^Match\s+([A-Za-z_][A-Za-z0-9_]*)", line)
        if m:
            out.append(m.group(1))
    return out


def cmd_classify(args: argparse.Namespace) -> None:
    """Recommend a tier for working on <func>: skip / cluster-only / haiku / sonnet / opus.

    Looks at:
    - decomp-notes structural-blocker tags → skip
    - mismatch breakdown (reloc-symbol vs instruction) → skip / cluster-only
    - fuzzy %, mismatch count, recent-similar matches → haiku / sonnet / opus

    Mama Claude reads the recommendation and dispatches accordingly. The
    point is to skip the easy cases (cluster-only) and tier-down the
    pattern-transfer cases (haiku) without burning Sonnet tokens.
    """
    import json

    func = args.func
    notes = _parse_notes()
    BLOCKER_TAGS = {"permuter-false-positive", "tu-data-osreport",
                    "tu-wide-data", "cross-tu-globals", "data-symbols-missing"}

    # 1) Skip if known blocker
    nentry = notes.get(func)
    if nentry and (nentry["tags"] & BLOCKER_TAGS):
        blockers = ", ".join(sorted(nentry["tags"] & BLOCKER_TAGS))
        print(f"tier: skip")
        print(f"reason: in decomp-notes with structural-blocker tag(s): {blockers}")
        print(f"action: don't dispatch. The fix needs TU-layout work, not function-body changes.")
        return

    # 2) Get current diff state
    try:
        c_file = find_c_file(func)
    except SystemExit as e:
        print(f"tier: skip")
        print(f"reason: cannot locate source file ({e})")
        return

    rel_base = Path("build-linux") / "GALE01" / "src" / rel(c_file).relative_to("src").with_suffix(".o")
    rel_target = Path("build-linux") / "GALE01" / "obj" / rel(c_file).relative_to("src").with_suffix(".o")

    # Build base + report.json so the diff and fuzzy% are current
    if not args.skip_build:
        rc = wsl_ninja(f"{rel_base.as_posix()} build-linux/GALE01/report.json").returncode
        if rc != 0:
            sys.exit(f"build failed (exit {rc})")

    fuzzy = _current_fuzzy_pct(func)
    if fuzzy is None:
        print(f"tier: skip")
        print(f"reason: function not in report.json (untouched? — needs full decomp from scratch)")
        return
    if fuzzy >= 100.0:
        print(f"tier: skip")
        print(f"reason: already matched (fuzzy=100.0%)")
        return

    proc = subprocess.run(
        [str(OBJDIFF_CLI), "diff", "-1", str(rel_target), "-2", str(rel_base),
         func, "--format", "json", "-o", "-"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"objdiff failed: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    target_sym = next((s for s in data.get("left", {}).get("symbols", []) if s.get("name") == func), None)
    base_sym = next((s for s in data.get("right", {}).get("symbols", []) if s.get("name") == func), None)

    if target_sym is None:
        print(f"tier: skip")
        print(f"reason: function not in target object")
        return
    if base_sym is None:
        print(f"tier: opus")
        print(f"reason: function not yet in base — needs full decomp from scratch (fuzzy={fuzzy:g}%)")
        print(f"action: dispatch Opus subagent with prep --m2c --similar 5 --examples 3")
        return

    target_ins = target_sym.get("instructions") or []
    base_ins = base_sym.get("instructions") or []
    reloc_count = 0
    offset_count = 0
    instr_count = 0
    for t, b in zip(target_ins, base_ins):
        if t.get("diff_kind", "NONE") in ("NONE", "EQUAL"):
            continue
        t_text = t.get("instruction", {}).get("formatted", "")
        b_text = b.get("instruction", {}).get("formatted", "")
        kind = _classify_mismatch(t_text, b_text)
        if kind == "reloc-symbol":
            reloc_count += 1
        elif kind == "numerical-offset":
            offset_count += 1
        else:
            instr_count += 1
    size_diff = abs(len(target_ins) - len(base_ins))
    instr_count += size_diff  # treat insertions/deletions as instruction-level
    # Reloc-derived = explicit reloc-symbol + numerical-offset consequences.
    # If there's at least one true reloc-symbol mismatch, the offset diffs
    # are almost always consequences of the same anchor problem.
    reloc_derived = reloc_count + (offset_count if reloc_count > 0 else 0)
    # If no reloc-symbol but there are offset-only diffs, treat them as
    # instruction-level (could be real frame-size or struct-offset noise).
    if reloc_count == 0:
        instr_count += offset_count
    total = reloc_derived + instr_count

    # 3) Reloc-derived dominated → TU-layout blocker
    if reloc_count >= 1 and instr_count == 0:
        print(f"tier: skip")
        print(f"reason: {reloc_count} reloc-symbol + {offset_count} consequent offset mismatches, 0 instruction — TU-layout blocker")
        print(f"action: don't dispatch permuter (false-positive class). Subagent should run log-stuck and move on.")
        return

    # 4) Pure-instruction diff (regalloc/scheduling, no reloc-derived) → cluster-only.
    # Threshold of 15 covers the regalloc cases observed in batches; above that
    # a subagent might find a structural simplification.
    if total <= 15 and reloc_derived == 0 and instr_count == total:
        print(f"tier: cluster-only")
        print(f"reason: {total} instruction mismatches (all DIFF_ARG/regalloc territory, no reloc diffs)")
        print(f"action: python tools/permute.py diff {func} --auto-permute --cluster")
        return

    # 5) Haiku tier: 99%+ fuzzy, small diff, similar recent match exists
    if fuzzy >= 99.0 and total <= 8:
        # Look for embedding-similar functions that were matched recently
        asm_path = BUILD_LINUX / f"{func}.s"
        recent = set(_recent_matched_funcs(limit=80))
        similar_recent: list[str] = []
        if asm_path.exists() and recent:
            for s in find_similar_via_embeddings(asm_path, n=10, exclude=func):
                if s in recent:
                    similar_recent.append(s)
        if similar_recent:
            print(f"tier: haiku")
            print(f"reason: fuzzy={fuzzy:g}%, {total} mismatches ({reloc_count} reloc + {offset_count} reloc-derived + {instr_count} instr), pattern likely from recent match {similar_recent[0]}")
            print(f"action: dispatch Haiku — brief with 'apply pattern from commit matching {similar_recent[0]}', reinforce commit-match guard")
            return

    # 6) Sonnet for novel near-misses
    if fuzzy >= 95.0:
        print(f"tier: sonnet")
        print(f"reason: fuzzy={fuzzy:g}%, {total} mismatches ({reloc_count} reloc + {offset_count} reloc-derived + {instr_count} instr), no clear pattern transfer")
        print(f"action: dispatch Sonnet with standard subagent prompt + log-stuck protocol")
        return

    # 7) Opus territory
    print(f"tier: opus")
    print(f"reason: fuzzy={fuzzy:g}%, {total} mismatches — significant structural work")
    print(f"action: mama Claude should review first; dispatch Opus subagent if novel structural diagnosis is needed")


def cmd_dispatch(args: argparse.Namespace) -> None:
    """Classify each function and AUTO-HANDLE skip / cluster-only.

    For skip / cluster-only / matched, takes the action directly (no
    subagent token spend). For haiku / sonnet / opus, prints a structured
    list at the end so mama Claude knows which functions still need a
    subagent dispatch and which model.

    This is the orchestration layer — call it on a batch of candidates
    from `backlog` or `picker` and it filters out the work that doesn't
    need an LLM at all.
    """
    import json
    import io
    import contextlib

    funcs = args.funcs
    if not funcs:
        sys.exit("provide one or more function names")

    # Build all referenced .o files + report.json once so per-classify
    # runs hit the cache. Group by source file.
    rel_objs: list[str] = []
    for f in funcs:
        try:
            cf = find_c_file(f)
            rel_objs.append((Path("build-linux") / "GALE01" / "src" / rel(cf).relative_to("src").with_suffix(".o")).as_posix())
        except SystemExit:
            pass
    if rel_objs:
        targets = " ".join(set(rel_objs)) + " build-linux/GALE01/report.json"
        print(f"[dispatch] building {len(set(rel_objs))} unique objects + report.json…")
        rc = wsl_ninja(targets).returncode
        if rc != 0:
            sys.exit(f"build failed (exit {rc})")

    fired_cluster: list[str] = []
    skipped: list[tuple[str, str]] = []
    matched: list[str] = []
    for_haiku: list[tuple[str, str]] = []  # (func, reason)
    for_sonnet: list[tuple[str, str]] = []
    for_opus: list[tuple[str, str]] = []

    for func in funcs:
        # Capture classify output to parse the tier
        buf = io.StringIO()
        old_argv = sys.argv
        try:
            class _Ns:
                pass
            ns = _Ns()
            ns.func = func
            ns.skip_build = True  # we already built above
            with contextlib.redirect_stdout(buf):
                cmd_classify(ns)
        except SystemExit:
            pass
        out = buf.getvalue()
        first_line = next((l for l in out.splitlines() if l.startswith("tier:")), "tier: unknown")
        tier = first_line.split(":", 1)[1].strip()
        reason_line = next((l for l in out.splitlines() if l.startswith("reason:")), "")
        reason = reason_line.split(":", 1)[1].strip() if reason_line else ""

        if tier == "skip":
            skipped.append((func, reason))
            print(f"  [skip]    {func}  ({reason[:80]})")
        elif tier == "cluster-only":
            # Fire the permuter directly
            try:
                c_file = find_c_file(func)
            except SystemExit as e:
                print(f"  [skip]    {func}  (no source: {e})")
                continue
            # Don't double-fire if a permuter already exists
            active = {f for f, _, _ in list_active_permuters()}
            if func in active:
                print(f"  [active]  {func}  (already running)")
                continue
            print(f"  [cluster] {func}  ({reason[:80]})")
            _launch_permuter_background(c_file, func, cluster=True)
            fired_cluster.append(func)
        elif tier == "haiku":
            for_haiku.append((func, reason))
            print(f"  [haiku]   {func}  ({reason[:80]})")
        elif tier == "sonnet":
            for_sonnet.append((func, reason))
            print(f"  [sonnet]  {func}  ({reason[:80]})")
        elif tier == "opus":
            for_opus.append((func, reason))
            print(f"  [opus]    {func}  ({reason[:80]})")
        else:
            # "skip" reasons that came from already-matched / unknown
            if "already matched" in reason:
                matched.append(func)
                print(f"  [matched] {func}  (fuzzy=100, no work needed)")
            else:
                skipped.append((func, reason))
                print(f"  [skip]    {func}  ({reason[:80]})")

    print()
    print("=" * 60)
    print(f"summary: {len(fired_cluster)} cluster fired, {len(skipped)} skipped, "
          f"{len(matched)} already matched, "
          f"{len(for_haiku)} haiku-tier, {len(for_sonnet)} sonnet-tier, {len(for_opus)} opus-tier")

    if for_haiku or for_sonnet or for_opus:
        print()
        print("=== NEEDS SUBAGENT DISPATCH (mama Claude action) ===")
        for func, reason in for_haiku:
            print(f"  HAIKU   {func}  — {reason}")
        for func, reason in for_sonnet:
            print(f"  SONNET  {func}  — {reason}")
        for func, reason in for_opus:
            print(f"  OPUS    {func}  — {reason}")


def cmd_brief(args: argparse.Namespace) -> None:
    """Emit a complete subagent prompt for working on <func>.

    Includes:
    - target metadata (file path, current fuzzy %)
    - prior decomp-notes entry for this function (if any)
    - decomp-notes entries for embedding-similar functions (pattern hints)
    - the standard protocol steps (commit-match, log-stuck, false-positive rule)
    - hard-stop rules (no destructive git ops, no raw commits)

    Mama Claude calls this and uses the output as the subagent prompt body.
    Auto-injects what `notes <func>` would surface, so the subagent doesn't
    have to fetch it themselves and so prior diagnoses + sibling patterns
    actually inform the next attempt.
    """
    func = args.func

    # Resolve source file
    try:
        c_file = find_c_file(func)
        c_rel = rel(c_file).as_posix()
    except SystemExit:
        c_rel = "<unknown source — locate via find_c_file>"

    fuzzy = _current_fuzzy_pct(func)
    fuzzy_str = f"{fuzzy:g}%" if fuzzy is not None else "(unknown — run prep first)"

    # Direct notes entry
    notes = _parse_notes()
    direct_entry = notes.get(func)

    # Embedding-similar lookups (slow: load jina model). Skip unless --similar.
    similar_with_notes: list[tuple[str, dict]] = []
    similar_recent_matches: list[str] = []
    asm_path = BUILD_LINUX / f"{func}.s"
    if args.similar and asm_path.exists():
        recent = set(_recent_matched_funcs(limit=80))
        for s in find_similar_via_embeddings(asm_path, n=15, exclude=func):
            if s in notes and (not direct_entry or notes[s]["header"] != direct_entry["header"]):
                if len(similar_with_notes) < 3:
                    similar_with_notes.append((s, notes[s]))
            if s in recent and len(similar_recent_matches) < 3:
                similar_recent_matches.append(s)
            if len(similar_with_notes) >= 3 and len(similar_recent_matches) >= 3:
                break

    # Build the prompt
    print(f"Subagent in Melee decomp swarm. Target: `{func}` in `{c_rel}`. Current fuzzy: {fuzzy_str}.")
    print()

    if direct_entry:
        print(f"### PRIOR DIAGNOSIS for {func} (from decomp-notes.md)")
        print(f"Read this carefully — past attempts and what's been ruled out:")
        print()
        print(direct_entry["body"].strip())
        print()

    if similar_with_notes:
        print(f"### SIMILAR-FUNCTION DIAGNOSES (by ASM embedding, may share blocker pattern)")
        for name, entry in similar_with_notes:
            print()
            print(entry["body"].strip())
        print()

    if similar_recent_matches:
        print(f"### RECENTLY MATCHED SIBLINGS (pattern-transfer hints)")
        print(f"These embedding-similar functions were matched in the last 80 commits.")
        print(f"Run `git show <SHA> -- <file>` for each to see what fix worked:")
        for s in similar_recent_matches:
            print(f"- {s}")
        print()

    print("### PROTOCOL (CLAUDE.md swarm flow)")
    print(f"1. `python tools/permute.py prep {func} -q --m2c --similar 3 --examples 2`")
    print(f"2. Try at most **2** source-shape variants. Don't re-try anything ruled out above.")
    print(f"3. If 100%: `python tools/permute.py commit-match {func}` — verifies fuzzy=100% in BOTH objdiff AND report.json. NEVER raw `git commit`. If a `.h` change is needed, REPORT the path; mama lands it in a follow-up.")
    print(f"4. If permuter-territory near-miss (regalloc/scheduling/expression-order, no reloc-symbol diffs): `python tools/permute.py diff {func} --auto-permute --cluster`")
    print(f"5. If stuck: MUST call `python tools/permute.py log-stuck {func} --tags=… --diagnosis=\"…\" --tried=\"…\" --likely-fix=\"…\"` BEFORE reporting back. The diagnosis is auto-indexed by ASM embedding for future attempts.")
    print()
    print("### CRITICAL FALSE-POSITIVE RULE")
    print(f"If the diff is dominated by `@ha`/`@l` reloc-symbol mismatches (BSS-anchor `bss.0+0xN` vs `lbl_X+0`, sdata2 `@N@sda21` vs named global, `.data.0+0xN` vs `lbl_X`), DO NOT dispatch the permuter — its scorer treats those as equivalent (post-link bytes match) but `report.json fuzzy` does not. Tag as `permuter-false-positive` + the layout class and `log-stuck`.")
    print()
    print("### HARD-STOP RULES")
    print(f"- NEVER raw `git commit` for a Match. ONLY `commit-match` is authorized.")
    print(f"- NEVER `git stash` (push or pop), `git restore`, `git checkout -- <file>`, `git reset --hard`, `git clean -f`, or `rm` on tracked files. The working tree is shared with mama and other subagents — those clobber other agents' uncommitted work.")
    print(f"- NEVER edit files outside `src/melee/`, `src/sysdolphin/`, or `{c_rel}`. No tool changes, no .gitignore edits, no header edits unless they're the immediate dependency of your match.")
    print(f"- NEVER kill a permuter you didn't launch.")
    print(f"- If `git status --short` shows unfamiliar changes, leave them alone.")
    print()
    print("### REPORT FORMAT")
    print("Report one of: `matched(SHA)` / `permuter-launched(pid)` / `stuck(logged via log-stuck)` / `false-positive(logged)`. Keep it concise.")


def cmd_outputs(args: argparse.Namespace) -> None:
    """Show per-function permuter zero-score outputs with their diffs vs base.c.

    Complementary to `harvest` (which gives a project-wide status). Use this
    when `harvest` flagged a HIT 100% function and you need to inspect the
    candidate ports to decide which one to translate to src/.

    Permuter saves `nonmatchings/<func>/output-0-N/` whenever a mutation
    scores 0 by ITS metric. Permuter's scorer is looser than `report.json`'s
    fuzzy_match — many "score 0" outputs are false positives that don't
    yield 100% fuzzy when ported (preprocessed-source mutation ≠ macro-
    expanded original). This command lets you eyeball the diff before
    spending time on the port.
    """
    func = args.func
    nm_dir = ROOT / "nonmatchings" / func
    if not nm_dir.is_dir():
        sys.exit(f"no nonmatchings dir for {func} — has permuter ever run on it?")

    base_c = nm_dir / "base.c"
    if not base_c.exists():
        sys.exit(f"missing {base_c}")

    outputs = sorted(p for p in nm_dir.iterdir() if p.is_dir() and p.name.startswith("output-0-"))
    if not outputs:
        print(f"no zero-score outputs in {rel(nm_dir).as_posix()}")
        # Show next-best
        all_outs = sorted(p for p in nm_dir.iterdir() if p.is_dir() and p.name.startswith("output-"))
        if all_outs:
            print(f"\n# Next-best outputs (non-zero scores):")
            for p in all_outs[:5]:
                score_file = p / "score.txt"
                score = score_file.read_text().strip() if score_file.exists() else "?"
                print(f"  {p.name}  score={score}")
        return

    print(f"# {len(outputs)} zero-score output(s) for {func}\n")

    import difflib

    base_text = base_c.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    for i, out_dir in enumerate(outputs[: args.limit]):
        src = out_dir / "source.c"
        if not src.exists():
            continue
        cand_text = src.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            base_text, cand_text,
            fromfile=f"base.c",
            tofile=f"{out_dir.name}/source.c",
            n=2,
            lineterm="",
        ))
        # Trim huge diffs
        if len(diff) > 60:
            diff = diff[:60] + [f"  (... {len(diff) - 60} more diff lines)"]

        print(f"## {out_dir.name}")
        if not diff:
            print("  (no diff vs base — output is identical to base.c?)")
        else:
            for line in diff:
                print(line.rstrip())
        print()

    if len(outputs) > args.limit:
        print(f"# (showing first {args.limit} of {len(outputs)} outputs; pass --limit N for more)\n")

    print(f"# Next steps:")
    print(f"#   - Pick a candidate whose diff is minimal + idiomatic")
    print(f"#   - Manually port the change into src/.../<file>.c (note: outputs are PREPROCESSED — macros are expanded)")
    print(f"#   - python tools/permute.py commit-match {func} -m '...'")
    print(f"#   - If commit-match refuses, the permuter score-0 was a false positive (its metric ≠ report.json fuzzy)")


def _tus_differing_from_upstream() -> set[str]:
    """Return the set of TU short-names (e.g. 'melee/gr/grpura') whose .c file
    differs from upstream/master.

    A TU whose source matches upstream byte-for-byte but still doesn't fully
    byte-match in our build either (a) is matched upstream but our build env
    diverges, or (b) is impacted by neighbor-TU layout. Either way, the
    target function offers no source-shape lever for a subagent to pull —
    those are wasted attempts. This filter restricts picker output to TUs
    where there is actually source-side work left to do.
    """
    remote = permute_upstream._upstream_remote()
    if remote is None:
        return set()
    r = subprocess.run(
        ["git", "diff", "--name-only", f"{remote}/master", "--",
         "src/melee/", "src/sysdolphin/"],
        capture_output=True, cwd=ROOT, check=False,
    )
    if r.returncode != 0:
        return set()
    out = r.stdout.decode("utf-8", errors="replace")
    tus: set[str] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("src/") or not line.endswith(".c"):
            continue
        tus.add(line[len("src/"):-len(".c")])
    return tus


def cmd_picker(args: argparse.Namespace) -> None:
    """List undecompiled or in-progress functions sorted by difficulty estimate.

    Difficulty proxy: instruction count primarily, with a small bonus for
    presence of float / jump-table instructions. Uses build-linux/.../report.json
    which is regenerated on every ninja run.
    """
    import json

    report_paths = [
        BUILD_LINUX / "GALE01" / "report.json",
        ROOT / "build" / "GALE01" / "report.json",
    ]
    report_path = next((p for p in report_paths if p.exists()), None)
    if report_path is None:
        sys.exit("no report.json found — run ninja at least once")
    data = json.loads(report_path.read_text())

    differing_tus: Optional[set[str]] = None
    if getattr(args, "source_differs_upstream", False):
        differing_tus = _tus_differing_from_upstream()

    rows: list[tuple[float, dict]] = []
    skipped_no_diff = 0
    for unit in data.get("units", []):
        unit_name = unit.get("name", "")
        unit_short = unit_name.replace("main/", "")
        for fn in unit.get("functions", []) or []:
            pct = fn.get("fuzzy_match_percent", 0.0)
            size_bytes = int(fn.get("size", 0))

            if args.mode == "untouched" and pct >= 99.99:
                continue
            if args.mode == "untouched" and pct > 0.01:
                continue
            if args.mode == "in_progress" and (pct >= 99.99 or pct < 0.01):
                continue
            if args.max_size is not None and size_bytes > args.max_size:
                continue
            if differing_tus is not None and unit_short not in differing_tus:
                skipped_no_diff += 1
                continue

            rows.append((size_bytes, {
                "name": fn.get("name"),
                "size": size_bytes,
                "pct": pct,
                "unit": unit_name,
            }))

    rows.sort(key=lambda r: r[0])

    suffix = ""
    if differing_tus is not None:
        suffix = (f"  (filtered by source-differs-upstream: "
                  f"{len(differing_tus)} TUs differ; {skipped_no_diff} fns skipped)")
    print(f"# {len(rows)} {args.mode} functions (showing first {args.limit}){suffix}")
    print(f"{'instructions':>12}  {'match%':>7}  function name")
    for _, r in rows[: args.limit]:
        ins = r["size"] // 4
        unit_short = r["unit"].replace("main/", "")
        print(f"{ins:>12d}  {r['pct']:>6.1f}%  {r['name']}  ({unit_short})")


def _load_report_json() -> dict:
    import json

    report_paths = [
        BUILD_LINUX / "GALE01" / "report.json",
        ROOT / "build" / "GALE01" / "report.json",
    ]
    report_path = next((p for p in report_paths if p.exists()), None)
    if report_path is None:
        sys.exit("no report.json found - run ninja at least once")
    return json.loads(report_path.read_text())


def _objdiff_symbols(func: str, c_file: Path) -> tuple[dict | None, dict | None] | None:
    import json

    rel_c = rel(c_file)
    try:
        obj_rel = rel_c.relative_to("src").with_suffix(".o")
    except ValueError:
        return None
    rel_base = Path("build-linux") / "GALE01" / "src" / obj_rel
    rel_target = Path("build-linux") / "GALE01" / "obj" / obj_rel
    if not (ROOT / rel_base).exists() or not (ROOT / rel_target).exists():
        return None

    proc = subprocess.run(
        [
            str(OBJDIFF_CLI), "diff",
            "-1", str(rel_target),
            "-2", str(rel_base),
            func,
            "--format", "json",
            "-o", "-",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    data = json.loads(proc.stdout)
    target_syms = data.get("left", {}).get("symbols") or []
    base_syms = data.get("right", {}).get("symbols") or []
    target_sym = next((s for s in target_syms if s.get("name") == func), None)
    base_sym = next((s for s in base_syms if s.get("name") == func), None)
    return target_sym, base_sym


def _ins_text(ins: dict) -> str:
    return ins.get("instruction", {}).get("formatted", "") or ""


def _has_lha_extsh_signature(target_sym: dict, base_sym: dict) -> tuple[int, bool]:
    """Detect the cheap-win pattern where base loads a signed halfword into r0
    and then emits an extra extsh r3,r0 before a call, while target loads the
    same value directly into r3.
    """
    target_ins = target_sym.get("instructions") or []
    base_ins = base_sym.get("instructions") or []
    lha_pairs = 0
    has_extsh_insert = False
    for t, b in zip(target_ins, base_ins):
        text_t = _ins_text(t)
        text_b = _ins_text(b)
        if text_t.startswith("lha r3,") and text_b.startswith("lha r0,"):
            lha_pairs += 1
        if text_b == "extsh r3, r0":
            has_extsh_insert = True
    return lha_pairs, has_extsh_insert


def cmd_sweep_lha_extsh(args: argparse.Namespace) -> None:
    """Find near-misses likely fixed by widening an s16 local to s32.

    This uses existing built objects and objdiff JSON; it does not rebuild.
    """
    data = _load_report_json()
    notes = _parse_notes()
    candidates: list[dict] = []
    for unit in data.get("units", []):
        unit_name = unit.get("name", "")
        for fn in unit.get("functions", []) or []:
            name = fn.get("name")
            if not name:
                continue
            pct = fn.get("fuzzy_match_percent", 0.0) or 0.0
            if pct >= args.max_fuzzy or pct < args.min_fuzzy:
                continue
            size_raw = fn.get("size", 0)
            try:
                size = int(size_raw)
            except (TypeError, ValueError):
                continue
            if args.max_size is not None and size > args.max_size:
                continue
            if not args.include_notes and name in notes:
                continue
            candidates.append({
                "name": name,
                "size": size,
                "pct": pct,
                "unit": unit_name,
            })

    candidates.sort(key=lambda r: (r["size"], -r["pct"]))
    if args.scan_limit is not None:
        candidates = candidates[: args.scan_limit]

    hits: list[tuple[int, dict]] = []
    skipped = 0
    for row in candidates:
        try:
            c_file = find_c_file(row["name"])
        except SystemExit:
            skipped += 1
            continue
        symbols = _objdiff_symbols(row["name"], c_file)
        if symbols is None:
            skipped += 1
            continue
        target_sym, base_sym = symbols
        if target_sym is None or base_sym is None:
            skipped += 1
            continue
        lha_pairs, has_extsh = _has_lha_extsh_signature(target_sym, base_sym)
        if lha_pairs and has_extsh:
            hits.append((lha_pairs, row))

    print(
        f"# scanned {len(candidates)} candidates"
        f" ({skipped} skipped: missing owner/object/objdiff)"
    )
    print(f"# {len(hits)} lha-r0/extsh-r3 candidates")
    print(f"{'pairs':>5}  {'instructions':>12}  {'match%':>7}  function name")
    for pairs, row in hits[: args.limit]:
        unit_short = row["unit"].replace("main/", "")
        print(
            f"{pairs:>5d}  {row['size'] // 4:>12d}  "
            f"{row['pct']:>6.1f}%  {row['name']}  ({unit_short})"
        )


def cmd_check(args: argparse.Namespace) -> None:
    print("[check] ninja…")
    res = wsl_ninja(capture=True)
    out = res.stdout + res.stderr
    sys.stdout.write(res.stdout)
    sys.stderr.write(res.stderr)
    if "main.dol: OK" in out:
        print("\nSHA1 OK")
    elif "FAILED" in out or res.returncode != 0:
        print("\nSHA1 FAILED", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nninja exited {res.returncode}")
        sys.exit(res.returncode)


_CMD_LINE_RX = re.compile(r"^(.*?)(?:\s+'?&&'?\s+.*)?$")


def fix_compile_sh(path: Path) -> None:
    """Strip the trailing `&& transform_dep.py ...` and add the input/output args."""
    text = path.read_text()
    fixed = []
    changed = False
    for line in text.splitlines():
        if "transform_dep" in line and "&&" in line:
            head = re.split(r"\s+'?&&'?\s+", line, maxsplit=1)[0]
            line = f'{head} "$INPUT" -o "$OUTPUT"'
            changed = True
        fixed.append(line)
    if changed:
        # Force LF — script runs in WSL bash and CRLF breaks the shebang
        path.write_bytes(("\n".join(fixed) + "\n").encode())


def cmd_permute(args: argparse.Namespace) -> None:
    func = args.func
    c_file = find_c_file(func)
    asm_path = BUILD_LINUX / f"{func}.s"
    if not asm_path.exists():
        # Run prep automatically
        print(f"[permute] no extracted asm — running prep first")
        asm_path, _ = disasm_and_extract(c_file, func)

    rel_c = rel(c_file).as_posix()
    rel_asm = rel(asm_path).as_posix()

    # Clean up any stale -N collision dirs
    nm_root = ROOT / "nonmatchings"
    nm_root.mkdir(exist_ok=True)

    cmd = (
        'PERMUTER_AS="$(pwd)/build-linux/binutils/powerpc-eabi-as -mgekko -mregnames" '
        "vendor/decomp-permuter/.venv-linux/bin/python vendor/decomp-permuter/import.py "
        f"{rel_c} {rel_asm}"
    )
    print(f"[permute] importing {func}…")
    rc = wsl(cmd).returncode
    if rc != 0:
        sys.exit(f"import.py failed (exit {rc})")

    # Pick the most recently created dir starting with func
    candidates = sorted(
        (p for p in nm_root.iterdir() if p.is_dir() and p.name.startswith(func)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        sys.exit("import.py did not create a nonmatchings dir")
    nm_dir = candidates[0]
    print(f"[permute] dir: {rel(nm_dir).as_posix()}")

    fix_compile_sh(nm_dir / "compile.sh")
    print(f"[permute] fixed compile.sh")

    # Smoke test
    smoke = wsl(
        f'bash {rel(nm_dir / "compile.sh").as_posix()} '
        f'{rel(nm_dir / "base.c").as_posix()} -o /tmp/permute_smoke.o',
        capture=True,
    )
    if smoke.returncode != 0:
        print("[permute] WARNING: smoke compile failed", file=sys.stderr)
        sys.stderr.write(smoke.stderr)
    else:
        print("[permute] smoke compile OK")

    run_cmd = (
        f'wsl -d {WSL_DISTRO} -- bash -lc \'cd {WSL_ROOT} && '
        f'PATH="$(pwd)/build-linux/binutils:$PATH" '
        f"vendor/decomp-permuter/.venv-linux/bin/python vendor/decomp-permuter/permuter.py "
        f'{rel(nm_dir).as_posix()}/ -j 4 --show-errors\''
    )
    print()
    print("To run permuter:")
    print(f"  {run_cmd}")


_PLACEHOLDER_NAME_RX = re.compile(r"^[A-Za-z][A-Za-z0-9_]*?_(?:[0-9A-Fa-f]{8})$|^fn_[0-9A-Fa-f]{8}$")


def _looks_like_placeholder(name: str) -> bool:
    """True if `name` follows the `<prefix>_<8-hex-addr>` convention used for
    not-yet-meaningfully-named functions."""
    return bool(_PLACEHOLDER_NAME_RX.match(name))


def _extract_func_body(c_text: str, func: str) -> Optional[tuple[int, int, str]]:
    """Locate `func`'s definition in c_text and return (start_line, end_line, body).

    Uses brace-depth tracking from the opening `{`. Returns None if the function
    isn't defined in this file (declared-only or absent).
    """
    rx = re.compile(
        r"^[A-Za-z_][\w\s\*]*?\b(" + re.escape(func) + r")\s*\([^;)]*\)\s*\n?\s*\{",
        re.MULTILINE,
    )
    m = rx.search(c_text)
    if not m:
        return None
    start = m.start()
    body_start = c_text.find("{", m.end() - 1)
    if body_start < 0:
        return None
    depth = 0
    i = body_start
    body_end = -1
    while i < len(c_text):
        ch = c_text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                body_end = i + 1
                break
        i += 1
    if body_end < 0:
        return None
    start_line = c_text.count("\n", 0, start) + 1
    end_line = c_text.count("\n", 0, body_end) + 1
    return (start_line, end_line, c_text[start:body_end])


def _list_funcs_in_tu(c_text: str) -> list[str]:
    """Return the list of function names defined in this .c (in source order)."""
    rx = re.compile(
        r"^[A-Za-z_][\w\s\*]*?\b([A-Za-z_]\w*)\s*\([^;)]*\)\s*\n?\s*\{",
        re.MULTILINE,
    )
    seen: list[str] = []
    seen_set: set[str] = set()
    for m in rx.finditer(c_text):
        name = m.group(1)
        if name in seen_set:
            continue
        seen_set.add(name)
        seen.append(name)
    return seen


def _find_callers(
    func: str,
    *,
    max_results: int = 50,
    exclude_def_in: Optional[tuple[Path, int, int]] = None,
) -> list[tuple[str, int, str]]:
    """Grep src/ for call sites of `func`. Returns list of (rel_path, line_no, line_text).

    `exclude_def_in` is (file, start_line, end_line) covering the function's own
    definition — calls to `func` within that range are skipped (covers the
    signature line and any recursion within the body, which we'd want to count
    separately if at all).
    """
    pattern = re.compile(rf"\b{re.escape(func)}\s*\(")
    out: list[tuple[str, int, str]] = []
    excl_path = exclude_def_in[0].resolve() if exclude_def_in else None
    excl_start = exclude_def_in[1] if exclude_def_in else 0
    excl_end = exclude_def_in[2] if exclude_def_in else 0

    for c_file in SRC.rglob("*.c"):
        try:
            text = c_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if func not in text:
            continue
        is_def_file = excl_path is not None and c_file.resolve() == excl_path
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not pattern.search(line):
                continue
            # Skip the function's own definition lines (signature + body lines)
            if is_def_file and excl_start <= line_no <= excl_end:
                continue
            # Skip declarations (end with `;` after the `)`)
            if re.search(rf"\b{re.escape(func)}\s*\([^)]*\)\s*;\s*$", line):
                continue
            out.append((rel(c_file).as_posix(), line_no, line))
            if len(out) >= max_results:
                return out
    return out


def _extract_strings_in_body(body: str) -> list[tuple[str, str]]:
    """Return (kind, content) for each debug-string found in body."""
    found: list[tuple[str, str]] = []
    patterns = [
        ("OSReport",   r'OSReport\s*\(\s*"([^"]*)"'),
        ("OSPanic",    r'OSPanic\s*\([^,]+,\s*[^,]+,\s*"([^"]*)"'),
        ("DevText",    r'DevTextPrint\w*\s*\([^"]*"([^"]*)"'),
        ("HSD_Panic",  r'HSD_Panic\s*\([^,]+,\s*"([^"]*)"'),
        ("printf",     r'\bprintf\s*\(\s*"([^"]*)"'),
        ("fprintf",    r'\bfprintf\s*\(\s*\w+\s*,\s*"([^"]*)"'),
    ]
    for kind, pat in patterns:
        for m in re.finditer(pat, body):
            found.append((kind, m.group(1)))
    return found


def _extract_asserts_in_body(body: str) -> list[str]:
    """Return matched assert calls from the function body (as raw substrings)."""
    found: list[str] = []
    patterns = [
        r"HSD_ASSERT\s*\([^)]*\)",
        r"HSD_ASSERTMSG\s*\([^)]*\)",
        r"MELEE_ASSERT\s*\([^)]*\)",
        r"MELEE_ASSERTMSG\s*\([^)]*\)",
        r"\bOS_ASSERT[A-Z]*\s*\([^)]*\)",
        r"\bASSERT\s*\([^)]*\)",
        r"\bASSERTMSG\s*\([^)]*\)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, body):
            found.append(m.group(0))
    return found


def cmd_propose_naming(args: argparse.Namespace) -> None:
    """Gather citation-grounded evidence for naming a placeholder-named function.

    Outputs structured evidence (asserts, debug strings, callers, naming-convention
    siblings, embedding-similar matched functions) so an agent (or human) can propose
    a name with cited sources. Does NOT itself propose a name — by design, the
    artifact reviewers care about is the evidence trail, not an LLM's claim.
    """
    func = args.func
    c_file = find_c_file(func)
    rel_c = rel(c_file).as_posix()

    try:
        c_text = c_file.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        sys.exit(f"can't read {rel_c}: {e}")

    body_info = _extract_func_body(c_text, func)
    if body_info is None:
        sys.exit(f"could not locate definition of {func} in {rel_c} (still INCLUDE_ASM? declared-only?)")
    start_line, end_line, body = body_info
    n_lines = end_line - start_line + 1

    print(f"# propose-naming: {func}")
    print(f"# file: {rel_c}:{start_line}-{end_line} ({n_lines} lines)")
    print(f"# placeholder: {_looks_like_placeholder(func)}")
    print()

    # 1. Asserts in the body (often contain the function's own name)
    asserts = _extract_asserts_in_body(body)
    print(f"## Asserts in body ({len(asserts)})")
    if asserts:
        for a in asserts:
            marker = ""
            if func in a:
                marker = "  [self-name in assert!]"
            print(f"  {a}{marker}")
    else:
        print("  (none)")
    print()

    # 2. Debug strings (OSReport, panic, etc — often contain function name + role)
    strings = _extract_strings_in_body(body)
    print(f"## Debug strings ({len(strings)})")
    if strings:
        for kind, content in strings:
            marker = "  [self-name!]" if func in content else ""
            print(f"  {kind}: {content!r}{marker}")
    else:
        print("  (none)")
    print()

    # 3. Callers
    callers = _find_callers(func, max_results=40, exclude_def_in=(c_file, start_line, end_line))
    print(f"## Callers in src/ ({len(callers)}{' shown — see --max-callers' if len(callers) >= 40 else ''})")
    if callers:
        for path, line_no, line in callers[:30]:
            print(f"  {path}:{line_no}: {line.strip()[:120]}")
        if len(callers) > 30:
            print(f"  (... {len(callers) - 30} more callers)")
    else:
        print("  (none -- possibly only invoked via function pointer; check StageCallbacks/cb tables)")
    print()

    # 4. Naming convention in the same TU
    same_tu = _list_funcs_in_tu(c_text)
    named = [n for n in same_tu if not _looks_like_placeholder(n) and n != func]
    placeholders = [n for n in same_tu if _looks_like_placeholder(n) and n != func]
    print(f"## Same TU naming ({len(same_tu)} funcs total: {len(named)} named, {len(placeholders)} placeholder)")
    if named:
        # Show prefixes — gives a sense of the file's convention
        prefixes: dict[str, int] = {}
        for n in named:
            pfx = n.split("_", 1)[0] if "_" in n else n
            prefixes[pfx] = prefixes.get(pfx, 0) + 1
        top_prefixes = sorted(prefixes.items(), key=lambda x: -x[1])[:5]
        print(f"  Top prefixes: {', '.join(f'{p}({c})' for p, c in top_prefixes)}")
        print(f"  Sample named funcs:")
        for n in named[:10]:
            print(f"    {n}")
        if len(named) > 10:
            print(f"    (... {len(named) - 10} more)")
    else:
        print("  (no other named funcs in this TU -- naming convention unclear from file alone)")
    print()

    # 5. Similar matched functions via embeddings
    print("## Embedding-similar matched functions")
    try:
        asm_path, _ = disasm_and_extract(c_file, func)
    except SystemExit:
        asm_path = None
    if asm_path is None:
        print("  (couldn't extract asm for embedding lookup)")
    else:
        similar = find_similar_via_embeddings(asm_path, n=10, exclude=func)
        if not similar:
            print("  (no embedding hits -- index missing? run `permute.py index-embeddings`)")
        else:
            for s in similar:
                marker = " [placeholder]" if _looks_like_placeholder(s) else ""
                # Try to locate the file for context
                try:
                    s_file = rel(find_c_file(s)).as_posix()
                except SystemExit:
                    s_file = "?"
                print(f"  {s} -- {s_file}{marker}")
    print()

    # 6. Confidence summary
    self_name_in_strings = any(func in s for _, s in strings)
    self_name_in_asserts = any(func in a for a in asserts)
    if self_name_in_strings or self_name_in_asserts:
        confidence = "HIGH (function name appears in source — direct evidence)"
    elif len(callers) >= 3 and len(named) >= 5:
        confidence = "MEDIUM (multiple callers + same-TU convention to compare against)"
    elif len(callers) >= 1 or len(named) >= 3:
        confidence = "LOW (limited evidence -- propose tentatively or keep placeholder)"
    else:
        confidence = "VERY LOW (no callers, no convention; PREFER keeping placeholder)"

    print(f"## Confidence: {confidence}")
    print()
    print("Next step: review the evidence above and propose a name with citations.")
    print("CONTRIBUTING.md: 'don't name functions you don't understand.' If the evidence")
    print("doesn't directly support a name, keep the placeholder -- that's the correct call.")


def _parse_args_list(args_text: str) -> list[tuple[str, str]]:
    """Parse a C arg list like 'Fighter* fp, s32 idx, void* user' into [(type, name), ...].

    Crude but works for melee's single-line C signatures (no templates, no defaults).
    """
    if not args_text.strip() or args_text.strip() == "void":
        return []
    out: list[tuple[str, str]] = []
    # Split on commas, but only at depth 0 (account for func pointer types like void (*cb)(int))
    depth = 0
    parts: list[str] = []
    cur = ""
    for ch in args_text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    for raw in parts:
        s = raw.strip()
        if not s:
            continue
        # Function pointer: void (*cb)(args)
        m = re.match(r"^(.+?\(\s*\*\s*)(\w+)(\s*\)\s*\([^)]*\))\s*$", s)
        if m:
            out.append((m.group(1) + m.group(3), m.group(2)))
            continue
        # Array: Type name[N]
        m = re.match(r"^(.+?\b)(\w+)(\s*\[[^\]]*\])\s*$", s)
        if m:
            out.append((m.group(1).strip() + m.group(3), m.group(2)))
            continue
        # Plain: Type name (with optional pointer stars)
        m = re.match(r"^(.+?[\s\*])(\w+)\s*$", s)
        if m:
            out.append((m.group(1).strip(), m.group(2)))
            continue
        # Type only (unnamed) — fall through
        out.append((s, ""))
    return out


def _find_accesses_for_arg(body: str, arg_name: str) -> list[tuple[str, str]]:
    """Return access patterns for arg_name in body as [(kind, detail), ...]."""
    if not arg_name:
        return []
    out: list[tuple[str, str]] = []
    name_rx = re.escape(arg_name)
    patterns = [
        ("arrow_field",  rf"\b{name_rx}->(\w+)"),
        ("dot_field",    rf"\b{name_rx}\.(\w+)"),
        ("subscript",    rf"\b{name_rx}\[([^\]]+)\]"),
        ("deref",        rf"\*\s*\b{name_rx}\b"),
        ("addr_of",      rf"&\s*\b{name_rx}\b"),
        ("call_arg",     rf"\b\w+\s*\([^)]*\b{name_rx}\b[^)]*\)"),
        ("assignment",   rf"\b{name_rx}\s*=[^=]"),
        ("compare_null", rf"\b{name_rx}\s*(?:==|!=)\s*NULL"),
    ]
    for kind, pat in patterns:
        for m in re.finditer(pat, body):
            detail = m.group(1) if m.lastindex else m.group(0).strip()
            out.append((kind, detail))
    return out


def _extract_field_offsets(accesses: list[tuple[str, str]]) -> list[int]:
    """Pull hex offsets from field-access patterns like x44_velocity, xC4, unk30, etc."""
    offsets: list[int] = []
    rx = re.compile(r"^(?:x|X|unk)([0-9A-Fa-f]{1,4})(?:_|$)")
    for kind, detail in accesses:
        if kind not in {"arrow_field", "dot_field"}:
            continue
        m = rx.match(detail)
        if m:
            try:
                offsets.append(int(m.group(1), 16))
            except ValueError:
                pass
    return offsets


def _find_struct_candidates(offsets: list[int], *, max_results: int = 5) -> list[tuple[str, str, int]]:
    """Best-effort: search headers for struct definitions whose `/* 0xNN */`
    annotated fields match the observed offsets. Returns (struct_name, rel_path, score).

    Score = number of matched offsets. Crude but catches the common melee pattern.
    """
    if not offsets:
        return []
    target = set(offsets)
    cands: list[tuple[str, str, int]] = []

    header_dirs = [SRC, ROOT / "include"]
    struct_rx = re.compile(
        r"(?:typedef\s+)?struct\s+(\w+)?\s*\{([^{}]*?(?:\{[^{}]*\}[^{}]*?)*)\}\s*(\w+)?\s*;",
        re.DOTALL,
    )
    field_offset_rx = re.compile(r"/\*\s*0x([0-9A-Fa-f]+)\s*\*/")

    for header_dir in header_dirs:
        if not header_dir.exists():
            continue
        for header in header_dir.rglob("*.h"):
            try:
                text = header.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "/* 0x" not in text:
                continue
            for m in struct_rx.finditer(text):
                struct_body = m.group(2)
                struct_offsets = {int(o.group(1), 16) for o in field_offset_rx.finditer(struct_body)}
                if not struct_offsets:
                    continue
                matched = target & struct_offsets
                if len(matched) >= max(1, len(target) * 2 // 3):
                    name = m.group(1) or m.group(3) or "<anon>"
                    cands.append((name, rel(header).as_posix(), len(matched)))
    cands.sort(key=lambda x: -x[2])
    seen: set[str] = set()
    out: list[tuple[str, str, int]] = []
    for c in cands:
        if c[0] in seen:
            continue
        seen.add(c[0])
        out.append(c)
        if len(out) >= max_results:
            break
    return out


def cmd_propose_types(args: argparse.Namespace) -> None:
    """Gather access-pattern evidence for a function's argument types.

    Output structure: signature, per-arg access patterns + offset summary,
    candidate structs from header search (offset-layout match), and call sites
    showing what types the callers pass. Agent reasons over evidence; tool
    does NOT propose types itself.
    """
    func = args.func
    c_file = find_c_file(func)
    rel_c = rel(c_file).as_posix()
    c_text = c_file.read_text(encoding="utf-8", errors="replace")
    body_info = _extract_func_body(c_text, func)
    if body_info is None:
        sys.exit(f"could not locate definition of {func} in {rel_c}")
    start_line, end_line, body = body_info

    sig_rx = re.compile(
        r"^([A-Za-z_][\w \t\*]*?\b" + re.escape(func) + r")\s*\(([^;)]*)\)\s*\n?\s*\{",
        re.MULTILINE,
    )
    sig_m = sig_rx.search(c_text)
    if not sig_m:
        sys.exit(f"can't parse signature for {func}")
    return_and_name = sig_m.group(1).strip()
    args_text = sig_m.group(2).strip()
    arg_specs = _parse_args_list(args_text)
    # Strip signature off the body so access analysis doesn't count the
    # function's own definition line as a "call_arg" of itself.
    body_inner_start = body.find("{")
    body_inner = body[body_inner_start + 1:] if body_inner_start >= 0 else body

    print(f"# propose-types: {func}")
    print(f"# file: {rel_c}:{start_line}-{end_line}")
    print(f"# signature: {return_and_name}({args_text})")
    print()
    print(f"## Arguments ({len(arg_specs)})")
    for declared_type, arg_name in arg_specs:
        print()
        print(f"### `{arg_name}: {declared_type}`")
        if not arg_name:
            print("  (unnamed parameter)")
            continue
        accesses = _find_accesses_for_arg(body_inner, arg_name)
        if not accesses:
            print("  (no accesses in body -- unused or aliased to a local)")
            continue
        # Group by kind
        by_kind: dict[str, list[str]] = {}
        for kind, detail in accesses:
            by_kind.setdefault(kind, []).append(detail)
        for kind in ("arrow_field", "dot_field", "subscript", "deref",
                     "addr_of", "compare_null", "assignment", "call_arg"):
            if kind not in by_kind:
                continue
            seen: list[str] = []
            for d in by_kind[kind]:
                if d not in seen:
                    seen.append(d)
            shown = seen[:8]
            extra = f" (+{len(seen) - 8} more)" if len(seen) > 8 else ""
            print(f"  {kind}: {shown}{extra}")
        offsets = _extract_field_offsets(accesses)
        if offsets:
            uniq = sorted(set(offsets))
            print(f"  observed offsets: {[f'0x{o:X}' for o in uniq]}")
            cands = _find_struct_candidates(uniq)
            if cands:
                print(f"  candidate structs (offset-layout match):")
                for name, path, score in cands:
                    print(f"    {name} -- {path} (matched {score}/{len(uniq)} offsets)")
            else:
                print(f"  (no struct found with matching offset annotations -- agent can grep for these manually)")
    print()

    # Call sites — show what callers pass
    callers = _find_callers(func, max_results=20, exclude_def_in=(c_file, start_line, end_line))
    print(f"## Call sites ({len(callers)})")
    if callers:
        for path, line_no, line in callers[:15]:
            print(f"  {path}:{line_no}: {line.strip()[:140]}")
    else:
        print("  (none in src/ -- only invoked via function pointer)")
    print()
    print("## Suggested next step")
    print("Review the access patterns above. Propose argument types based on cited offset")
    print("evidence and caller-passed types. Verification: every dereferenced offset must")
    print("exist in the proposed struct. CONTRIBUTING.md: don't propose what the access")
    print("pattern doesn't support.")


def cmd_pr_check(args: argparse.Namespace) -> None:
    """Dry-run: cherry-pick our 'Match ' commits onto upstream master in a worktree.

    Reports clean / conflict / polluted (touches non-source paths) so the user
    knows what's PR-ready and what needs cleanup before submission.
    """
    upstream_url = args.upstream
    base_ref = args.base
    worktree_dir = Path(args.worktree).resolve()

    # 1. Ensure 'upstream' remote
    cur = subprocess.run(
        ["git", "remote", "get-url", "upstream"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if cur.returncode != 0:
        print(f"[pr-check] adding upstream remote -> {upstream_url}")
        rc = subprocess.run(
            ["git", "remote", "add", "upstream", upstream_url],
            cwd=ROOT, capture_output=True, text=True,
        )
        if rc.returncode != 0:
            sys.exit(f"git remote add failed: {rc.stderr}")

    # 2. Fetch upstream
    print(f"[pr-check] fetching upstream/{base_ref}...")
    fetch = subprocess.run(
        ["git", "fetch", "upstream", base_ref],
        cwd=ROOT, capture_output=True, text=True,
    )
    if fetch.returncode != 0:
        sys.exit(f"git fetch failed: {fetch.stderr}")

    upstream_ref = f"upstream/{base_ref}"

    # 3. Find merge-base
    mb = subprocess.run(
        ["git", "merge-base", upstream_ref, "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"[pr-check] merge-base: {mb[:9]}")

    # 4. List Match commits since divergence
    log = subprocess.run(
        ["git", "log", "--reverse", "--format=%H|%s", f"{mb}..HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    all_commits = []
    for line in log.stdout.strip().splitlines():
        if "|" in line:
            sha, subj = line.split("|", 1)
            all_commits.append((sha, subj))
    match_commits = [(s, t) for s, t in all_commits if t.startswith("Match ")]
    print(f"[pr-check] {len(match_commits)} 'Match ' commit(s) since divergence (of {len(all_commits)} total)")

    # 5. Filter for source-only (skip tooling-polluted)
    SRC_PREFIXES = ("src/melee/", "src/sysdolphin/", "include/")
    clean: list[tuple[str, str]] = []
    polluted: list[tuple[str, str, list[str]]] = []
    for sha, subj in match_commits:
        files = subprocess.run(
            ["git", "show", "--name-only", "--format=", sha],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
        files = [f for f in files if f]
        bad = [f for f in files if not f.startswith(SRC_PREFIXES)]
        if bad:
            polluted.append((sha, subj, bad))
        else:
            clean.append((sha, subj))
    print(f"[pr-check]   clean (source-only): {len(clean)}")
    print(f"[pr-check]   polluted (touches tooling): {len(polluted)}")

    # 6. Setup worktree
    if worktree_dir.exists():
        print(f"[pr-check] removing existing worktree: {worktree_dir}")
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_dir)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if worktree_dir.exists():
            sys.exit(f"failed to remove existing dir: {worktree_dir}")

    print(f"[pr-check] creating worktree: {worktree_dir}")
    wt = subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), upstream_ref],
        cwd=ROOT, capture_output=True, text=True,
    )
    if wt.returncode != 0:
        sys.exit(f"git worktree add failed: {wt.stderr}")

    # 7. Cherry-pick clean commits one by one
    successes: list[tuple[str, str]] = []
    conflicts: list[tuple[str, str, str]] = []
    for sha, subj in clean:
        rc = subprocess.run(
            ["git", "cherry-pick", sha],
            cwd=worktree_dir, capture_output=True, text=True,
        )
        if rc.returncode == 0:
            successes.append((sha, subj))
        else:
            conflicting_files = []
            st = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=worktree_dir, capture_output=True, text=True,
            )
            conflicting_files = st.stdout.strip().splitlines()
            conflicts.append((sha, subj, ", ".join(conflicting_files) or "?"))
            subprocess.run(
                ["git", "cherry-pick", "--abort"],
                cwd=worktree_dir, capture_output=True, text=True,
            )

    # 8. Report
    print()
    print("=" * 60)
    print("PR-CHECK RESULTS")
    print("=" * 60)
    print(f"Worktree: {worktree_dir}")
    print(f"Base:     {upstream_ref} ({mb[:9]})")
    print()
    print(f"Cherry-pick: {len(successes)}/{len(clean)} clean, {len(conflicts)} conflicted")
    if conflicts:
        print()
        print("Conflicts (need manual resolution before PR):")
        for sha, subj, files in conflicts:
            print(f"  {sha[:9]}  {subj}")
            print(f"             conflict in: {files}")
    if polluted:
        print()
        print(f"Polluted commits ({len(polluted)} -- need splitting before PR):")
        for sha, subj, bad in polluted:
            print(f"  {sha[:9]}  {subj}")
            for f in bad[:3]:
                print(f"             + {f}")
            if len(bad) > 3:
                print(f"             + ... (+{len(bad) - 3} more files)")
    print()
    print(f"Next steps:")
    print(f"  - inspect: cd {worktree_dir} && git log --oneline {upstream_ref}..HEAD")
    print(f"  - build-verify (heavy): cd {worktree_dir} && python configure.py && wsl ninja")
    print(f"  - cleanup when done: git worktree remove {worktree_dir}")


def main() -> None:
    # Wire dependencies into extracted modules so they can call back into
    # the main script's helpers without circular imports.
    permute_notes._set_deps(
        find_c_file=find_c_file,
        rel=rel,
        current_fuzzy_pct=_current_fuzzy_pct,
        find_similar_via_embeddings=find_similar_via_embeddings,
        disasm_and_extract=disasm_and_extract,
        log_event=_log_event,
        build_linux=BUILD_LINUX,
    )
    permute_upstream._set_deps(find_c_file=find_c_file)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("prep", help="extract a function's asm")
    pp.add_argument("func")
    pp.add_argument("-q", "--quiet", action="store_true", help="don't dump asm to stdout")
    pp.add_argument(
        "--no-context",
        dest="context",
        action="store_false",
        help="skip the referenced-symbols summary",
    )
    pp.add_argument(
        "--m2c",
        action="store_true",
        help="also run m2c (via tools/decomp.py) to print a starting decompilation",
    )
    pp.add_argument(
        "--examples",
        type=int,
        default=0,
        metavar="N",
        help="show N already-matched functions from the same TU as in-context examples",
    )
    pp.add_argument(
        "--similar",
        type=int,
        default=0,
        metavar="N",
        help="show N most-similar matched functions via embeddings (requires `index-embeddings` first)",
    )
    pp.add_argument(
        "--skip-upstream-check",
        action="store_true",
        dest="skip_upstream_check",
        help="bypass the upstream-match pre-flight check (use only if intentionally re-working an upstream match)",
    )
    pp.set_defaults(handler=cmd_prep, context=True)

    pie = sub.add_parser("index-embeddings", help="build the function-similarity embeddings index (~30 min, one-time)")
    pie.set_defaults(handler=lambda args: subprocess.run(
        [
            "wsl", "-d", WSL_DISTRO, "--", "bash", "-c",
            "cd /mnt/c/Users/david/projects/melee && .venv-embeddings/bin/python tools/embed_index.py build",
        ],
        cwd=ROOT,
    ))

    pd = sub.add_parser("diff", help="show match%% and mismatched instructions for a function")
    pd.add_argument("func")
    pd.add_argument(
        "--auto-permute",
        action="store_true",
        help="if match%% < 100 and within --permute-threshold mismatches, launch permuter in background",
    )
    pd.add_argument(
        "--permute-threshold",
        type=int,
        default=15,
        help="max mismatched instructions to consider a near-miss (default 15)",
    )
    pd.add_argument(
        "--max-concurrent",
        type=int,
        default=DEFAULT_MAX_CONCURRENT_PERMUTERS,
        help=f"refuse to launch a new local permuter when this many already running (default {DEFAULT_MAX_CONCURRENT_PERMUTERS})",
    )
    pd.add_argument(
        "--cluster",
        action="store_true",
        help="dispatch to local p@h cluster (`-J` mode), bypassing the local CPU cap. Requires tools/pah/ controller running.",
    )
    pd.add_argument(
        "--with-fuzzy",
        action="store_true",
        help="also rebuild report.json so fuzzy_match_percent is current (~30s extra). Default: skip — use commit-match for fuzzy verification.",
    )
    pd.add_argument(
        "--force-permute",
        action="store_true",
        dest="force_permute",
        help="dispatch --auto-permute even when reloc-symbol mismatches dominate (default: refuse, since permuter scorer treats them as equivalent and the run will plateau)",
    )
    pd.set_defaults(handler=cmd_diff)

    pcm = sub.add_parser("commit-match", help="verify 100%% match in both objdiff + report.json, then commit (refuses otherwise)")
    pcm.add_argument("func")
    pcm.add_argument("-m", "--message", help="commit message (default: 'Match <func>')")
    pcm.add_argument("--with-header", action="store_true",
                     help="after the .c commit, also commit any modified .h/.static.h files that reference the function (verifies build still passes first)")
    pcm.set_defaults(handler=cmd_commit_match)

    pps = sub.add_parser("permute-stop", help="stop a backgrounded permuter run")
    pps.add_argument("func")
    pps.set_defaults(handler=cmd_permute_stop)

    pbg = sub.add_parser("budget", help="show active permuters and CPU budget headroom")
    pbg.add_argument(
        "--max-concurrent",
        type=int,
        default=DEFAULT_MAX_CONCURRENT_PERMUTERS,
        help=f"max concurrent permuters (default {DEFAULT_MAX_CONCURRENT_PERMUTERS})",
    )
    pbg.set_defaults(handler=cmd_budget)

    pr = sub.add_parser("reap", help="kill stuck/timed-out permuters (wall-clock or silence cap)")
    pr.add_argument("--wall-cap-min", type=int, default=DEFAULT_REAP_WALL_MIN,
                    help=f"max wall-clock minutes per permuter (default {DEFAULT_REAP_WALL_MIN})")
    pr.add_argument("--silent-cap-min", type=int, default=DEFAULT_REAP_SILENT_MIN,
                    help=f"kill if no log + no new outputs for N minutes (default {DEFAULT_REAP_SILENT_MIN})")
    pr.add_argument("--dry-run", action="store_true", help="report what would be killed but don't kill")
    pr.add_argument("--aggressive", action="store_true",
                    help="also kill permuters whose target is already at fuzzy=100%% in report.json, and clean stale .dispatched markers")
    pr.set_defaults(handler=cmd_reap)

    ph = sub.add_parser("harvest",
                        help="report 100%% matches ready to commit, plateau runs ready for re-dispatch")
    ph.add_argument("--plateau-min", type=int, default=15,
                    help="treat a run as plateaued after N min without a new output (default 15)")
    ph.add_argument("--show-empty", action="store_true",
                    help="also list nonmatchings/ dirs with no outputs yet")
    ph.add_argument("--show-false-positives", action="store_true",
                    help="don't suppress score=0 hits for funcs tagged as TU-layout blockers in decomp-notes")
    ph.set_defaults(handler=cmd_harvest)

    po = sub.add_parser("outputs", help="show permuter zero-score output diffs for a function (port candidate review)")
    po.add_argument("func")
    po.add_argument("--limit", type=int, default=5, help="max outputs to show (default 5)")
    po.set_defaults(handler=cmd_outputs)

    # `notes` and `log-stuck` subcommands are registered by permute_notes.py
    permute_notes.add_subcommands(sub)
    permute_upstream.add_subcommands(sub)

    pbk = sub.add_parser(
        "backlog",
        help="list functions worth re-dispatching to the cluster (filtered against structural blockers)",
    )
    pbk.add_argument("--limit", type=int, default=20, help="max entries per section (default 20)")
    pbk.add_argument("--plateau-min", type=int, default=30,
                     help="only include plateau funcs idle this many min (default 30)")
    pbk.add_argument("--max-mismatches", type=int, default=6,
                     help="fresh: skip funcs with more than N estimated mismatches (default 6)")
    pbk.add_argument("--min-fuzzy", type=float, default=99.0,
                     help="fresh: skip funcs below this fuzzy %% (default 99.0)")
    pbk.add_argument("--no-fresh", action="store_true",
                     help="skip the fresh-near-misses section")
    pbk.add_argument("--fire", type=int, default=0, metavar="N",
                     help="re-dispatch top N candidates to the cluster")
    pbk.add_argument("--ready", action="store_true",
                     help="filter to candidates ready for immediate dispatch (excludes TUs with 2+ stuck siblings AND funcs dispatched within last 60min)")
    pbk.add_argument("--no-stuck-tu", action="store_true",
                     help="exclude candidates in TUs with 2+ logged stuck siblings")
    pbk.add_argument("--no-tu-locked", action="store_true",
                     help="exclude candidates in TUs currently held by a tu-refactor lock")
    pbk.add_argument("--reserve", action="store_true",
                     help="atomically reserve printed candidates by touching .dispatched markers; subsequent --ready calls won't pick them")
    pbk.set_defaults(handler=cmd_backlog)

    pra = sub.add_parser("reset-attempts", help="clear the 2-variant cap counter for <func> (use sparingly)")
    pra.add_argument("func")
    pra.set_defaults(handler=cmd_reset_attempts)

    pci = sub.add_parser("commit-improvements", help="bank non-match source improvements (>= threshold mismatch drop) as `improve` commits")
    pci.add_argument("--threshold", type=int, default=1, help="min mismatch_count drop to commit (default 1)")
    pci.add_argument("--dry-run", action="store_true", help="preview without committing")
    pci.add_argument("--max", type=int, default=5, help="max commits per invocation (default 5)")
    pci.set_defaults(handler=cmd_commit_improvements)

    ptl = sub.add_parser("tu-lock", help="claim exclusive edit lock for a TU (for tu-refactor agents)")
    ptl.add_argument("tu", help="path to .c file (e.g. src/melee/lb/lbcardnew.c)")
    ptl.set_defaults(handler=cmd_tu_lock)

    ptu = sub.add_parser("tu-unlock", help="release the TU-refactor lock for a .c file")
    ptu.add_argument("tu", help="path to .c file")
    ptu.set_defaults(handler=cmd_tu_unlock)

    ptb = sub.add_parser("tu-brief", help="emit a TU-refactor brief: stuck functions grouped by shared blocker tags")
    ptb.add_argument("tu", help="path to .c file")
    ptb.set_defaults(handler=cmd_tu_brief)

    pcl = sub.add_parser(
        "classify",
        help="recommend a tier (skip/cluster-only/haiku/sonnet/opus) for working on a function",
    )
    pcl.add_argument("func")
    pcl.add_argument("--skip-build", action="store_true",
                     help="don't rebuild base.o + report.json (faster but uses possibly-stale data)")
    pcl.set_defaults(handler=cmd_classify)

    pds = sub.add_parser(
        "dispatch",
        help="classify a batch and AUTO-fire skip/cluster-only; print the rest for mama to dispatch",
    )
    pds.add_argument("funcs", nargs="+", help="function names to dispatch")
    pds.set_defaults(handler=cmd_dispatch)

    pbr = sub.add_parser(
        "brief",
        help="emit a complete subagent prompt for working on a function (auto-injects prior diagnoses)",
    )
    pbr.add_argument("func")
    pbr.add_argument("--similar", action="store_true",
                     help="also include diagnoses from embedding-similar functions and recent matched siblings (slow: loads jina model)")
    pbr.set_defaults(handler=cmd_brief)

    pev = sub.add_parser(
        "events",
        help="aggregate swarm-events.jsonl: time-to-outcome per recommendation class",
    )
    pev.add_argument("--since-hours", type=float, default=24,
                     help="only include events from the last N hours (default 24)")
    pev.set_defaults(handler=cmd_events)

    pcb = sub.add_parser(
        "compact-brief",
        help="emit a compact diagnostic for a function (~3K of text vs prep's 25K — for cheap subagent dispatch)",
    )
    pcb.add_argument("func")
    pcb.add_argument("--no-cache", action="store_true",
                     help="ignore the cached brief and recompute")
    pcb.add_argument("--no-build", action="store_true",
                     help="skip the implicit ninja rebuild (use existing base.o if present)")
    pcb.set_defaults(handler=cmd_brief_compact)

    ppk = sub.add_parser("picker", help="list undecompiled functions sorted by difficulty")
    ppk.add_argument("--limit", type=int, default=30, help="max results (default 30)")
    ppk.add_argument("--max-size", type=int, default=None, help="max size in bytes")
    ppk.add_argument(
        "--mode",
        choices=["untouched", "in_progress", "all"],
        default="untouched",
        help="untouched=0%% match, in_progress=between 0%% and 100%%, all=both",
    )
    ppk.add_argument(
        "--source-differs-upstream", action="store_true",
        help=("only include functions whose TU source differs from upstream/master. "
              "Filters out TUs where source is identical (so any non-100%% is build-env "
              "or neighbor-TU layout, not source-shape work for a subagent)."),
    )
    ppk.set_defaults(handler=cmd_picker)

    pse = sub.add_parser(
        "sweep-lha-extsh",
        help="scan near-misses for lha-r0 plus extsh-r3 sign-extension fix candidates",
    )
    pse.add_argument("--limit", type=int, default=30, help="max hits to print (default 30)")
    pse.add_argument("--scan-limit", type=int, default=250,
                     help="max near-miss candidates to objdiff-scan after filtering (default 250)")
    pse.add_argument("--max-size", type=int, default=320,
                     help="max function size in bytes to scan (default 320)")
    pse.add_argument("--min-fuzzy", type=float, default=80.0,
                     help="minimum fuzzy match percent to scan (default 80.0)")
    pse.add_argument("--max-fuzzy", type=float, default=100.0,
                     help="maximum fuzzy match percent to scan, exclusive (default 100.0)")
    pse.add_argument("--include-notes", action="store_true",
                     help="include functions already present in decomp-notes.md")
    pse.set_defaults(handler=cmd_sweep_lha_extsh)

    pc = sub.add_parser("check", help="run ninja and report SHA1 status")
    pc.set_defaults(handler=cmd_check)

    pm = sub.add_parser("permute", help="import a function into permuter")
    pm.add_argument("func")
    pm.set_defaults(handler=cmd_permute)

    pnm = sub.add_parser(
        "propose-naming",
        help="gather citation-grounded naming evidence for a function (asserts, OSReports, callers, similar matches)",
    )
    pnm.add_argument("func")
    pnm.set_defaults(handler=cmd_propose_naming)

    ppt = sub.add_parser(
        "propose-types",
        help="gather access-pattern + offset evidence for argument types (with candidate-struct match)",
    )
    ppt.add_argument("func")
    ppt.set_defaults(handler=cmd_propose_types)

    pprc = sub.add_parser(
        "pr-check",
        help="dry-run cherry-pick of Match commits onto upstream master in a worktree (reports conflicts + tooling-pollution)",
    )
    pprc.add_argument("--upstream", default="https://github.com/doldecomp/melee",
                      help="upstream URL (default: doldecomp/melee)")
    pprc.add_argument("--base", default="master",
                      help="upstream branch to rebase onto (default: master)")
    pprc.add_argument("--worktree", default=str((ROOT.parent / "melee-pr-check").resolve()),
                      help="path for the test worktree (default: ../melee-pr-check)")
    pprc.set_defaults(handler=cmd_pr_check)

    args = p.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
