---
function: grGreens_802150C4
tu: src/melee/gr/grgreens.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc]
---
## grGreens_802150C4 (`src/melee/gr/grgreens.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 96.8% match after 2 attempts. All 64 mismatches are register allocation differences: target uses r5 for x8_blocks base and r6/r4 for column offsets; compiled code uses r4/r5/r3/r6. Code structure is semantically correct and matches target instruction pattern exactly (deferred cur_col computation, 4 diagonal sections each reloading base from gp->gv.greens.x8_blocks). Local permuter ran 152 iterations, reached score 455 (base 525). Permuter dispatch toggle is OFF in viz.
- **Tried:** (1) u8* base pointer cached at function start; (2) u32 base reloaded per section with deferred cur_col computation. Both semantically correct, structural issue was cur_col ordering.
- **Likely fix:** Permuter should find the register allocation match. The function uses raw byte pointer arithmetic on x8_blocks array with direct offset computations. No structural changes needed.

