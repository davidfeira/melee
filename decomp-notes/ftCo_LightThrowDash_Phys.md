---
function: ftCo_LightThrowDash_Phys
tu: src/melee/ft/chara/ftCommon/ftCo_ItemThrow.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## ftCo_LightThrowDash_Phys (`src/melee/ft/chara/ftCommon/ftCo_ItemThrow.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 99.0741%
- **Diagnosis:** 5-instruction pure register allocation mismatch: compiler assigns r4 to p_ftCommonData pointer, target uses r6. All other instructions are identical. Both attempts (swap declaration order with local cd variable, and remove local cd variable to use p_ftCommonData inline) produced identical r4 output. MWCC's register allocator is making a fixed choice regardless of source shape.
- **Tried:** 1) Swapped declaration order (cd before fp) + fixed else branch to use cd consistently. 2) Removed cd local variable entirely, used p_ftCommonData inline throughout both branches.
- **Likely fix:** Permuter is the right tool here - it can shuffle temps/expression order to nudge MWCC into choosing r6 over r4 for the global pointer load. Manual structural changes cannot influence this allocation.

