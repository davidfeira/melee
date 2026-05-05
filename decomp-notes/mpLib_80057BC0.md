---
function: mpLib_80057BC0
tu: src/melee/mp/mplib.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## mpLib_80057BC0 (`src/melee/mp/mplib.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 99.7719%
- **Diagnosis:** One strict mismatch remains: target emits addi r3,r30,0 before mpIsland_8005B334, base emits mr r3,r30.
- **Tried:** Tried joint_id + 0 and copying joint_id through the existing start local before the call; both stayed at 99.771866% with the same one mismatch.
- **Likely fix:** Needs permuter or a source shape that forces an addi copy for the first call argument without perturbing the surrounding unrolled loops.
