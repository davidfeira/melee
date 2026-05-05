---
function: grKongo_801D55D8
tu: src/melee/gr/grkongo.c
headline: stack-offset + frame-size
tags: [stack-offset, frame-size, regalloc]
---
## grKongo_801D55D8 (`src/melee/gr/grkongo.c`) — stack-offset + frame-size

- **Tags:** `stack-offset`, `frame-size`, `regalloc`
- **Best fuzzy:** 99.0194%
- **Diagnosis:** Frame size +0x8 vs base. Target spills (s32) float-cast results to 4 stack slots (0x20/0x28/0x30/0x38), base coalesces to 3 slots overlapping with sp14 area. Source structure (Vec3 sp14 + 2 inline random_adder_f/random_adder calls) appears semantically equivalent and produces 100%-matching grKongo_801D5774, but layout differs in 55D8. Cascade of regalloc/stack-offset diffs from this single frame-size choice; also 2 named-symbol false-positives (grKg_804DAFA0/A4@sda21 vs anon @180/244). 6 'real' mismatches center on lfs/fctiwz ordering: target reads 0x2c then 0x30, base reads 0x30 then 0x2c (likely tied to whether MWCC commutes the > comparison).
- **Tried:** V1: move Vec3 sp14 into block scope just before lb_8000B1CC (no change, 35→35). V2: declare sp14 after Ground*/void* locals (no change, 35→35). MWCC stack layout for sp14 not affected by declaration order in this function.
- **Likely fix:** Possibly TU-wide difference: a sibling function above 55D8 in the TU may need its source landed first to shift literal pool / sda2 anchors. Or grkongo.static.h grKg_804DAFA0/A4 needs to be declared as extern f32 in the source so the compiler emits named @sda21 reloc — but since 5774 matches with 0.0f literal that may not be the issue. Real fix likely structural: identify what makes MWCC choose frame=0x50. Worth a permuter run after random_adder_f matches; cluster will have 4 stfd patterns to explore.
