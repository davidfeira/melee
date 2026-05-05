---
function: mnDataDel_8024EEC0
tu: src/melee/mn/mndatadel.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, data-symbols-missing]
---
## mnDataDel_8024EEC0 (`src/melee/mn/mndatadel.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `data-symbols-missing`
- **Best fuzzy:** 99.2589%
- **Diagnosis:** Diff dominated by BSS-anchor false positives: base uses '...bss.0@ha' anchor with 'mnDataDel_804A0938' at offset +0x70 within the section, while target emits 'mnDataDel_804A0938@ha' as a named symbol. Field accesses follow the anchor (0x70/0x74/0x78/0x7c in base vs 0/4/8/c in target) but ARE the same physical bytes after link. Cascade: stack-offset (0x34 vs 0x10/0x14/0x24/0x28 — frame layout shifts due to structural diffs in the wider TU) and regalloc swap (r28<->r30, r30<->r31) follow from this. Also one sdata2 float case: 'mnDataDel_804DC1A8@sda21' (target) vs '@166@sda21' (base) — base treats float as anonymous, our static.h names it.
- **Tried:** Inspected base/target .o disasm. Base .o has '_803EF870' (size 0x70) in .bss (zero-init), then '_804A0938' (size 0x10) at .bss+0x70, all 'local' visibility. Target .o has all 3 BSS symbols ('_804A0918','_804A0928','_804A0938') as 'global' size 0x10 each + 0x30 of .data spurious bytes for '_803EF870'. Source .static.h declares 'static struct MnDataDelData mnDataDel_803EF870;' and 'static StaticModelDesc mnDataDel_804A0938;' — should be local but emit as global.
- **Likely fix:** Three TU-wide actions (out of single-function 2-variant scope): (1) collapse '_804A0918'+'_804A0928'+'_804A0938' into a single static array/struct of 0x30 size, so mwcc emits one BSS object, eliminating the named-symbol mismatch; (2) ensure '_803EF870' compiles to BSS with size 0x70 (not 0x30) — likely needs the 'MnDataDelData' struct to fully cover offsets 0..0x70 AND not have a competing initialized definition elsewhere; (3) replace 'mnDataDel_804DC1A8' literal use with anonymous '0.05f' and friends so mwcc generates '@166'-style local sdata2 entries. All three need other functions in this TU (fn_8024F1D4, fn_8024F318, fn_8024F840, fn_8024FE4C, mnDataDel_80250170) to be decompiled or stubbed in a way that uses the same data layout.
