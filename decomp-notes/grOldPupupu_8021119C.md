---
function: grOldPupupu_8021119C
tu: src/melee/gr/groldpupupu.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## grOldPupupu_8021119C (`src/melee/gr/groldpupupu.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 79.2241%
- **Diagnosis:** Permuter plateaued at score 1135 (79.22%, 34 mismatches). Mismatches are register-allocation: base holds gobj in r28 across the ftCo_800C06E8 call and gp in r30 (final stw r31, 0xd0(r30)), with r31 reused as the 'max result' working register through the if/else-if. Current source compiles to gobj in r30, gp in r31, and uses r28/r29 for max/min, producing 22 regalloc + 11 'real' diffs (insertions/deletions of stw r28/r29 prologue saves and shifted branch offsets cascade from the regalloc choice). Function structure and control flow are correct.
- **Tried:** V1: introduced separate 'a','b' temp scoped block before max/min; mwcc CSE'd back to identical 79.22% / 34 mismatches. V2: introduced explicit 'result' variable initialized to max, mutated only inside branches; got 79.05% (slightly worse), still 34 mismatches.
- **Likely fix:** Need to coax mwcc to keep gobj in a callee-saved early-pressure slot (r28) and use r31 as the working accumulator. Possible angles: reorder ftCo_800C06E8 call vs gp deref, manual gobj caching in a local before the call, or reshape the if-chain to make max-as-result more obvious. Also possible the true source uses a different intermediate-var layout (e.g. write to gp->gv.unk.xD0 inside each branch instead of accumulating into 'max').
