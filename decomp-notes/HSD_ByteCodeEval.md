---
function: HSD_ByteCodeEval
tu: src/sysdolphin/baselib/bytecode.c
headline: permuter-false-positive + sdata2-float
tags: [permuter-false-positive, sdata2-float, tu-wide-data, regalloc]
---
## HSD_ByteCodeEval (`src/sysdolphin/baselib/bytecode.c`) — permuter-false-positive + sdata2-float

- **Tags:** `permuter-false-positive`, `sdata2-float`, `tu-wide-data`, `regalloc`
- **Best fuzzy:** 99.9156%
- **Diagnosis:** 65 mismatches dominated by reloc-symbol false-positives. (1) Many sdata2 float lfs/lfd against HSD_ByteCode_804DE7A0..D0 vs target's @396@sda21 etc — same post-link bytes, different symbol naming for shared TU rodata floats (90.0F, -90.0F, RAD_TO_DEG, DEG_TO_RAD constants). (2) Many 'addi r5, r31, 0xN' entries with IDENTICAL printed text — data-anchor differences for OSReport/HSD_Panic format strings. (3) One real regalloc: case 0x26 (atan2f) at offset 2568-2572 has fnmsubs/stfs using f24 in target vs f25 in base — single-instruction regalloc swap on the -90.0F branch (f1 >= 0.0F ? 90.0F : -90.0F).
- **Tried:** Only triaged via compact-brief and diff. No source variants attempted: per CLAUDE.md rule 6 (Permuter Boundary), reloc-symbol-dominated diffs must NOT be sent to the permuter — its scorer treats these as equivalent (post-link bytes match) but report.json fuzzy does not.
- **Likely fix:** (a) Cross-TU rodata: HSD_ByteCode_804DE7A0..D0 globals likely originate from another bytecode-related TU. Need to identify and remove from this TU OR confirm source location (similar to tu-data-osreport pattern). (b) Format strings: 'specified stack doesn't exist (%d).\n', 'not yet implemented.\n', 'unexpected byte code.\n', 'stack', 'stack->next' string layout/dedup — possibly need __FILE__ vs literal 'bytecode.c' adjustments throughout. (c) f24/f25 regalloc: probably needs spurious temp or reordering of the -90.0F vs 90.0F selection in case 0x26.
