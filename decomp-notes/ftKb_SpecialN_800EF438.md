---
function: ftKb_SpecialN_800EF438
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, mwcc-const-fold]
---
## ftKb_SpecialN_800EF438 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `mwcc-const-fold`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 90.3% / 63 mismatches dominated by register allocation (r22/r23/r24/r25/r26/r27 swaps throughout the function) and two instances of mwcc folding 'total_dobjs << N' to 'li 0' when total_dobjs is statically 0. Logical structure is correct: dyn=hat->hat_dynamics[2] gate; first joint-tree walk uses HSD_IDInsertToTable to register (joint, parts[i].joint); second walk loads HSD_DObjLoadDesc(joint->u.dobjdesc), splices into existing dobj chain (HSD_JObjAddDObj or lb_8000CE30), iterates the new chain storing dobjs into ((HSD_DObj**)fp->fv.gw.x224C_greenhouseGObj)[total_dobjs], bumps total. flags_b1 (not flags_b6) is the iteration predicate; byte+9 LSB |= 1 is the 'dobj loaded' marker. Asserts use ftKb_Init_assert_msg_0/1/2 already declared in TU plus ftKb_Init_804D3DAC="0" sized [2] to force @sda21. Header signature corrected from UNK_RET to void.
- **Tried:** (1) initial port from m2c - 88.4%; (2) fixed flag bit flags_b6 -> flags_b1 (MSB-first bitfield + lbz placing byte at word bits 24-31 means extrwi position 25 = mwcc-declared bit flags_b1); (3) sized ftKb_Init_804D3DAC[2] to switch hoisted @ha/@l into @sda21 - 90.3%; (4) reordered total_dobjs / sp20 init to defeat constant folding of 'total_dobjs << 4' - no change.
- **Likely fix:** Permuter for register allocation. May need a scheduling trick to keep slwi r25,r28,4 instead of li r25,0 (assign part_off through a path mwcc cannot prove constant).

