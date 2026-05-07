---
function: ftKb_SpecialNSpit0_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: scheduler + regalloc
tags: [scheduler, regalloc, sdata2-anonymous-floats, float-regalloc, paired-siblings, permuter-resistant]
---
## ftKb_SpecialNSpit0_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — scheduler + regalloc

- **Tags:** `scheduler`, `regalloc`, `sdata2-anonymous-floats`, `float-regalloc`, `paired-siblings`, `permuter-resistant`
- **Best fuzzy:** 95.1515%
- **Diagnosis:** 95.08% (5 mismatches). After two attempts: (1) adding explicit f32 local + double-negation caused 8-byte stack frame growth (MWCC allocated spill slot, not register-only), worsening to 94.8% with 21 mismatches; (2) all structural layouts confirmed correct. Remaining 4 real mismatches are: lfs/lwz order swap (facing_dir load before vs after dat_attrs ptr load) and missing fneg+fneg pair (double-negation scheduling artifact to preserve facing_dir in FPR across 0.0f constant clobber). 5th mismatch is sdata2-anonymous-floats class: @193@sda21 vs ftKb_Init_804D93B0@sda21 (both 0.0f, post-link equivalent). All mismatches are scheduler/regalloc decisions unreachable from C source.
- **Tried:** (1) f32 facing_dir local + -(-facing_dir) double-neg expression: caused stack frame growth from 0x90 to 0x98, worsened match. Reverted. (2) Analyzed all structural variants: da= vs direct deref, order of vel.x/z/y, and cast patterns. Stack frame 0x90 matches perfectly with current layout (u8 _pad[60] + it_2F28_DatAttrs + u8 _pad2[8]). Function body ordering is correct. Only scheduler issue remains.
- **Likely fix:** Permuter with fneg-insertion + lfs/lwz reorder. The sdata2-anonymous-floats mismatch is a permuter-false-positive (post-link identical). The real 4 mismatches need permuter to find the register-preservation scheduling pattern.

