---
function: mnDataDel_8024FE4C
tu: src/melee/mn/mndatadel.c
headline: bss-anchor + sdata2-float
tags: [bss-anchor, sdata2-float, struct-split, tu-wide-data, regalloc, frame-size, data-anchor]
---
## mnDataDel_8024FE4C (`src/melee/mn/mndatadel.c`) — bss-anchor + sdata2-float

- **Tags:** `bss-anchor`, `sdata2-float`, `struct-split`, `tu-wide-data`, `regalloc`, `frame-size`, `data-anchor`
- **Best fuzzy:** 85.194%
- **Diagnosis:** mnDataDel_803EF870 is declared static MnDataDelData (BSS, 0x70 bytes) but target has it as 4 AnimLoopSettings in .data (0x30 bytes), with separate mnDataDel_803EF8AC (.data, 0x1DC) for the s32/s16/f32/string fields. mnDataDel_804A0918/28/38 (StaticModelDesc) are static (BSS-colocated with 803EF870) but target has them as separate-section globals. The BSS colocation causes bss-anchor reloc mismatches for ALL accesses to mdata and 804A0918/28/38 (lis+addi use ...bss.0 base). Target preloads explicit r25=804A0918 pointer in prologue (requires separate section). This drives different register allocation throughout (r24 vs r26 for jobj, different stack frame -0x68 vs -0x50, different walking pointer patterns). 104 total mismatches at 84.8%, approx 30 bss/sdata2-anchor, 74 structural.
- **Tried:** 1) Wrote full function with MnDataDelData struct pointer, StaticModelDesc statics. Got 84.79% (104 mismatches). 2) Changed 804A0918/28/38 to extern globals in .c but they remain in same BSS section as 803EF870 -> no improvement. 3) Could not add proper initializer to 803EF870 without changing its declared size (0x30 target vs 0x70 struct).
- **Likely fix:** Split mnDataDel_803EF870 into three separate globals: AnimLoopSettings[4] mnDataDel_803EF870 (initialized, in .data), AnimLoopSettings mnDataDel_803EF8A0 (already done), and a new struct mnDataDel_803EF8AC (initialized, .data, contains s32 idx fields + s16 sis_ids + f32 coords + OSReport strings). Make 804A0918/28/38 extern globals. This puts 803EF870 in .data and 804A0918/28/38 alone in .bss, triggering explicit lis/addi addressing in compiler output. The data initializers for 803EF8AC require embedding 0x1DC bytes of mixed data (s32, s16, f32, strings) as struct fields.

