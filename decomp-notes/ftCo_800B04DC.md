---
function: ftCo_800B04DC
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc, frame-size]
---
## ftCo_800B04DC (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 81% match (96 mismatches). Logic verified correct: bitfield writes match, item kind switch (Heart/Tomato/Foods) → x4C assignment correct, distance check + sqrtf newton-raphson + ftCo_800A6700 + ftCo_800A1CC4 dispatch all matching the target's structure. Remaining diff is purely regalloc: target uses stmw r27, 0x44(r1) with 5 callee-saved regs (r27=is_healing(1), r28=0, r29=fp, r30=&data, r31=&data->x44) and 0x58 frame; my attempts get only 3 callee-saved (stw r29/r30/r31) with smaller frames. mwcc isn't promoting my int locals to callee-saved registers because they aren't live across enough calls. No structural blocker — permuter should resolve quickly.
- **Tried:** A1: clean rewrite modeled on ftCo_800B0760 sibling. A2: introduced explicit 'int is_healing=1, zero=0' locals plus a goto-skip rewrite of the item_gobj branch to make is_healing live across the ftCo_800A61D8 call. Both bumped match by ~2% but didn't resolve regalloc.
- **Likely fix:** Permuter randomization of local order/types should give r27/r28 callee-saved promotion → stmw → match.

