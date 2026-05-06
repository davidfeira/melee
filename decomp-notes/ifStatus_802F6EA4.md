---
function: ifStatus_802F6EA4
tu: src/melee/if/ifstatus.c
headline: permuter-blocked + regalloc
tags: [permuter-blocked, regalloc, literal-pool]
---
## ifStatus_802F6EA4 (`src/melee/if/ifstatus.c`) — permuter-blocked + regalloc

- **Tags:** `permuter-blocked`, `regalloc`, `literal-pool`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 98.2% (33 mismatches). Source structure correct: 8-branch (events with -1 arg, two SFX calls), else-branch (entry init, GObj/JObj setup, anim, x12 bit clears, store-back). Two remaining classes of mismatch: (1) register renumbering — target allocates entry=r27, sfx_b=r28, sfx_a/gobj=r29, ev_a=r30, ev_b=r31, but mwcc on my source picks r29/r27/r28/... — same shape, off-by-one. (2) Float literal 0.0f for HSD_JObjReqAnimAll loads from ifStatus_804DDAA8 (named sdata2 symbol) in target but @351 anonymous literal in base — TU literal-pool ordering, depends on other functions in TU. Both are classic permuter cases. Note: header signature for ifStatus_802F6EA4 changed from Event to void (*)(s32) (the function pointers are called with arg=-1, requiring a non-void signature).

