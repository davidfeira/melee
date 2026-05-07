---
function: grHeal_8021F70C
tu: src/melee/gr/grheal.c
headline: regalloc + data-anchor
tags: [regalloc, data-anchor, tu-data-osreport, mwcc-loop-opt]
---
## grHeal_8021F70C (`src/melee/gr/grheal.c`) — regalloc + data-anchor

- **Tags:** `regalloc`, `data-anchor`, `tu-data-osreport`, `mwcc-loop-opt`
- **Best fuzzy:** 43.6111%
- **Diagnosis:** Function uses grHeal_803E83B8[0xD] as entry pointer and needs: (1) character_id kept in r3 throughout (compiler moves it to r4), (2) lis grHeal_803E83B8@ha hoisted before cmpwi r3, (3) OSReport string at grHeal_803E83B8+0x170 (within-page relative addressing), (4) post-loop check using add+lwz 0x34 offset rather than lwzx, (5) loop has cmpw not cmplw for character_id check.
- **Tried:** (1) original upstream source with grHeal_803E851C entry pointer - 64%, 23 mismatches. (2) entry=&grHeal_803E83B8[0xD] with entry[frame]==-1 check and character_id in OSReport - 50.5%, 29 mismatches. (3) entry init before cmpwi to force lis hoisting - 39%, 35 mismatches (broke loop structure).
- **Likely fix:** Need register allocation that keeps r3=character_id, r5=grHeal_803E83B8 base. The grHeal_803E851C char array is a data layout artifact; the entry pointer must come from grHeal_803E83B8[0xD]. OSReport string must be within same 64KB page as grHeal_803E83B8. The loop structure mismatch (target: check -1 first then cmpw r3,r0; base: different order with extra cmplw) needs correct while() form. This is likely a regalloc + scheduler problem once correct data pointer is established.

