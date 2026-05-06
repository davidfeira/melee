#!/usr/bin/env python3
"""Extract a single function from dtk-disasm output into permuter glabel format."""
import re
import sys
from pathlib import Path


def extract(disasm_path: Path, func_name: str) -> str:
    # asm files may contain SJIS bytes from string data; tolerate them
    text = disasm_path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        rf"^\.fn\s+{re.escape(func_name)},\s*\w+\s*\n(.*?)^\.endfn\s+{re.escape(func_name)}",
        re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        sys.exit(f"function {func_name!r} not found in {disasm_path}")

    body = match.group(1)
    out_lines = [f".globl {func_name}", f"{func_name}:"]
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith(".endfn"):
            continue
        out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <disasm.s> <function_name>")
    disasm = Path(sys.argv[1])
    name = sys.argv[2]
    sys.stdout.write(extract(disasm, name))


if __name__ == "__main__":
    main()
