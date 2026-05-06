---
function: ftKb_SpecialN_800EF69C
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: permuter-territory + r30-r31-swap
tags: [permuter-territory, r30-r31-swap, regalloc]
---
## ftKb_SpecialN_800EF69C (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — permuter-territory + r30-r31-swap

- **Tags:** `permuter-territory`, `r30-r31-swap`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Source structure matches: 91.66%, 53 mismatches dominated by a persistent register-allocation swap (target uses r30=fp, r31=off, r29=i; base uses r31=fp, r29=off, r30=i). The same swap propagates through ~50 of the 53 diffs as DIFF_ARG_MISMATCH. One real structural diff: target has 'addi r3, r4, 0x9; lbz r3, 0x0(r3)' (2 instr) where base emits 'lbz r4, 0x9(r3)' (1 instr) for the byte-9 load inside the inner if-else - suggests the source uses an intermediate u8* pointer to byte 9 that the compiler does not fold.
- **Tried:** (1) m2c-style placeholder with FighterBone struct + bitfield accesses: 86.97%; (2) raw u8* byte access avoiding bitfield optimizations: 87.575%; (3) added explicit 0x1FC mask on bone[0xD]*2: 88.575%; (4) used struct flags_b6/flags2_b7 bitfields and 0x1FC byte-offset for x203C/dobj_list array indexing: 91.49%; (5) raw bytes for xD multiplier path to avoid 7-bit bitfield optimization: 91.66%.
- **Likely fix:** Permuter on r30/r31 swap (variable lifetime ordering) plus structural variant for the byte-9 load (e.g., 'u8* p = (u8*) bone + 9; b9 = *p;' or accessing as a struct member through pointer arithmetic). decomp-permuter offline per task instructions; defer dispatch.

