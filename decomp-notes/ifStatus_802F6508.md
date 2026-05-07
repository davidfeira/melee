---
function: ifStatus_802F6508
tu: src/melee/if/ifstatus.c
headline: regalloc + header-required
tags: [regalloc, header-required, permuter-dispatched]
---
## ifStatus_802F6508 (`src/melee/if/ifstatus.c`) — regalloc + header-required

- **Tags:** `regalloc`, `header-required`, `permuter-dispatched`
- **Best fuzzy:** 78.4235%
- **Diagnosis:** State pointer (IfDamageState*) allocated to volatile r4 instead of saved r28; compiler saves only 3 GPRs (r29-r31) instead of 4 (r28-r31). Root cause: MWCC does not allocate saved register r28 for the state pointer even though target does. Related issue: constant gen for 0xFFFF uses 'lis r3,1; subi r0,r3,1' vs target's 'li r0,-1'. Header change needed: ifStatus_802F5EC0 and ifStatus_802F61FC both take (IfDamageState*, u8) args not void.
- **Tried:** 1) Initial implementation with u8 temp_r30 and named field access: 78% match. 2) Changed to int temp_r30: 87.78% match (39 mismatches). Permuter launched from both bases, found score 300 and 500 but didn't reach 0. Core issue: 4 saved registers vs 3.
- **Likely fix:** Permuter needs more time. Try explicit register count forcing by adding a dummy fourth saved variable (e.g., a char* or int) that cross function call boundaries.

