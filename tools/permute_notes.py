"""decomp-notes/ store + log-stuck command.

Extracted from tools/permute.py as the first step of a per-command-group split.
The main script imports CANONICAL_TAGS, _parse_notes, cmd_notes, cmd_log_stuck
from here. The pattern set here applies to future extractions: shared helpers
move to tools/permute_common.py once we identify them; per-command-group code
moves to tools/permute_<group>.py.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Storage paths
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_ROOT = _THIS_DIR.parent
_NOTES_PATH = _ROOT / "decomp-notes.md"   # legacy monolith (read-only fallback)
_NOTES_DIR = _ROOT / "decomp-notes"       # per-function files with frontmatter (preferred)


# ---------------------------------------------------------------------------
# Canonical tag inventory
# ---------------------------------------------------------------------------

# Adding a new tag requires --allow-new-tag. Synced with all tags currently in
# decomp-notes.md as of canonicalization. New entries should reuse an existing
# tag where possible — a typo creates a "new" tag that no future query will find.
CANONICAL_TAGS: frozenset[str] = frozenset({
    # Diagnosis — what the source-vs-asm mismatch is
    "regalloc", "float-regalloc", "r30-r31-swap",
    "stack-offset", "frame-size",
    "float-literal", "literal-pool", "string-pool",
    "instruction-scheduling", "scheduler",
    "varargs-cr1eq", "bitfield-reuse",
    "branch-pattern", "branch-direction",
    "dead-cmpw", "dead-loads", "trailing-blr",
    "fma-fusion", "goto-loop", "inlining",
    "struct-split", "struct-typing",
    # Compiler quirks
    "mwcc-aliasing", "mwcc-branch-inversion", "mwcc-const-fold", "mwcc-loop-opt",
    # Permuter false-positive family (post-link bytes match, fuzzy scorer disagrees)
    "permuter-false-positive", "reloc-symbol-false-positive", "fuzzy-vs-strict",
    "sdata2-float", "sdata2-anonymous-floats", "sdata2-named", "sdata2-named-floats",
    "sdata2-named-global", "sda21", "sda21-float-collision",
    "bss-anchor", "data-anchor", "sdata-anchor",
    # TU-level / cross-function blockers
    "tu-wide-data", "cross-tu-globals", "paired-siblings", "tu-data-osreport",
    "tu-sdata2-globals", "data-symbols-missing", "sdata-symbols-missing",
    "cross-function-rodata", "rodata-typing",
    # Header / extern / prototype
    "header-prototype", "header-required", "extern-dolphin", "prototype-experiment",
    # Permuter run status / tooling
    "permuter-territory", "permuter-blocked", "permuter-plateau", "permuter-dispatched",
    "permuter-resistant", "permuter-tooling-failure", "tooling-gap",
    # Misc / meta
    "upstream-regression",
})


def _validate_tags(tags: list[str], *, allow_new: bool = False) -> None:
    """Reject tags outside CANONICAL_TAGS unless --allow-new-tag was passed."""
    unknown = [t for t in tags if t not in CANONICAL_TAGS]
    if not unknown:
        return
    if allow_new:
        for t in unknown:
            print(f"[log-stuck] WARNING: new tag `{t}` (not in canonical inventory)", file=sys.stderr)
        return
    import difflib
    msg_lines = [f"unknown tag(s): {', '.join(unknown)}"]
    for t in unknown:
        close = difflib.get_close_matches(t, CANONICAL_TAGS, n=3, cutoff=0.6)
        if close:
            msg_lines.append(f"  `{t}` — did you mean: {', '.join(close)}?")
    msg_lines.append("If this really is a new category, re-run with --allow-new-tag.")
    msg_lines.append("See canonical list: python tools/permute.py notes --tag-inventory")
    sys.exit("\n".join(msg_lines))


# ---------------------------------------------------------------------------
# Frontmatter + per-function file parsing
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML-frontmatter markdown into (frontmatter_dict, body).

    Minimal parser: only handles `key: value` and `key: [a, b, c]` forms.
    Avoids a yaml dependency.
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]
    fm: dict = {}
    for line in fm_text.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fm[key] = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif value.startswith('"') and value.endswith('"'):
            fm[key] = value[1:-1].replace('\\"', '"')
        else:
            fm[key] = value
    return fm, body


def _parse_notes() -> dict[str, dict]:
    """Parse notes from decomp-notes/<func>.md (preferred) or legacy decomp-notes.md.

    Returns {func_name: {body, tags, header}} where multi-function entries are
    indexed under each paired function name.
    """
    entries: dict[str, dict] = {}

    # New format: per-function files with YAML frontmatter
    if _NOTES_DIR.exists():
        for path in sorted(_NOTES_DIR.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            fm, body = _parse_frontmatter(text)
            primary = fm.get("function") or path.stem
            paired = fm.get("paired_with") or []
            tags = set(fm.get("tags") or [])
            header = primary
            entry = {"body": body, "tags": tags, "header": header}
            entries[primary] = entry
            for f in paired:
                entries[f] = entry
        return entries

    # Legacy fallback: monolith decomp-notes.md
    if not _NOTES_PATH.exists():
        return {}
    text = _NOTES_PATH.read_text(encoding="utf-8", errors="replace")
    current_funcs: list[str] = []
    current_body: list[str] = []
    current_tags: set[str] = set()

    def flush() -> None:
        if not current_funcs:
            return
        body = "\n".join(current_body).rstrip() + "\n"
        for f in current_funcs:
            entries[f] = {"body": body, "tags": set(current_tags), "header": current_funcs[0]}

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            current_body = [line]
            current_tags = set()
            heading = line[3:].strip()
            name_part = heading.split("(")[0].strip()
            current_funcs = [n.strip() for n in name_part.split("+") if n.strip()]
        else:
            current_body.append(line)
            tag_match = re.match(r"\s*-?\s*\*\*Tags:\*\*\s*(.+)$", line)
            if tag_match:
                tags_str = tag_match.group(1)
                for raw in re.findall(r"`([^`]+)`", tags_str):
                    current_tags.add(raw.strip())
    flush()
    return entries


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

# These two commands have a small surface of dependencies on the rest of permute.py.
# We accept them as injected callables so this module stays import-clean. The main
# script wires them up via register_handlers().

_deps: dict[str, Callable] = {}


def _set_deps(*, find_c_file, rel, current_fuzzy_pct, find_similar_via_embeddings,
              disasm_and_extract, log_event, build_linux: Path) -> None:
    """Wire dependencies from the main script. Called once at startup."""
    _deps["find_c_file"] = find_c_file
    _deps["rel"] = rel
    _deps["current_fuzzy_pct"] = current_fuzzy_pct
    _deps["find_similar_via_embeddings"] = find_similar_via_embeddings
    _deps["disasm_and_extract"] = disasm_and_extract
    _deps["log_event"] = log_event
    _deps["build_linux"] = build_linux


def cmd_log_stuck(args: argparse.Namespace) -> None:
    """Write a per-function diagnostic entry to decomp-notes/<func>.md."""
    func = args.func
    if not args.tags:
        sys.exit("--tags is required (comma-separated, e.g. --tags=stack-offset,float-literal)")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    _validate_tags(tags, allow_new=getattr(args, "allow_new_tag", False))

    if args.from_file:
        body_path = Path(args.from_file)
        if not body_path.is_absolute():
            body_path = _ROOT / body_path
        if not body_path.exists():
            sys.exit(f"--from-file {body_path} does not exist")
        body_text = body_path.read_text(encoding="utf-8")
    else:
        parts: list[str] = []
        if args.diagnosis:
            parts.append(f"- **Diagnosis:** {args.diagnosis}")
        if args.tried:
            parts.append(f"- **Tried:** {args.tried}")
        if args.likely_fix:
            parts.append(f"- **Likely fix:** {args.likely_fix}")
        if not parts:
            sys.exit("provide --diagnosis (and ideally --tried/--likely-fix), or pass --from-file")
        body_text = "\n".join(parts)

    try:
        c_file = _deps["find_c_file"](func)
        c_rel = _deps["rel"](c_file).as_posix()
    except SystemExit:
        c_rel = "<unknown source>"

    fuzzy = _deps["current_fuzzy_pct"](func)
    fuzzy_str = f"{fuzzy:g}%" if fuzzy is not None else "(unknown)"

    headline = " + ".join(tags[:2]) if tags else "blocker"

    md_body_lines = [
        f"## {func} (`{c_rel}`) — {headline}",
        "",
        f"- **Tags:** {', '.join(f'`{t}`' for t in tags)}",
        f"- **Best fuzzy:** {fuzzy_str}",
    ]
    body_text = body_text.strip("\n")
    md_body_lines.append(body_text)
    md_body_lines.append("")
    md_body = "\n".join(md_body_lines) + "\n"

    _NOTES_DIR.mkdir(exist_ok=True)
    out_path = _NOTES_DIR / f"{func}.md"

    if out_path.exists() and not args.force:
        sys.exit(f"entry for {func} already exists at {out_path}; pass --force to replace")

    fm_lines = ["---", f"function: {func}"]
    if c_rel != "<unknown source>":
        fm_lines.append(f"tu: {c_rel}")
    if headline:
        if any(c in headline for c in ":#&*!|>'\"%@`"):
            esc = headline.replace('"', '\\"')
            fm_lines.append(f'headline: "{esc}"')
        else:
            fm_lines.append(f"headline: {headline}")
    if tags:
        fm_lines.append(f"tags: [{', '.join(tags)}]")
    fm_lines.append("---")
    fm_lines.append("")

    out_path.write_text("\n".join(fm_lines) + md_body, encoding="utf-8")

    print(f"[log-stuck] wrote entry for {func} to {out_path.relative_to(_ROOT)}")
    print(f"  tags: {', '.join(tags)}")
    print(f"  fuzzy: {fuzzy_str}")
    print(f"  source: {c_rel}")
    _deps["log_event"]("stuck", func=func, tags=list(tags), fuzzy=fuzzy_str)


def cmd_notes(args: argparse.Namespace) -> None:
    """Look up decomp-notes entries for a function (and similar functions, by embedding)."""
    if getattr(args, "tag_inventory", False):
        print("# Canonical tag inventory (log-stuck validates against this set):\n")
        for t in sorted(CANONICAL_TAGS):
            print(f"  {t}")
        print(f"\n# {len(CANONICAL_TAGS)} canonical tags. Use --allow-new-tag to add a new one.")
        return

    entries = _parse_notes()

    if args.blocker:
        tag = args.blocker
        hits = [(name, e) for name, e in entries.items() if tag in e["tags"]]
        if not hits:
            print(f"no entries tagged `{tag}`")
            return
        print(f"# {len(hits)} entr{'y' if len(hits)==1 else 'ies'} tagged `{tag}`:\n")
        seen_headers: set[str] = set()
        for name, e in hits:
            if e["header"] in seen_headers:
                continue
            seen_headers.add(e["header"])
            print(e["body"])
        return

    if not args.func:
        all_tags: dict[str, int] = {}
        for e in entries.values():
            for t in e["tags"]:
                all_tags[t] = all_tags.get(t, 0) + 1
        print("# Available tags (use --blocker TAG to filter):\n")
        for t, n in sorted(all_tags.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {t:30s} ({n})")
        source_loc = "decomp-notes/" if _NOTES_DIR.exists() else "decomp-notes.md"
        print(f"\n# {len(entries)} total functions in {source_loc}")
        return

    func = args.func
    direct = entries.get(func)
    if direct:
        print(f"# Direct entry for {func}:\n")
        print(direct["body"])

    asm_path = _deps["build_linux"] / f"{func}.s"
    if not asm_path.exists():
        try:
            c_file = _deps["find_c_file"](func)
            asm_path, _ = _deps["disasm_and_extract"](c_file, func)
        except SystemExit:
            return

    similar_names = _deps["find_similar_via_embeddings"](asm_path, n=10, exclude=func)
    relevant = [n for n in similar_names if n in entries]
    if relevant:
        seen_headers = {direct["header"]} if direct else set()
        printed_any = False
        for name in relevant[:5]:
            entry = entries[name]
            if entry["header"] in seen_headers:
                continue
            seen_headers.add(entry["header"])
            if not printed_any:
                print(f"\n# Similar functions with notes (by asm embedding):\n")
                printed_any = True
            print(entry["body"])

    if not direct and not relevant:
        print(f"no notes for {func} or any embedding-similar function")


def add_subcommands(sub: "argparse._SubParsersAction") -> None:
    """Register `notes` and `log-stuck` on the main argparse subparsers."""
    pn = sub.add_parser("notes", help="look up decomp-notes entries for a function or filter by blocker tag")
    pn.add_argument("func", nargs="?", help="function name (omit to list available tags)")
    pn.add_argument("--blocker", help="filter to entries with this tag (e.g. stack-offset, regalloc, mwcc-aliasing)")
    pn.add_argument("--tag-inventory", action="store_true", dest="tag_inventory",
                    help="print the canonical tag list (used by log-stuck validation)")
    pn.set_defaults(handler=cmd_notes)

    pls = sub.add_parser(
        "log-stuck",
        help="append a structured diagnosis to decomp-notes/<func>.md (REQUIRED before reporting stuck)",
        description=(
            "Subagents must call this before reporting 'stuck' so the diagnosis isn't lost.\n"
            "Auto-indexed by the embedding similarity lookup since we embed function ASM,\n"
            "not note text. Future subagents on similar functions will see the entry."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    pls.add_argument("func")
    pls.add_argument("--tags", required=True, help="comma-separated, e.g. stack-offset,float-literal")
    pls.add_argument("--diagnosis", help="what's wrong (one paragraph)")
    pls.add_argument("--tried", help="what was tried that didn't work")
    pls.add_argument("--likely-fix", dest="likely_fix", help="what might unstick it later")
    pls.add_argument("--from-file", dest="from_file", help="read full markdown body from this file (overrides --diagnosis/--tried/--likely-fix)")
    pls.add_argument("--force", action="store_true", help="replace existing entry for this function")
    pls.add_argument("--allow-new-tag", action="store_true", dest="allow_new_tag",
                     help="bypass canonical tag check (use only for genuinely new categories)")
    pls.set_defaults(handler=cmd_log_stuck)
