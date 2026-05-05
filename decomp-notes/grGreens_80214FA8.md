---
function: grGreens_80214FA8
tu: src/melee/gr/grgreens.c
headline: tu-wide-data + data-symbols-missing
tags: [tu-wide-data, data-symbols-missing, struct-split]
---
## grGreens_80214FA8 (`src/melee/gr/grgreens.c`) — tu-wide-data + data-symbols-missing

- **Tags:** `tu-wide-data`, `data-symbols-missing`, `struct-split`
- **Best fuzzy:** 98.493%
- **Diagnosis:** Source uses single array grGr_803E7840[128] (s16) for both inner loops, but target asm shows two DIFFERENT s16[30] arrays inside a larger aggregate symbol grGr_callbacks: first loop reads grGr_callbacks+0x244+i*2 (mpJointSetCb2 second arg), second loop reads grGr_callbacks+0x208+j*2 (Ground_801C3FA4 second arg). Target uses 'lis r4, grGr_callbacks@ha; addi r29, r4, grGr_callbacks@l' as a single base, then derives both arrays via constant offsets. Source's grGr_803E7840 base symbol is wrong abstraction — should be two distinct s16 arrays, both fields of the grGr_callbacks aggregate. 21 mismatches: 2 are real (lha/addi at array-base setup), 17 cascade as regalloc shifts (r26<->r27, r30<->r27 etc) downstream of the 0x244/0x208 base-derivation extra add instruction reshuffling live ranges, 2 permuter-false-positives.
- **Tried:** Diagnosis from asm reading. Codex TU attempts: (1) first loop `grGr_803E7840[i + 30]` improved strict 98.28169% -> 98.33803% but still had 21 mismatches and kept the wrong `...data.0+0xfc` anchor; (2) making `grGr_callbacks`/`grGr_803E7840` non-static had no effect; (3) explicit `s16*` locals for `grGr_callbacks+0x244/+0x208` regressed to 36 mismatches by growing the frame; (4) direct offset dereferences regressed to 28 mismatches; (5) one advancing `s16*` iterator regressed to 35 mismatches. All source edits were reverted.
- **Likely fix:** TU-wide refactor: declare grGr_callbacks aggregate (likely a struct in static.h with named callback arrays + s16[30] subarrays at offsets 0x208 and 0x244) and rewrite grGreens_80214FA8 to use the appropriate subarray for each loop. Likely shared with grGreens_802139C4 sibling stuck-note pattern. Beyond single-function scope.
