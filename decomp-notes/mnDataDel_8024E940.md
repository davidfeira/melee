---
function: mnDataDel_8024E940
tu: src/melee/mn/mndatadel.c
headline: struct-split + header-required
tags: [struct-split, header-required, data-anchor]
---
## mnDataDel_8024E940 (`src/melee/mn/mndatadel.c`) — struct-split + header-required

- **Tags:** `struct-split`, `header-required`, `data-anchor`
- **Best fuzzy:** 87.8667%
- **Diagnosis:** Reached 87.2%/94.3% with structural decomp. Blocker: target uses mnDataDel_803EF8AC@ha as a separate symbol (size 0x1DC, distinct from mnDataDel_803EF870 size 0x30 and mnDataDel_803EF8A0 size 0xC). The static.h MnDataDelData struct must be split into three separate static objects (x0..x2C as mnDataDel_803EF870, x30 padding, mnDataDel_803EF8A0 as separate AnimLoopSettings, and mnDataDel_803EF8AC as the trailing struct). This refactor impacts already-matched fn_8024FBA4, fn_8024FC48, fn_8024FD40, mnDataDel_8024EBC8 which all reference data->x3C through data->x6C. Also: stack frame is 0x38 vs 0x30 (8 bytes of additional locals/PAD needed beyond what PAD_STACK(16) provides — PAD_STACK uses unsigned char[] which mwcc may eliminate), and register r30/r31 swap depends on data ptr declaration order. Recommend out-of-band header refactor across the TU before resuming.

