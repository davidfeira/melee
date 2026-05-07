---
function: gmMainLib_8015F150
tu: src/melee/gm/gmmain_lib.c
headline: regalloc + mwcc-loop-opt
tags: [regalloc, mwcc-loop-opt, instruction-scheduling, upstream-regression]
---
## gmMainLib_8015F150 (`src/melee/gm/gmmain_lib.c`) — regalloc + mwcc-loop-opt

- **Tags:** `regalloc`, `mwcc-loop-opt`, `instruction-scheduling`, `upstream-regression`
- **Best fuzzy:** 76.9706%
- **Diagnosis:** 77% match. Target uses r31=0x19 as a callee-saved inner-loop-bound constant compared via cmpwi r31,0x8 for CodeWarrior unroll threshold; base uses r0 for zero-constant in unrolled sth stores and r6 as the pointer base, while target uses r4 for zero and r3 for pointer. The index computation (clrlwi/mulli/add) is hoisted before the conditional in base but deferred to inside each branch in target. Upstream (PR #2410) submitted at 77% and marked matched.
- **Tried:** (1) Changed outer loop var from s32 to u8 — degraded to 67%, extra callee-saved reg (r29), frame grew to -0x28. Reverted. Source is otherwise identical to upstream.
- **Likely fix:** Permuter territory: remaining mismatches are entirely register allocation (r4 vs r0 for zero-constant, r3 vs r6 for pointer) and instruction scheduling (index computation order relative to conditional branch). No source-shape change is likely to fix this without permuter.

