---
function: grIceMt_801FA0BC
tu: src/melee/gr/gricemt.c
headline: permuter-queued + data-anchor
tags: [permuter-queued, data-anchor, regalloc, inlining]
---
## grIceMt_801FA0BC (`src/melee/gr/gricemt.c`) — permuter-queued + data-anchor

- **Tags:** `permuter-queued`, `data-anchor`, `regalloc`, `inlining`
- **Best fuzzy:** 73.8588%
- **Diagnosis:** At 99.71% (9 mismatches) after manual decomp + #pragma dont_inline on grIceMt_801F71E8 definition + PAD_STACK(0x18). Body and control flow match exactly. Remaining 9 splits: (a) 4x addi r3, r30, 0x690 vs 0x178 — the 'mgobj' assert string anchored via &grIm_803E4068 base is at a different .data offset because the TU's data layout still differs (data-anchor false-positive class); (b) 5x r28 vs r30 register allocation for the cleanup-loop ptrs base (&gp->xC8) — pure regalloc, permuter material.
- **Tried:** (1) Plain manual decomp -> 73% (compiler inlined grIceMt_801F71E8 since callsite is below def). (2) #pragma dont_inline on caller -> 66% (broke static inline of HSD_JObjSetTranslateY). (3) #pragma inline_depth(0)/(1) on caller -> regressed. (4) #pragma push/dont_inline on around grIceMt_801F71E8 DEFINITION -> 99.63% (no other callers below def, safe). (5) +PAD_STACK(0x18) -> 99.71%, 9 mismatches.
- **Likely fix:** Permuter to swap r28<->r30 in the second branch should clear 5 regalloc mismatches. The 4 data-anchor mismatches are layout-driven and should resolve once neighboring TU functions land — they reflect 'mgobj' string position relative to grIm_803E4068, which depends on prior-fn data emit order in this TU.

