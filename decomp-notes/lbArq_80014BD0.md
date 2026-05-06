---
function: lbArq_80014BD0
tu: src/melee/lb/lbarq.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc]
---
## lbArq_80014BD0 (`src/melee/lb/lbarq.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 94% match (46 mismatches). Function logic confirmed correct. The remaining diff is pure register allocation: target keeps r31=&global, r28=rp; base chose r25=&global, r31=rp, with an extra 'mr r31, r0' insert (because base loaded list[0] into r0 first). The shift propagates throughout, causing all r25-r28 register references to differ. Frame size differs (-0x58 target vs -0x48 base) due to one extra live register slot. No structural source change is likely to flip mwcc's allocator choice; classic permuter territory. Source improvements kept (cleaned UNK_T types in header, captured callback signature). Tag permuter-queued unavailable; using permuter-territory.

