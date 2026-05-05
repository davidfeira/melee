#!/usr/bin/env python3
"""One-time migration: split decomp-notes.md into per-function decomp-notes/<func>.md files.

Each output file gets YAML frontmatter (function, tu, tags, headline, paired_with) plus
the original markdown body. Run once; afterwards `permute.py log-stuck` writes new entries
directly to the per-function file format.

Usage:
    python tools/migrate_notes_split.py          # dry-run (count + sample)
    python tools/migrate_notes_split.py --apply  # actually write files
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = ROOT / "decomp-notes.md"
OUT_DIR = ROOT / "decomp-notes"


def parse_entries(text: str) -> list[dict]:
    """Return list of {funcs, tu, headline, body, tags}."""
    entries: list[dict] = []
    current: dict | None = None
    body_lines: list[str] = []

    def flush():
        nonlocal current, body_lines
        if current is None:
            return
        body = "\n".join(body_lines).rstrip() + "\n"
        # Extract tags
        tags: list[str] = []
        m = re.search(r"\*\*Tags:\*\*\s*(.+)", body)
        if m:
            for raw in re.findall(r"`([^`]+)`", m.group(1)):
                if raw.strip():
                    tags.append(raw.strip())
        current["body"] = body
        current["tags"] = tags
        entries.append(current)
        current = None
        body_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            # Parse: "fnA + fnB (`path`) — headline"
            tu = ""
            headline = ""
            name_part = heading
            tu_match = re.search(r"\(`([^`]+)`\)", heading)
            if tu_match:
                tu = tu_match.group(1)
                name_part = heading[: tu_match.start()].strip()
                rest = heading[tu_match.end():].strip()
                if rest.startswith("—") or rest.startswith("-"):
                    headline = rest.lstrip("—-").strip()
            else:
                # No TU — split on em-dash
                if "—" in heading:
                    name_part, headline = heading.split("—", 1)
                    name_part, headline = name_part.strip(), headline.strip()
            funcs = [n.strip() for n in name_part.split("+") if n.strip()]
            current = {
                "funcs": funcs,
                "tu": tu,
                "headline": headline,
                "raw_heading": line,
            }
            body_lines = [line]
        elif current is not None:
            body_lines.append(line)
        # Lines before any `## ` are just the file preamble; skip.
    flush()
    return entries


def safe_filename(func: str) -> str:
    """Function names should already be filesystem-safe, but guard against weirdness."""
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", func)


def write_entry(entry: dict, out_dir: Path) -> Path:
    primary = entry["funcs"][0]
    paired = entry["funcs"][1:]
    tu = entry["tu"]
    headline = entry["headline"]
    tags = entry["tags"]

    fm_lines = ["---"]
    fm_lines.append(f"function: {primary}")
    if paired:
        fm_lines.append(f"paired_with: [{', '.join(paired)}]")
    if tu:
        fm_lines.append(f"tu: {tu}")
    if headline:
        # YAML scalar — quote if it contains special chars
        if any(c in headline for c in ":#&*!|>'\"%@`"):
            esc = headline.replace('"', '\\"')
            fm_lines.append(f'headline: "{esc}"')
        else:
            fm_lines.append(f"headline: {headline}")
    if tags:
        fm_lines.append(f"tags: [{', '.join(tags)}]")
    fm_lines.append("---")
    fm_lines.append("")

    body = entry["body"]
    text = "\n".join(fm_lines) + body

    out_path = out_dir / f"{safe_filename(primary)}.md"
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write files (default: dry-run)")
    args = ap.parse_args()

    if not SRC_PATH.exists():
        sys.exit(f"{SRC_PATH} does not exist")

    text = SRC_PATH.read_text(encoding="utf-8")
    entries = parse_entries(text)

    print(f"parsed {len(entries)} entries from {SRC_PATH}")
    multi = [e for e in entries if len(e["funcs"]) > 1]
    no_tu = [e for e in entries if not e["tu"]]
    no_headline = [e for e in entries if not e["headline"]]
    no_tags = [e for e in entries if not e["tags"]]
    print(f"  multi-function entries: {len(multi)}")
    print(f"  entries without TU path: {len(no_tu)}")
    print(f"  entries without headline: {len(no_headline)}")
    print(f"  entries without tags: {len(no_tags)}")

    if no_tu:
        print("\nentries missing TU path (heading shown):")
        for e in no_tu[:5]:
            print(f"  {e['raw_heading']}")

    if not args.apply:
        print("\n(dry-run; pass --apply to write files)")
        if no_headline:
            print("\nentries without headline (heading shown):")
            for e in no_headline:
                print(f"  {e['raw_heading']}")
        return

    if OUT_DIR.exists() and any(OUT_DIR.iterdir()):
        sys.exit(f"{OUT_DIR} already exists and is non-empty; refuse to overwrite")
    OUT_DIR.mkdir(exist_ok=True)

    written = 0
    collisions: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for e in entries:
        out_path = write_entry(e, OUT_DIR)
        if out_path in seen:
            collisions.append((e["funcs"][0], out_path))
        seen.add(out_path)
        written += 1

    print(f"wrote {written} files to {OUT_DIR}")
    if collisions:
        print(f"WARNING: {len(collisions)} filename collisions (later entry overwrote earlier):")
        for func, p in collisions:
            print(f"  {func} -> {p.name}")


if __name__ == "__main__":
    main()
