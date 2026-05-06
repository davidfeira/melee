---
function: grIceMt_801F8208
tu: src/melee/gr/gricemt.c
headline: permuter-queued
tags: [permuter-queued]
---
## grIceMt_801F8208 (`src/melee/gr/gricemt.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** 84.6235%
- **Diagnosis:** 99.96% (3 instr). Sources structurally correct: stack frame size matched at 0x28, all 13 missing instructions reconstructed (UnkFlagStruct b0=0, joint_indices[4] copied via *(u32*)& from grIm_804DB590/594, grIceMt_801F8CDC call). Remaining diff: s16 joint_indices[4] is allocated at 0x18(r1) instead of target's 0x14(r1) — local stack slot ordering with adjacent u32 unused[2] block. Pure stack layout permutation. Source uses 'extern const u32 grIm_804DB590; extern const u32 grIm_804DB594;' externs (sdata2) and casts &joint_indices[0..2] to (u32*) for the load+store — matches asm pattern of two lwz/stw word loads from sdata2. Sibling functions grIceMt_801F7D94 and grIceMt_801F7F70 share the same idiom and are also unmatched (concurrent agent already added 7D94 with same approach).

