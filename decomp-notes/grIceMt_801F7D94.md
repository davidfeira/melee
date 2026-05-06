---
function: grIceMt_801F7D94
tu: src/melee/gr/gricemt.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-territory]
---
## grIceMt_801F7D94 (`src/melee/gr/gricemt.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-territory`
- **Best fuzzy:** 86.6626%
- **Diagnosis:** At 99.61%, 4 mismatches. Source-shape correct (added bitfield clear ((UnkFlagStruct*)((u8*)gp+0xC4))->b0=0, joint_indices stack array, grIceMt_801F8CDC call with grIm_804DB588 sdata2 const). Stack offset matched by declaring s16 joint_indices[4] and passing &joint_indices[2] (bumps array to 0x14 like target). Remaining diff: register allocation swap r3<->r4 for the 'li 0x0' source (used in rlwimi for bitfield clear) vs arg0 setup. Pure scheduling/regalloc -- permuter territory.

