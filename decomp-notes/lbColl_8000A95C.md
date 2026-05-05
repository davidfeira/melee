---
function: lbColl_8000A95C
tu: src/melee/lb/lbcollision.c
headline: tu-wide-data + permuter-false-positive
tags: [tu-wide-data, permuter-false-positive, rodata-typing, stack-offset]
---
## lbColl_8000A95C (`src/melee/lb/lbcollision.c`) — tu-wide-data + permuter-false-positive

- **Tags:** `tu-wide-data`, `permuter-false-positive`, `rodata-typing`, `stack-offset`
- **Best fuzzy:** 99.8621%
- **Diagnosis:** lbcollision.c TU-wide issue. 99.69% strict / 99.86% fuzzy with 20 mismatches: (1) 4 sda21 mismatches where target uses named symbols lbColl_804D3700 ("jobj.h") and lbColl_804D3708 ("jobj") but base produces anonymous string pool entries @790@sda21 / @791@sda21 - both resolve identically at link time but objdiff treats as different. These are __FILE__/__FUNCTION__ strings produced by HSD_ASSERT in inlined HSD_JObjGetMtxPtr. (2) 16 stack-offset mismatches: target allocates Vec3 sp24/sp30 as PSMTXMultVec outputs at low offsets and copies them to higher slots sp6C/sp78 for the lbColl_800096B4 by-value Vec3 args; base reuses the slots in reverse order (PSMTXMultVec writes directly to 0x6C/0x78 then copies to 0x24/0x30). Sibling lbColl_8000AB2C has IDENTICAL diff pattern - same TU, same wrapper structure. Reordering Mtx sp3C declaration to last matched the Mtx slot but did not fix Vec3 slot allocation choice.
- **Tried:** prep + diff baseline. Tried local reorder: moved Mtx sp3C from before Vec3 sp30/sp24 to after them - got Mtx at 0x3C correctly but Vec3 sp24/sp30 went to 0x6C/0x78 instead of target 0x24/0x30. Verified lbColl_8000AB2C (sibling, identical structure) has the SAME 20-mismatch pattern (99.69% strict). Pattern is TU-wide, not function-local. The string-pool issue (@790 vs lbColl_804D3700) appears in many other lbcollision functions too.
- **Likely fix:** Not a permuter case - the 4 string mismatches are link-equivalent (rodata anchor false positive), and the 16 stack mismatches are mwcc allocation choice that won't change with manual source-shape variants alone. Probably needs TU-wide rodata RE: explicitly declare the assert filename/funcname strings as named static char arrays at TU scope to force mwcc to emit named references rather than anonymous pool entries. The stack-slot issue may be coupled - changing string literal handling earlier in TU may shift later compilation decisions. Investigate at TU level after rodata fix; do not iterate in isolation on this function.
