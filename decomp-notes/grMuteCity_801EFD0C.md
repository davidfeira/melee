---
function: grMuteCity_801EFD0C
tu: src/melee/gr/grmutecity.c
headline: data-anchor + instruction-scheduling
tags: [data-anchor, instruction-scheduling, regalloc]
---
## grMuteCity_801EFD0C (`src/melee/gr/grmutecity.c`) — data-anchor + instruction-scheduling

- **Tags:** `data-anchor`, `instruction-scheduling`, `regalloc`
- **Best fuzzy:** 94.8814%
- **Diagnosis:** Target asm uses grMc_803E30B0 (0x803E30B0) as array base but source declares grMc_803E30C4 (0x803E30C4), offset by 0x14 (one StageCallbacks entry). This causes OSReport string offsets to be 0x14 too low (0x34c/0x370 vs expected 0x360/0x384) and missing the 'addi r29, r29, 0x14' instruction. Expanding to grMc_803E30B0[40] fixes string offsets but breaks callbacks pointer computation: &grMc_803E30B0[gobj_id + 1] causes compiler to compute gobj_id+1 before multiply (mulli r0, r0, 0x14) instead of mulli r0, r28, 0x14. Using &grMc_803E30B0[gobj_id] + 1 produces worse register allocation. The upstream match uses grMc_803E30C4[39] + &grMc_803E30C4[gobj_id] -- it is unclear how upstream achieves 100% since the asm clearly shows grMc_803E30B0.
- **Tried:** (1) Renamed array grMc_803E30C4[39] to grMc_803E30B0[40] with prepended NULL entry, changed callbacks = &grMc_803E30B0[gobj_id + 1] and StageData ref to &grMc_803E30B0[1] -- fixed string offsets but regressed to 92.8% due to mulli using wrong register. (2) Changed to &grMc_803E30B0[gobj_id] + 1 for pointer arithmetic style -- worse (89.1%).
- **Likely fix:** Need to find the expression that makes compiler emit: mulli r0, r28, 0x14; lis r3, grMc_803E30B0@ha; addi r31, r3, grMc_803E30B0@l; add r29, r31, r0; addi r29, r29, 0x14. Possible approach: declare separate s32 offset = gobj_id * sizeof(StageCallbacks) and add 0x14 manually, or use a volatile intermediate. Also check if a 1-entry padding struct/variable before grMc_803E30B0 in the data section could shift the address without changing the array size.

