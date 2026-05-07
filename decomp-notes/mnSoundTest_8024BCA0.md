---
function: mnSoundTest_8024BCA0
tu: src/melee/mn/mnsoundtest.c
headline: data-anchor + tu-wide-data
tags: [data-anchor, tu-wide-data, frame-size, sdata2-float]
---
## mnSoundTest_8024BCA0 (`src/melee/mn/mnsoundtest.c`) — data-anchor + tu-wide-data

- **Tags:** `data-anchor`, `tu-wide-data`, `frame-size`, `sdata2-float`
- **Best fuzzy:** 92.8819%
- **Diagnosis:** At 97.06% (30 mismatches) with correct body structure. r31=mnSoundTest_803EF0A8 base held throughout. Main blockers: (1) frame-size 0x50 vs 0x28 — compiler allocates only 0x28 frame even though target needs 0x50 with sp24 at 0x24; likely needs additional dummy locals or the xoris/int-to-float fix forces a larger temp area; (2) data-anchor: 4 reloc offsets off by 4 bytes (0x33c vs 0x338, 0x35c vs 0x358, 0x44c vs 0x448, 0x464 vs 0x460, 0x474 vs 0x470) because current source anchor ...data.0 is 4 bytes past mnSoundTest_803EF0A8 — same tu-wide-data issue as fn_8024B7E4; (3) 0.0f for HSD_JObjReqAnimAll generates 0x0(r31) data-section load instead of mnSoundTest_804DC0E4@sda21 — vec_0.x gives data ref, plain 0.0f literal gives anonymous sda21 slot; (4) int-to-float for (f32)data_4[idx] missing xoris r4,r4,0x8000 — need (s32) cast or s32 array type; (5) unk10 NULL check generates lwz-to-r0 + cmplwi r0 + mr r3,r0 instead of lwz-to-r3 + cmplwi r3.
- **Tried:** Attempt 1: used separate element accesses for mnSoundTest_804A08C8 and data_3/data_4 — wrong structure, 92.6% (42 mismatches). Attempt 2: introduced void** temp_r29=mnSoundTest_804A08C8 to force early r29 load, used vec_0.x for 0.0f (wrong: gives data ref), used (f32)data_4[idx] without s32 cast (missing xoris). Got to 97.06% (30 mismatches).
- **Likely fix:** Same TU-wide consolidation as fn_8024B7E4: collapse vec_0..vec_7 + floats_2 into mnSoundTest_803EF0A8[] array (removing #if 0 guard and extending to 9 Vec3s). Additionally: (1) fix data_4 type to s32[] or add (s32) cast for xoris; (2) for 0.0f in HSD_JObjReqAnimAll, use the computation (f32)(0 == 0) or another pattern that maps to mnSoundTest_804DC0E4@sda21; (3) frame-size fix may resolve itself once anchor is correct.

