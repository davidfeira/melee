---
function: gmCamera_801A2BF0
tu: src/melee/gm/gmcamera.c
headline: permuter-queued + r30-r31-swap
tags: [permuter-queued, r30-r31-swap, frame-size, sdata2-float, regalloc]
---
## gmCamera_801A2BF0 (`src/melee/gm/gmcamera.c`) — permuter-queued + r30-r31-swap

- **Tags:** `permuter-queued`, `r30-r31-swap`, `frame-size`, `sdata2-float`, `regalloc`
- **Best fuzzy:** 90.6941%
- **Diagnosis:** At 94.19% (29 mismatches). Function logic correct: lb_80011E24 + HSD_JObjReqAnimAll/AnimAll + HSD_ForeachAnim, then gcus->x18=0, second lb_80011E24, HSD_JObjSetTranslateX. Target compiler chose to keep TWO base pointers (r31=&gcus, r30=&gcus->x8) and used stwu r0,0x18(r31) to store gcus->x18=0 while advancing r31. My base uses single r31 with separate stw. Diffs are register allocation (r30 vs r31), stack frame +8 bytes (r30 spill), and 4 sdata2-float local-vs-named labels (likely link-equivalent false positives for 5.0f/-5.0f/1.0f/2.0f). This is exactly the kind of regalloc/scheduling diff the permuter handles.
- **Tried:** (1) gcus local pointer, (2) inlined gmCamera_80479BC8.gcus.x8 expressions
- **Likely fix:** Permuter regalloc/scheduling pass; target uses stwu pattern with r30=&gcus->x8 pre-saved, current source produces single-register pattern. Compiler heuristic differs by ~1 spill register. Worth trying source variations that hint at &gcus->x8 reuse, or hand-tweak via permuter randomizer.

