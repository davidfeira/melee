---
function: gm_801BAC9C
tu: src/melee/gm/gm_1BA8.c
headline: regalloc + stack-offset
tags: [regalloc, stack-offset, frame-size]
---
## gm_801BAC9C (`src/melee/gm/gm_1BA8.c`) — regalloc + stack-offset

- **Tags:** `regalloc`, `stack-offset`, `frame-size`
- **Best fuzzy:** 96.566%
- **Diagnosis:** At 97.60%, 18 DIFF_ARG_MISMATCH mismatches. Two blockers: (1) stack-offset: buf array must be at r1+0x18 (target) but our best achieves either buf@0x18 with frame=0x48 [PAD_STACK(8)] or buf@0x20 with frame=0x50 [PAD_STACK(0x10)]; target needs BOTH buf@0x18 AND frame=0x50 - no PAD_STACK value achieves this; the extra 8-byte gap (0x39..0x47) between buf end and saved r30@0x48 is unexplained. (2) regalloc: 16 register allocation mismatches: dst=r9(need r6), found=r10(need r11), i=r11(need r9), list=r8(need r12), matches=r12(need r10).
- **Tried:** PAD_STACK(0x10): correct frame=0x50, buf@0x20 wrong. PAD_STACK(8): buf@0x18 correct, frame=0x48 wrong (+8 bytes short). Two PAD_STACK(8): same as PAD_STACK(0x10). Nested block PAD_STACK: same result. (int) cast for sentinel comparison: fixed cmpwi vs cmplwi mismatch.
- **Likely fix:** Need to understand what causes the extra 8 bytes in the target frame (r1+0x39..0x47 gap) - possibly a spilled temporary or an additional u8/int local at stack offset 0x40 that isn't visible in the matched asm. Regalloc is pure permuter territory once frame-size is resolved.

