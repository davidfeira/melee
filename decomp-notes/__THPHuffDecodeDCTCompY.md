---
function: __THPHuffDecodeDCTCompY
tu: <unknown source>
headline: tooling-gap + extern-dolphin
tags: [tooling-gap, extern-dolphin]
---
## __THPHuffDecodeDCTCompY (`<unknown source>`) — tooling-gap + extern-dolphin

- **Tags:** `tooling-gap`, `extern-dolphin`
- **Best fuzzy:** 99.9952%
- **Diagnosis:** Function lives in extern/dolphin/src/dolphin/thp/THPDec.c (THPDec TU). permute.py prep/diff cannot locate it: _build_symbol_cache hardcodes 'src/' prefix when mapping rel_o -> .c, and _find_c_file_by_text only walks SRC = ROOT/'src'. Both lookups skip extern/dolphin entirely, so 'no .c file owns __THPHuffDecodeDCTCompY' is the immediate failure. Additionally, subagent hard-stop rule restricts edits to src/melee/ and src/sysdolphin/, and extern/dolphin/ is ambiguous w.r.t. allowed edit area.
- **Tried:** prep (failed: tooling can't find owner .c), report.json lookup (function exists at fuzzy=99.99518, size=1660, in dolphin/thp/THPDec unit), grep'd all source for symbol (only extern/dolphin/src/dolphin/thp/THPDec.c, extern/dolphin/include/dolphin/thp/thp.h, config/GALE01/symbols.txt have it).
- **Likely fix:** Two-part: (1) extend permute.py _build_symbol_cache and _find_c_file_by_text to also try Path('extern/dolphin/src') / rel_o and walk extern/dolphin/src; (2) explicit guidance from mama Claude on whether subagents may edit extern/dolphin/ files when that is the assigned function's owner. Function diff is reportedly 1 instr off so the actual fix is likely tiny once tooling is unblocked.
