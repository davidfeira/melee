---
function: lbArchive_80017040
paired_with: [lbArchive_800171CC]
tu: src/melee/lb/lbarchive.c
headline: paired regalloc
tags: [stack-offset, paired-siblings]
---
## lbArchive_80017040 + lbArchive_800171CC (`src/melee/lb/lbarchive.c`) — paired regalloc

- **Tags:** `stack-offset`, `paired-siblings`
- **Best fuzzy:** 99.93% / 99.92% (Opus subagent — cluster permuter launched, identical structure)
- **Diagnosis:** Pure stack-offset shift, all 7 mismatches are exactly 4 bytes off (target wants 0x7c/0x80/0x84/0x88; base has 0x80/0x84/0x88/0x8c). The va_list area, length slot, and arg spill positions are uniformly off.
- **Tried:** `u8 _[4]` padding (grew frame wrong direction), inlining `lbArchive_LoadArchive` body (broke register allocation entirely). Both reverted.
- **Likely fix:** permuter (registered allocation territory). Sibling `lbArchive_800171CC` is structurally identical (only difference: calls `lbArchive_vLoadSections` vs `_vLoadSectionsFatal`) — same fix should apply once found.
