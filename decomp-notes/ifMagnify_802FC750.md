---
function: ifMagnify_802FC750
tu: src/melee/if/ifmagnify.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## ifMagnify_802FC750 (`src/melee/if/ifmagnify.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 86.2143%
- **Diagnosis:** Loop with 3 induction vars (i, ptr, offset). Target uses 5 callee-save regs (r26-r30) with stmw r26; base uses 4 (r27-r30) with stmw r27. Target also emits slwi r28,r26,4 (offset = i<<4 hoisted) which base does not. Remaining diff after best variant is 5 register-allocation/init-order mismatches.
- **Tried:** (1) Permuter-discovered shape: re-assign u8* new_var = (u8*)base inside loop body before deref. Drops mismatches 17->5 (82.1%->88.4%). Permuter score 260 (down from 475 baseline). (2) Initialize offset = i<<4 before loop with i=0 separately initialized: regressed to 14 mismatches; mwcc folds away.
- **Likely fix:** Pure regalloc/scheduling territory after applying new_var hoist; dispatch permuter on the new_var variant to push from 5 mismatches to 0. The slwi suggests target source has offset expressed via i*16 somewhere that mwcc preserves only when i is referenced after init.
