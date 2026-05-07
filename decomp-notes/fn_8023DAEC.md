---
function: fn_8023DAEC
tu: src/melee/mn/mnnamenew.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling]
---
## fn_8023DAEC (`src/melee/mn/mnnamenew.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`
- **Best fuzzy:** 91.3968%
- **Diagnosis:** Improved from 81% to 95.36% (19 mismatches) by: (1) using AnimLoopSettings* settings = mnNameNew_803EDA58 to force early base-address computation into r31, (2) removing HSD_Text* text temp var and using data->field != NULL directly (fixes lwz r3 vs lwz r0+mr pattern), (3) adding explicit f32* end_frame = &settings[1].end_frame to create the 5th callee-save register r28. Remaining 19 mismatches are all register swaps: target uses var_r30->r30, data->r29 but MWCC assigns data->r30, var_r30->r29 (data has more uses, MWCC frequency-based alloc). Also target schedules addi r28, r31, 0x10 after 1st call (in latency slot), base schedules it before 2nd call.
- **Tried:** (1) original upstream source - 81%, (2) AnimLoopSettings* settings only (no end_frame) - 83%, (3) various declaration order permutations - all gave same 4 reg (stw r28-r31) not 5 reg (stmw r27), (4) explicit f32* end_frame with settings - 95.36% best, (5) early var_r30=1 before data assignment - MWCC ignores assignment order for reg alloc, (6) removed duplicate var_r30=1 - worse at 91%
- **Likely fix:** Need MWCC to assign r30 to var_r30 and r29 to data. data has ~15 uses vs var_r30 ~5 uses so MWCC gives data higher reg. Possible: reduce data access count by pre-caching fields early, or find source structure where var_r30 gets more weight. The addi r28 scheduling is also instruction-scheduling domain.

