---
function: ftPp_SpecialHiStart_0_Anim
tu: src/melee/ft/chara/ftPopo/ftPp_SpecialS.c
headline: instruction-scheduling + float-regalloc
tags: [instruction-scheduling, float-regalloc, inlining, permuter-territory]
---
## ftPp_SpecialHiStart_0_Anim (`src/melee/ft/chara/ftPopo/ftPp_SpecialS.c`) — instruction-scheduling + float-regalloc

- **Tags:** `instruction-scheduling`, `float-regalloc`, `inlining`, `permuter-territory`
- **Best fuzzy:** 96.6364%
- **Diagnosis:** 4 mismatches remain after fixing stack frame (PAD_STACK 32 in function body) and bool-comparison (ftNn_Init_8012300C == 1). Blocker is MWCC generating lfsu f2,0xb0(r3) (load-with-update) for checkNanaInRange inline, while our compilation emits 4 plain lfs instructions. Target loads nana_fp->cur_pos.x via lfsu then accesses nana_fp->cur_pos.y at updated_r3+0x4; base loads both fields at explicit 0xb0/0xb4 offsets. Load ordering also differs (target: nana.x, fp.x, fp.y, nana.y; base: fp.x, nana.x, fp.y, nana.y).
- **Tried:** 1) Added PAD_STACK(32) to function body, changed ftNn_Init_8012300C condition to ==1 -- fixed 7 of 11 mismatches. 2) Swapped subtraction order in SQ() to put nana_fp fields first -- made things worse (5 mismatches), reverted.
- **Likely fix:** Permuter run on checkNanaInRange inline expression; the lfsu pattern is a pure compiler scheduling/regalloc choice that requires the permuter to discover the right expression form.

