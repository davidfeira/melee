---
function: grGreens_802139C4
tu: src/melee/gr/grgreens.c
headline: regalloc + frame-size
tags: [regalloc, frame-size]
---
## grGreens_802139C4 (`src/melee/gr/grgreens.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`
- **Best fuzzy:** 87.569%
- **Diagnosis:** Base saves r28-r31 (4 callee-saves, frame -0x28); target only saves r30,r31 (frame -0x20) and spills to stack slot 0x14 instead. Cascading regalloc shift: gobj is r28 in base vs r30 in target; gp is r29 in base vs r31 in target. The randrange inline picks min=r31/max=r30 in base but min=r29/max=r28 in target. All 35 mismatches stem from this register pressure decision; the 8 'real' diffs are actually regalloc shifts misclassified.
- **Tried:** V1: move GET_GROUND after ftCo_800C06E8 call (worse, 41 mismatches; mwcc moved fn_80213B1C@ha load earlier). V2: cache grGr_params->x34/x38 into local int min,max (no change, still 35).
- **Likely fix:** Permuter territory: needs RANDOMIZE_VAR_ORDER / pernop / register-pressure tweaks. Or upstream: maybe randrange inline body shape (different rng/diff variable layout) would change the live-range and force base's regalloc. Worth dispatching to cluster permuter.
