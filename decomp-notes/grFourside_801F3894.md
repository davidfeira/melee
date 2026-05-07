---
function: grFourside_801F3894
tu: src/melee/gr/grfourside.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## grFourside_801F3894 (`src/melee/gr/grfourside.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 97.8% match after 1 attempt. Logic is correct. Remaining 33 mismatches are all register allocation (r27/r28/r29/r30 swap, frame size 0x30 vs 0x28) plus 2 extsh instructions from s16 prob variable spilling through u16 struct fields. Permuter launched locally to resolve.
- **Tried:** Direct decomp from m2c + asm analysis. Added cm/camera.h include. Fixed variable declaration order for C89.
- **Likely fix:** Permuter should resolve register allocation. extsh may need struct field types changed to s16 (x46/x48) if permuter stalls.

