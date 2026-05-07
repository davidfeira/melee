---
function: ftKb_SpecialNSpit1_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-resistant + scheduler
tags: [permuter-resistant, scheduler, float-regalloc, sdata2-anonymous-floats, paired-siblings, instruction-scheduling]
---
## ftKb_SpecialNSpit1_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-resistant + scheduler

- **Tags:** `permuter-resistant`, `scheduler`, `float-regalloc`, `sdata2-anonymous-floats`, `paired-siblings`, `instruction-scheduling`
- **Best fuzzy:** 95.1515%
- **Diagnosis:** 95.08% (5 mismatches). Identical mismatch shape to sibling ftKb_SpecialNSpit0_Anim (already diagnosed as permuter-resistant). Both share ftKb_SpecialNSpit0_Anim_inline static inline. Blocker: double-fneg scheduling artifact (fneg f1,f0 + fneg f2,f1 pair) to preserve facing_dir across 0.0f constant load that clobbers f0 — compiler generates this pattern when 0.0f is loaded via @sda21 and facing_dir must be preserved in FPR. Also: lfs/lwz ordering swap (target loads fp->facing_dir into f0 before gobj->user_data ptr load, base has them reversed) and sdata2-anonymous-floats mismatch (ftKb_Init_804D93B0@sda21 vs @193@sda21, post-link equivalent 0.0f). All 5 mismatches are scheduler/regalloc decisions unreachable from C source.
- **Tried:** No source edits attempted (0/2 attempts used). Diagnosis inherited from sibling ftKb_SpecialNSpit0_Anim which exhausted 2 attempts confirming permuter-resistance: (1) f32 local + double-neg expression caused stack frame growth and worsened to 94.8%; (2) all structural variants confirmed correct. Since both functions use the same inline, any C-level fix to the inline would fix both or neither.
- **Likely fix:** Not fixable from C source alone. Would require either: (a) compiler version/switch that happens to produce the double-fneg scheduling pattern, (b) post-processing ASM injection (not allowed in this project), or (c) accepting the 5-instruction mismatch as a known permuter-resistant case.

