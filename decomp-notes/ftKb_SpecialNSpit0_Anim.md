---
function: ftKb_SpecialNSpit0_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-queued + scheduler
tags: [permuter-queued, scheduler, regalloc, sda21-float-collision, sdata2-anonymous-floats, paired-siblings]
---
## ftKb_SpecialNSpit0_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-queued + scheduler

- **Tags:** `permuter-queued`, `scheduler`, `regalloc`, `sda21-float-collision`, `sdata2-anonymous-floats`, `paired-siblings`
- **Best fuzzy:** 94.5455%
- **Diagnosis:** 95.08% (5 mismatches: 2 instr-swap lfs/lwz, 2 missing fneg pair, 1 sda21 symbol naming @193 vs ftKb_Init_804D93B0). Frame layout, store ordering (z then y), and access pattern (gobj->user_data->dat_attrs reload after lb_8000B1CC) all matched. Sibling Spit1 matches identically (just tail-call differs: ft_8008A2BC vs ftCo_Fall_Enter). Both functions share inline ftKb_SpecialNSpit0_Anim_inline(). Stack pad uses u8 _pad[60] before attrs + u8 _pad2[8] after. Constant 0.0f compiles to anonymous @193 instead of named ftKb_Init_804D93B0; using extern f32 ftKb_Init_804D93B0 directly causes register reshuffle (f0/f1/f2 perm) and worse match. The two missing fneg instructions are compiler scheduling artifact: target stashes facing_dir into f1 via fneg-then-fneg-back across the f0-clobbering 0.0f load. Not directly expressible from C source. Permuter required for fneg insertion plus lfs/lwz swap.

