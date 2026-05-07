---
function: HSD_Synth_8038ADD0
tu: src/sysdolphin/baselib/synth.c
headline: regalloc + mwcc-branch-inversion
tags: [regalloc, mwcc-branch-inversion, struct-typing]
---
## HSD_Synth_8038ADD0 (`src/sysdolphin/baselib/synth.c`) — regalloc + mwcc-branch-inversion

- **Tags:** `regalloc`, `mwcc-branch-inversion`, `struct-typing`
- **Best fuzzy:** 88.8774%
- **Diagnosis:** Function reaches 94.85% (47 mismatches in 212 instructions). Dominant issue is systematic r27/r28 register allocation swap for cur_block vs loop counter i. Secondary structural issues: (1) getNode inline generates beq+extra-b instead of target bne+b pattern (mwcc-branch-inversion for && condition); (2) loop-2b ADPCM loop init uses slwi-r,i,3 (i*8) rather than target's (i*2+3)*4 pattern (i*8+12 precomputed). Static header needed struct updates: lbl_804C4540 x8 field changed from s32 to u32 (addis+cmplwi -1 check), adpcmloop array added with 8-byte stride (AXPBADPCMLOOP + u16 pad per element). HSD_Synth_804D7770 extern changed from s32 to u32 to get mulhwu for modulo-3 ops.
- **Tried:** Attempt 1: initial m2c-based implementation with local cur_block, 83.9%. Attempt 2: changed loop body to use HSD_Synth_804D7774 (extern reload) instead of cur_block register in loop, fixed u32/s32 types for HSD_Synth_804D7770 and x8 struct field, 94.85%. Declaration reordering did not resolve r27/r28 swap.
- **Likely fix:** Permuter for r27/r28 regalloc swap (39 of 47 mismatches). Structural fixes needed first: (1) resolve beq/bne inversion in getNode inline - try restructuring outer if-null/if-flags as separate nested ifs; (2) loop-2b adpcmloop access may need different C expression to produce (i*2+3)*4 pattern.

