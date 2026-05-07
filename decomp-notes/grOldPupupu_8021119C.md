---
function: grOldPupupu_8021119C
tu: src/melee/gr/groldpupupu.c
headline: regalloc + r30-r31-swap
tags: [regalloc, r30-r31-swap, instruction-scheduling]
---
## grOldPupupu_8021119C (`src/melee/gr/groldpupupu.c`) — regalloc + r30-r31-swap

- **Tags:** `regalloc`, `r30-r31-swap`, `instruction-scheduling`
- **Best fuzzy:** 85.6897%
- **Diagnosis:** All 30 mismatches are pure register allocation: target uses r30=gobj, r31=gp, r28=max, r29=min; our compiled output uses r28=gobj, r29=gp (or variants), with max/min in r0/r31/r30. Function structure and control flow are now correct (rnd variable with explicit else-0 in both branches matches m2c pattern). The mr r3, r0 vs li r3, 0 issue is resolved with the rnd+else-0 reshape. Remaining 30 mismatches are entirely regalloc: mwcc assigns r28 to gobj instead of r30, cascading through all struct accesses and the prologue save order.
- **Tried:** V1 (79.22%): original code with max=min+HSD_Randi(range) in if-branch. V2 (85.69%): rnd variable + explicit else-0 in both branches; gp declared after max/min. V3 (85.69%): same but gp declared last. Declaration order does not affect regalloc. mwcc consistently puts gobj in r28 instead of r30 regardless of declaration ordering.
- **Likely fix:** Permuter-territory: need to coax mwcc to assign r30 to gobj and r31 to gp. Possible approaches: volatile cast, different initialization order, or an intermediate variable indirection on gobj. The true fix may require a differently-shaped loop/early-exit pattern that creates different liveness intervals for the pointer variables.

