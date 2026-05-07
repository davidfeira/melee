---
function: SimplifySrc
tu: src/sysdolphin/baselib/texpdag.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-territory]
---
## SimplifySrc (`src/sysdolphin/baselib/texpdag.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-territory`
- **Best fuzzy:** 95.807%
- **Diagnosis:** 96.37% match after attempt 1. All 70 remaining mismatches are register allocation differences (r27/r30 for sel, r29/r27 for res, r30/r31 for i, r31/r29 for p; exp=r28 matches) and one load/store scheduling difference in the 0xFF case (target does load-load-store-store, base does load-store-load-store for the two-word write of HSD_TExpDag_804D5FF8/FFC).
- **Tried:** (1) m2c literal translation with for loops and word-store casts for HSD_TExpDag_804D5FF8. (2) Tried reordering variable declarations (p,res,i,exp,sel vs exp,p,sel,res,i) — former gave 96.37%, latter gave 95.77% with worse register mismatches.
- **Likely fix:** Permuter: need r31=p, r30=i, r29=res, r28=exp, r27=sel register allocation. Scheduling of the two stw instructions in the 0xFF fallthrough case.

