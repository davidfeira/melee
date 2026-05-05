---
function: AXDriver_8038BF6C
tu: src/sysdolphin/baselib/axdriver.c
headline: regalloc + stack-offset
tags: [regalloc, stack-offset, sdata-anchor]
---
## AXDriver_8038BF6C (`src/sysdolphin/baselib/axdriver.c`) — regalloc + stack-offset

- **Tags:** `regalloc`, `stack-offset`, `sdata-anchor`
- **Best fuzzy:** 99.5765%
- **Diagnosis:** Baseline 99.454544 strict, 58 mismatches. Remaining blockers are FPR allocation and stack temps in the sqrt mix block, sdata literal symbol anchors, and initial flag r3/r4 swap.
- **Tried:** PAD_STACK(4) regressed to 111 mismatches/frame size change; inlining left_inv_sqrt*left_inv_sqrt*right_sqrt reduced count to 55 but lowered score to 98.82262 and kept stack/regalloc drift; removing right_inv_sqrt temp regressed to 138 mismatches.
- **Likely fix:** Needs targeted source-shape/permuter search around mix sqrt temporaries and loop flag load order, not a TU data-anchor fix.
