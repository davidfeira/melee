---
function: ftKb_SpecialNSpit1_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-queued + scheduler
tags: [permuter-queued, scheduler, regalloc, sda21-float-collision, sdata2-anonymous-floats, paired-siblings]
---
## ftKb_SpecialNSpit1_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-queued + scheduler

- **Tags:** `permuter-queued`, `scheduler`, `regalloc`, `sda21-float-collision`, `sdata2-anonymous-floats`, `paired-siblings`
- **Best fuzzy:** 94.5455%
- **Diagnosis:** 95.08% match, identical mismatch shape to ftKb_SpecialNSpit0_Anim (sibling: same body, only tail call differs ftCo_Fall_Enter vs ft_8008A2BC). Both share static inline ftKb_SpecialNSpit0_Anim_inline. See ftKb_SpecialNSpit0_Anim notes for full diagnosis. Permuter on Spit0 should propagate.

