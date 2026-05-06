---
function: gmCamera_801A2D44
tu: src/melee/gm/gmcamera.c
headline: permuter-territory + r30-r31-swap
tags: [permuter-territory, r30-r31-swap, instruction-scheduling]
---
## gmCamera_801A2D44 (`src/melee/gm/gmcamera.c`) — permuter-territory + r30-r31-swap

- **Tags:** `permuter-territory`, `r30-r31-swap`, `instruction-scheduling`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 96.87% (22 mismatches). Source shape semantically correct: pad 0x18 stack frame matches via PAD_STACK(24), gcus pointer alias hoists r31, jobj at sp+0x24 / jobj_b at sp+0x20. Remaining diffs are pure register allocation: target uses r30 as alias for both &gcus.x18 and the loaded HSD_JObj* (lifetimes don't overlap), while mwcc on my source allocates r31 to the loaded jobj ptr. Adding 'u32* p = &gcus->x18;' alias (96.26%, 20 mm) produces the right addi r30,r31,0x18 instruction but schedules it after lbAudioAx call instead of before. Non-aliased version (96.87%) is cleaner.
- **Tried:** (1) baseline m2c-shape with PAD_STACK(8) -> 92.5%; (2) gcus pointer alias + (s32) cast on x18 + PAD_STACK(24) -> 96.87%; (3) added u32* p = &gcus->x18 inside both branches -> 96.26% (instruction scheduling regression, alias is computed correctly but emitted later).
- **Likely fix:** Permuter should solve r30/r31 swap + instruction reordering trivially. The non-aliased PAD_STACK(24) version (without u32* p alias) at 96.87% is the best handoff candidate.

