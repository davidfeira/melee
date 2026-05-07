---
function: mnSoundTest_8024BEE0
tu: src/melee/mn/mnsoundtest.c
headline: tu-wide-data + string-pool
tags: [tu-wide-data, string-pool, data-anchor]
---
## mnSoundTest_8024BEE0 (`src/melee/mn/mnsoundtest.c`) — tu-wide-data + string-pool

- **Tags:** `tu-wide-data`, `string-pool`, `data-anchor`
- **Best fuzzy:** 56.9531%
- **Diagnosis:** Function uses mnSoundTest_803EF0A8 + 0x480/0x498/0x4B4/0x4D4 as string pointers for lbArchive_LoadSections. Current source compiles to ...data.0 offsets (0x47C/0x494/0x4B0/0x4D0) - 4 bytes short - because floats_2 is f32[2] in source vs f32[3] ({-1.7, 2, 0}) in target DOL (verified by reading DOL at 0x803EF0A8+0x60 = 0x00 00 00 00 pad after the 2 floats). The 4-byte deficit in floats_2 makes ...data.0 string offsets 4 less than needed. Beyond the offset, the compiler emits ...data.0 (anonymous section base) not mnSoundTest_803EF0A8 (named symbol) because the source declares individual vec_0..vec_7/floats_2/text_ids/data_2/data_3/data_4 instead of one combined mnSoundTest_803EF0A8[] array. Target requires ALL sibling functions to use mnSoundTest_803EF0A8+offset addressing (verified: target .o uses mnSoundTest_803EF0A8 everywhere; base .o uses ...data.0 everywhere).
- **Tried:** Attempt 1 (53.4%): String-literal args to lbArchive_LoadSections. Confirmed 4-byte offset discrepancy from floats_2 being 2-float instead of 3-float. Confirmed ...data.0 naming blocker.
- **Likely fix:** Full TU data restructure: (1) change floats_2 from {-1.7, 2} to {-1.7, 2, 0} to add 4 bytes; (2) declare entire data block as mnSoundTest_803EF0A8[] combining vec_0..vec_7 (8 Vec3), floats_2 (3 f32), text_ids (80 u8), data_2 (80 soundtest_data), data_3 (30 u8 + 6 pad), data_4 (60 u32), debug strings, and lbArchive strings at offsets 0x480/0x498/0x4B4/0x4D4; (3) update ALL sibling function source references from vec_N/text_ids/data_2/etc to mnSoundTest_803EF0A8 offset-based pointers. This is a multi-function coordinated rewrite for the whole TU.

