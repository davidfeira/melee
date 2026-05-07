---
function: grRCruise_80200B48
tu: src/melee/gr/grrcruise.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## grRCruise_80200B48 (`src/melee/gr/grrcruise.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 97.9787%
- **Diagnosis:** Pure register allocation mismatch: 17 mismatches all DIFF_ARG_MISMATCH swapping r26/r27 (i counter vs entry ptr) and r28/r29 (jobj temp vs gp). Target wants i=r26, entry=r27, jobj=r28, gp=r29; current code produces i=r28, entry=r26, jobj=r29, gp=r27 or similar permutations depending on declaration order. Struct and semantics are correct.
- **Tried:** 1) Explicit separate vars (i, arr, offset) before gp - broke symbol encoding (61%). 2) Swapped declaration order (s32 i before Ground* gp) - still 17 regalloc mismatches, just different register assignments.
- **Likely fix:** Permuter needed to find the declaration order / variable scoping that forces the compiler to assign r26=i, r27=entry, r28=jobj, r29=gp. Manual declaration reordering is insufficient — compiler considers liveness and use patterns holistically.

