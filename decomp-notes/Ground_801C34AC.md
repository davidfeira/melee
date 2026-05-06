---
function: Ground_801C34AC
tu: src/melee/gr/ground.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-dispatched]
---
## Ground_801C34AC (`src/melee/gr/ground.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-dispatched`
- **Best fuzzy:** 90.137%
- **Diagnosis:** At 90.14% (41 mismatches) after manual decomp. Bulk of remaining diff is r28/r29/r30/r31 regalloc swap — clear permuter territory. One structural concern: source uses phi_r3[i] array indexing inside the joint-walk loop, which mwcc emits as mulli r0,r6,0xc + add r3,r5,r0 per iteration; target advances a pointer by addi r6,r6,0xc (single instruction). Source should be rewritten to advance phi_r3 by 12 bytes per iter rather than indexing. After that, permuter on regalloc likely closes the gap.

