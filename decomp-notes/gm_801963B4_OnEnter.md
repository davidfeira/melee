---
function: gm_801963B4_OnEnter
tu: src/melee/gm/gm_18A5.c
headline: data-anchor + data-symbols-missing
tags: [data-anchor, data-symbols-missing, sdata-anchor, sdata-symbols-missing, permuter-false-positive]
---
## gm_801963B4_OnEnter (`src/melee/gm/gm_18A5.c`) — data-anchor + data-symbols-missing

- **Tags:** `data-anchor`, `data-symbols-missing`, `sdata-anchor`, `sdata-symbols-missing`, `permuter-false-positive`
- **Best fuzzy:** 99.8667%
- **Diagnosis:** 12 instruction mismatches: 10 are data-anchor (lbl_803D9F80@ha/l vs data.0@ha/l, offset differences of 0x208) and 2 are sdata named-vs-anonymous (@2566/@2568@sda21 vs lbl_804D4180/lbl_804D4188@sda21 for GmTou1p/GmTou2p strings). Root cause: the TU is missing ~10 data symbol definitions (lbl_803D9F80 size 0x58, lbl_803D9FD8 size 0x4C, lbl_803D9F18, lbl_803D9F5C, lbl_803D9F68, lbl_803D9F74, lbl_803D9EE8, lbl_803D9EF4, lbl_803D9F00). Without these, the compiler uses data.0 as base instead of lbl_803D9F80. Post-link bytes are identical; pre-link relocations differ.
- **Tried:** 1) Applied upstream GXColor spacing change (no effect on this function). 2) Analyzed full data section layout: target .data is 0x5C0 bytes vs our 0x35E bytes; lbl_803D9F80 is at target offset 0x260, strings at 0x320 (delta 0xc0), but these symbols are extern-only in our source. sdata: GmTou1p/GmTou2p compile as anonymous @2566/@2568 at wrong sdata offsets.
- **Likely fix:** Define all missing data symbols (lbl_803D9F80=0x58 bytes, lbl_803D9FD8=0x4C bytes, lbl_803D9F18/5C/68/74 strings, lbl_803D9EE8/F4/F00 structs) in gm_18A5.c or .static.h with correct types and values to fix data layout. Also define lbl_804D4180/lbl_804D4188 as named sdata string variables. This is a whole-file data-layout problem, not a single-function fix.

