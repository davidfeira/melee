---
function: ftPp_SpecialS_0_Coll
tu: src/melee/ft/chara/ftNana/ftNn_Init.c
headline: permuter-false-positive + rodata-typing
tags: [permuter-false-positive, rodata-typing, regalloc]
---
## ftPp_SpecialS_0_Coll (`src/melee/ft/chara/ftNana/ftNn_Init.c`) — permuter-false-positive + rodata-typing

- **Tags:** `permuter-false-positive`, `rodata-typing`, `regalloc`
- **Best fuzzy:** 96.9308%
- **Diagnosis:** 13 mismatches at 98.85% strict / 99.19% fuzzy. 5 are sdata2 float label mismatches (target uses named globals like ftNn_Init_804D98D8/C0/E8 in sda21, base produces unnamed @290/@197/@516) — these are post-link byte-equivalent (permuter-false-positive). 5 are real regalloc/scheduling: target lis order is r4=efLib_PauseAll@ha then r5=ftNn_Init_80122FAC@ha; base reverses. addi r30=ResumeAll comes BEFORE addi r28=ftNn_Init in target, swapped in base. The 3 remaining mismatches at offsets 4612/4700/4708/4728 are downstream regalloc (r27 vs r28 holding nana_fp in trailing inline, plus mr r3,r27 vs addi r3,r27,0).
- **Tried:** 1) swapped inline2 statement order (pre_hitlag/post_hitlag before take_dmg/death2): mismatches 13->25, reverted. 2) inlined ftNn_Init_80123B3C_inline body directly into inline3 (4 stores written explicitly twice around Fighter_ChangeMotionState): mismatches 13->31 with stack frame growing 0x60->0x68 and additional stack-spill diffs, reverted.
- **Likely fix:** Introduce named static const f32 globals ftNn_Init_804D98D8/C0/E8 (and probably 804D98D0 used as f64) in rodata to match target sdata2 layout — would close 5 of the 13 mismatches. Remaining 5 lis/addi swaps may be schedule-noise from compiler choosing between r4/r5 first; could be permuter-tractable AFTER the rodata is fixed since the false-positive class would no longer dominate. Sibling ftPp_SpecialS_1_Coll shares the identical inline2 and exhibits the same 5+ symbol mismatches plus extra body diffs — should be paired with this fix.
