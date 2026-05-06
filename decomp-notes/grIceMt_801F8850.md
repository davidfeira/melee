---
function: grIceMt_801F8850
tu: src/melee/gr/gricemt.c
headline: permuter-queued
tags: [permuter-queued]
---
## grIceMt_801F8850 (`src/melee/gr/gricemt.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** 84.6235%
- **Diagnosis:** 99.96% match (3 mismatches, all stack offsets). Source shape mirrors matched sibling grIceMt_801F8208 (same prologue/epilogue, same call to grIceMt_801F8CDC with 4 joint_indices). Stack frame size correct (0x28), but mwcc places joint_indices[4] at sp+0x18 instead of sp+0x14 (target). Tried with and without u32 unused[2], with extra HSD_JObj* locals -- none affect placement of the s16 array. Reg-allocation/local-ordering quirk that permuter should rotate.

