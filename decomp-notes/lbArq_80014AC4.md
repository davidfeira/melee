---
function: lbArq_80014AC4
tu: src/melee/lb/lbarq.c
headline: instruction-scheduling + regalloc
tags: [instruction-scheduling, regalloc, scheduler]
---
## lbArq_80014AC4 (`src/melee/lb/lbarq.c`) — instruction-scheduling + regalloc

- **Tags:** `instruction-scheduling`, `regalloc`, `scheduler`
- **Best fuzzy:** 96.9403%
- **Diagnosis:** Source is identical to upstream matched version but having lbArq_80014BD0 fully implemented in the same TU changes compiler codegen for the first prev=&global->list[node->state] computation. Base generates slwi r0,r0,2 / add r4,r30,r0 / addi r4,r4,0x1e0; target wants slwi r4,r0,2 / addi r4,r4,0x1e0 / add r4,r30,r4. Second occurrence in same function compiles correctly. The upstream matched with lbArq_80014BD0 as a stub only.
- **Tried:** 1) Removed global pointer variable (direct lbArq_804316C0 access) - much worse (35 mismatches). 2) Swapped node/global declaration order - same 6 mismatches. 3) Moved global= assignment after OSDisableInterrupts - same 6. 4) Used explicit u32 state=node->state intermediate - same 6.
- **Likely fix:** Stubbing lbArq_80014BD0 (/// #lbArq_80014BD0) would likely restore 100% match, consistent with upstream's approach. Alternatively, wait for lbArq_80014BD0 context to change or use permuter to find a scheduling hint.

