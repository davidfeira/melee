---
function: lbMthp8001FAA0
tu: src/melee/lb/lbmthp.c
headline: permuter-false-positive + cross-tu-globals
tags: [permuter-false-positive, cross-tu-globals, tu-wide-data]
---
## lbMthp8001FAA0 (`src/melee/lb/lbmthp.c`) — permuter-false-positive + cross-tu-globals

- **Tags:** `permuter-false-positive`, `cross-tu-globals`, `tu-wide-data`
- **Best fuzzy:** 99.8555%
- **Diagnosis:** 15 mismatches all permuter-false-positive class (bss-anchor reloc-symbol). Same TU blocker as 3 sibling functions in lbmthp.c (lbMthp8001F928, lbMthp_8001F410, fn_8001F2A4): mwcc coalesces lbl_804335B8 with adjacent Movieplayer (lbl_804333E0) into bss.0 anchor, target build emits lbl_804335B8 as its own labeled bss symbol. Bytes match post-link. Function source structure is correct. Fuzzy 99.856%, strict 99.744%.
- **Tried:** prep + compact-brief diff inspection only; no source edits per CLAUDE.md (do not run permuter for permuter-false-positive class, do not attempt non-surgical fixes for cross-TU bss layout).
- **Likely fix:** TU-wide bss layout fix: force lbl_804335B8 into its own bss section so mwcc emits a separate symbol. See sibling lbMthp8001F928 note for full options. Single-function edits cannot bridge this — needs cross-TU coordinated work on the lbmthp.c bss layout.
