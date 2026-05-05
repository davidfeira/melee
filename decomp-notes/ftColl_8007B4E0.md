---
function: ftColl_8007B4E0
tu: src/melee/ft/ftcoll.c
headline: regalloc
tags: [regalloc]
---
## ftColl_8007B4E0 (`src/melee/ft/ftcoll.c`) — regalloc

- **Tags:** `regalloc`
- **Best fuzzy:** 96.7647%
- **Diagnosis:** 30 mismatches, all pure regalloc (r5/r6 and r10/r11 swap pairs). Target writes hurt_capsules base via r5, inits via r6+r10/r11; base swaps to r6/r5 and r10/r11. Adding FighterHurtCapsule* hurt local did not change codegen. >15 instr so above auto-permute threshold, but single-class regalloc is permuter territory — eligible for cluster dispatch.
- **Tried:** (1) introduce FighterHurtCapsule* hurt = &fp->hurt_capsules[i] local pointer to mirror ftColl_HurtboxInit shape — same 30 mismatches.
- **Likely fix:** Cluster permuter run; manual approaches won't shift register pairs without an unrelated source change.
