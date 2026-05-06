---
function: mnSoundTest_8024BEE0
tu: src/melee/mn/mnsoundtest.c
headline: tu-wide-data + cross-function-rodata
tags: [tu-wide-data, cross-function-rodata, string-pool, permuter-blocked]
---
## mnSoundTest_8024BEE0 (`src/melee/mn/mnsoundtest.c`) — tu-wide-data + cross-function-rodata

- **Tags:** `tu-wide-data`, `cross-function-rodata`, `string-pool`, `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** lbArchive_LoadSections call references string literals at fixed offsets within mnSoundTest_803EF0A8 (the big data block 0x803EF0A8..0x803EF5A0 totaling 0x4F8 bytes that the linker splits into mnSoundTest_803EF0A8 + mnSoundTest_803EF114 symbols). Function asm uses 'addi rN, r30, 0x480' through '+0x4D4' against r30 = &mnSoundTest_803EF0A8. Those offsets are inside the second linker chunk and correspond to the pooled string literals 'MenMainConTs_Top_joint', '_animjoint', '_matanim_joint', '_shapeanim_joint'. To match the function we need the WHOLE TU's data block reconstructed as one contiguous declaration so MWCC's -str reuse pool places strings at offsets 0x480/0x498/0x4B4/0x4D4 from the array start. Source currently has data split into vec_0..vec_7 individuals (instead of mnSoundTest_803EF0A8[]) and missing other big arrays, so the strings land in literal pool at wrong addresses (compiler emits 'lis r6, ...data.0@ha; addi rN, r6, ...data.0@l').
- **Tried:** Attempt 1: matched control flow exactly with string-literal args to lbArchive_LoadSections. Builds at 53.4 percent / 42 mismatches — mostly @ha/@l reloc symbol mismatches because the compiler put the pooled strings under '...data.0' instead of folding them into the existing mnSoundTest_803EF0A8 region. Function body shape (cooldown, MenuFlow updates, gm_801601C4/gm_80160244, GObj_Create + SetupProc) matches; only the data-layout-anchored references are wrong.
- **Likely fix:** Restructure src/melee/mn/mnsoundtest.c data section into a single big declaration matching the original TU: combine vec_0..vec_7 into mnSoundTest_803EF0A8[] (Vec3[9] or appropriate type), then declare text_ids/data_2/data_3/data_4/string-section as part of the same logical block (or in correct ordering) so that the literal-pool strings land at offsets 0x480, 0x498, 0x4B4, 0x4D4 from mnSoundTest_803EF0A8. Then reference them as &mnSoundTest_803EF0A8[N] or via casts. This is a multi-function TU rewrite; affects all sibling functions in mnsoundtest.c including the already-decomped 8024A790/8024A958/8024AA70/8024ABF8/8024AD58/fn_8024AED0/fn_8024BAF0. Permuter cannot fix because the mismatches are reloc-symbol, not register/scheduling.

