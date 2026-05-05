---
function: ftAction_80072CD8
tu: src/melee/ft/ftaction.c
headline: frame-size + stack-offset
tags: [frame-size, stack-offset]
---
## ftAction_80072CD8 (`src/melee/ft/ftaction.c`) — frame-size + stack-offset

- **Tags:** `frame-size`, `stack-offset`
- **Best fuzzy:** 99.6506%
- **Diagnosis:** Frame is 0x88 vs target 0x78 (0x10 too big). mwcc places sp2C (anon u32 struct) at 0x5c AFTER _cmd at 0x38, leaving a 0x14-byte gap. Target has sp2C at 0x2c IMMEDIATELY before _cmd at 0x38 (contiguous). All 24 remaining mismatches are stack-offsets cascading from this. Bit position issue (extrwi 24 vs 30) for use_alt_bone was the only 'real' diff and is fixed in src/melee/lb/types.h (struct footstep_fx_0: added x1_b0_5:6 padding before use_alt_bone, plus x1_b7:1 after, replacing the old x1_b1_7:7). Improved match 99.6506% -> 99.7108%.
- **Tried:** 1) Fixed footstep_fx_0 bitfield layout in types.h (use_alt_bone moved from bit 8 to bit 14, matching extrwi 1,30 in original). 2) Reordered local declarations (range/offset first, primitives last) - regressed to 99.64% with 30 mismatches; reverted. Source comment '@todo too much stack' already flags this.
- **Likely fix:** Header fix (footstep_fx_0 bitfield) needs to land - REPORT THIS AS HEADER CHANGE. For frame-size: try declaring sp2C as u32[3] array instead of anon struct, or move sp2C decl to tightest scope inside the inner if(sp64!=-1) block (currently file scope), or use union with _cmd. mwcc may treat anon-struct differently from typed locals for layout purposes.
