---
function: ftKb_SpecialN_800F11F0
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + paired-siblings
tags: [regalloc, paired-siblings, permuter-resistant]
---
## ftKb_SpecialN_800F11F0 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + paired-siblings

- **Tags:** `regalloc`, `paired-siblings`, `permuter-resistant`
- **Best fuzzy:** 81.2037%
- **Diagnosis:** Stuck at 81.2% (21 mismatches). The compiler generates 4 saved regs (r28-r31: gobj,hat,fp,alloc_data) but target uses stmw r27 with 5 saved regs (r27-r31: gobj,hat,fp_copy,fp,alloc_data). The 5th register r29 is a hoisted copy of fp (addi r29, r30, 0) placed before the if-check, used only for the trailing ftCo_8009DB50(fp) call. The sibling 800F10D4 has identical diff. The matched sibling 800F130C (DrMario, 4 saves) has same structure but NO trailing ftCo call -- confirming the ftCo call forces a 5th register in the target. All source-level attempts to introduce a 5th variable fail: (1) if-body wrapping vs early-return has no effect; (2) explicit temp_r29=fp separate from fp with ftCo_8009DB50(temp_r29) -- optimizer collapses them. MWCC refuses to assign distinct registers to two same-value variables.
- **Tried:** (1) Changed early-return to if-body wrapping (== NULL) -- still 21 mismatches. (2) Declared temp_r30=gobj->user_data, temp_r29=temp_r30 separately, passed temp_r29 to ftCo_8009DB50 -- optimizer collapses, still 21 mismatches. Prior attempt (from notes): fp=fp=gobj->user_data self-assignment pattern -- same 21 mismatches.
- **Likely fix:** The stmw r27 pattern requires a genuine 5th live variable the compiler cannot optimize away. Possible approaches: (a) use #pragma optimize_for_space or other MWCC pragmas to disable the alias optimization; (b) check if ftCo_8009DB50 prototype change (e.g., adding an extra parameter or making it non-static) shifts register pressure; (c) check if the file-ordering fix from the 800F10D4 sibling (moving ftKb_SpecialN_800EF438 definitions) might affect register allocation in some indirect way; (d) this may be a genuine permuter-territory case despite permuter-resistant diagnosis -- the stmw/lmw pattern vs individual stw/lwz is scoreable by post-link bytes.

