---
function: mnDataDel_8024EA6C
tu: src/melee/mn/mndatadel.c
headline: struct-split + header-required
tags: [struct-split, header-required, data-anchor]
---
## mnDataDel_8024EA6C (`src/melee/mn/mndatadel.c`) — struct-split + header-required

- **Tags:** `struct-split`, `header-required`, `data-anchor`
- **Best fuzzy:** 91.092%
- **Diagnosis:** Reached 89.7%/87.8% with structural decomp. Same struct-split blocker as mnDataDel_8024E940: target asm uses mnDataDel_803EF8AC@ha as a distinct symbol anchor (= &mnDataDel_803EF870 + 0x3C), but the static.h MnDataDelData struct merges x0..x6C into one object so mwcc emits mnDataDel_803EF870@ha + 0x3C instead. Additional differences: target hoists 1.0f into f30 outside the loop and saves r29 (loop counter), r30 (idx ptr), r31 (user_data) — 3 GPRs + 2 FPRs preserved (stack 0x48); base allocates 2 GPRs + 1 FPR (stack 0x28) because register pressure is lower without the f30 hoist. The hoisting and 3rd GPR allocation likely cascade from the symbol-anchor choice (longer addressing sequence freeing/binding more registers). Fixing requires the same TU-wide struct refactor flagged in mnDataDel_8024E940 notes — splitting MnDataDelData into separate statics for x0..x2C, mnDataDel_803EF8A0, and mnDataDel_803EF8AC trailing array. Impacts already-matched fn_8024FBA4, fn_8024FC48, fn_8024FD40, mnDataDel_8024EBC8.

