---
function: grOldKongo_8020F52C
tu: src/melee/gr/groldkongo.c
headline: tu-data-osreport + cross-tu-globals
tags: [tu-data-osreport, cross-tu-globals]
---
## grOldKongo_8020F52C (`src/melee/gr/groldkongo.c`) — tu-data-osreport + cross-tu-globals

- **Tags:** `tu-data-osreport`, `cross-tu-globals`
- **Best fuzzy:** 94.8814%
- **Diagnosis:** Confirmed same state as prior entry (94.71%, 5 mismatches). All 5 mismatches are data-layout-driven: OSReport args use addi r3,r31,0x9c and addi r4,r31,0xc0 (r31=&grOk_803E6580), but base produces 0x50/0x74 offsets from grOk_803E658C. Plus scheduling INSERT/DELETE pair on addi r3,r28,0x0 and addi r29,r29,0xc. Requires defining grOk_803E6580 (12-byte struct) before the StageCallbacks array, plus grOk_803E65E8 (0x58-byte struct with format string at offset 0x34). Same structural blocker as grRCruise_801FF2C8.
- **Tried:** Verified asm (build-linux/grOldKongo_8020F52C.s), confirmed r31=grOk_803E6580 base, offsets 0x9c/0xc0. Read prior notes. No source edits attempted — TU-wide data refactor required, out of single-function scope.
- **Likely fix:** Define grOk_803E6580 (s32 x0=3, s32 x4=0x10001, s32 x8=0x30002) BEFORE the StageCallbacks array. Define grOk_803E65E8 as 0x58-byte struct with func-ptr fields plus char[0x28] format string at offset 0x34. Update OSReport call site to reference these. Fix also needed at multiple other OSReport sites in TU. Mama Claude TU-wide data refactor task.

