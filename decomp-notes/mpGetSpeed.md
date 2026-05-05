---
function: mpGetSpeed
tu: src/melee/mp/mplib.c
headline: tu-data-osreport + cross-tu-globals
tags: [tu-data-osreport, cross-tu-globals]
---
## mpGetSpeed (`src/melee/mp/mplib.c`) — tu-data-osreport + cross-tu-globals

- **Tags:** `tu-data-osreport`, `cross-tu-globals`
- **Best fuzzy:** 99.9784%
- **Diagnosis:** 11 ARG_MISMATCH, all reloc-symbol false-positives. Target anchors OSReport string args via mpLib_803BD3D8 + offsets 0x20D8/0x20F4/0x211C; base uses proper inline 'mplib.c' + format-string locals. Float consts (0.0f / 10000.0f) anchor via mpLib_804D8050 / mpLib_804D80AC@sda21 in target vs @415/@3542 locals in base. Function instructions and control flow already match exactly; only relocs differ. Fuzzy 99.978%, strict 99.583%.
- **Tried:** Manual diff inspection only — no source-shape attempts since the function source is already correct (m2c output matches existing structure), and all mismatches are data-symbol references not bridgeable from inside a single function.
- **Likely fix:** TU-wide multi-symbol refactor: declare all mpLib_804Dxxxx sdata2 statics (the .0f / 10000.0f / etc literal anchors) and restructure the mpLib_803BD3D8 string pool so mwcc anchors OSReport's 'mplib.c' / format strings off the same symbol the target uses. Same pattern as it_80274DAC (it_2725.c sdata2 anchors) and Exception_ReportStackTrace (lbl_8040AB00 anchor). Beyond single-function scope.
