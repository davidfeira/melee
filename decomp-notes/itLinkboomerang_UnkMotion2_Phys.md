---
function: itLinkboomerang_UnkMotion2_Phys
tu: src/melee/it/items/itlinkboomerang.c
headline: regalloc + sdata2-float
tags: [regalloc, sdata2-float, permuter-false-positive, paired-siblings]
---
## itLinkboomerang_UnkMotion2_Phys (`src/melee/it/items/itlinkboomerang.c`) — regalloc + sdata2-float

- **Tags:** `regalloc`, `sdata2-float`, `permuter-false-positive`, `paired-siblings`
- **Best fuzzy:** 99.05%
- **Diagnosis:** 99.05%/14 mismatches, identical to sibling itLinkboomerang_UnkMotion1_Phys (same TU, same source shape, same diff). 3 mismatches are sda21 reloc-symbol mismatches (target uses named globals it_804DCD68/it_804DCD88/it_804DCD90; base uses anonymous @N@sda21 pool literals). 11 mismatches are downstream f4-vs-f5 register-allocation cascade through inlined my_sqrtf body (lfs/fadds/fcmpo/frsqrte/3x fnmsub/fmul) plus stack 0x14-vs-0x10 spill slot for hypot-attrs->xC subtract. All instruction-level diffs (lfs/fadds/fcmpo/frsqrte/fnmsub/fmul) are register choice only, not real semantic differences.
- **Tried:** Per sibling's prior log: (1) inlining attrs->xC into subtract dropped to 90.21% (worse, 20 mismatches); (2) splitting hypot/subtract with intermediate var: no change. Both variants already exhausted on identical sibling. No new variants attempted here per stop-criteria (would duplicate sibling's failed work).
- **Likely fix:** Cross-TU: needs the named globals it_804DCD68/it_804DCD88/it_804DCD90 declared/used somewhere in this TU as named externs so MWCC emits them as named sdata2 references instead of anonymous pool literals. Per sibling diagnosis: investigate why other functions in the same TU (it_802A0E70, itLinkboomerang_UnkMotion1_Anim) match 100% with same 0.0f usage. Once Motion1_Phys unlocks via the cross-TU sdata2 fix, Motion2_Phys will follow with identical edit (or no edit -- they may share the same .rodata section).
