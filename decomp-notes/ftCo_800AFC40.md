---
function: ftCo_800AFC40
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## ftCo_800AFC40 (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 99.4882%
- **Diagnosis:** 13 mismatches, all register-naming swap r27<->r28 between target (r27=const-1, r28=&fp->x1A88) and base (r28=const-1, r27=&fp->x1A88). m2c shape is canonical (already matches base.c shape). Cluster permuter plateaued at score 1190 across 50+ outputs without breaking the swap; top candidates only flatten the trailing if/else { if/else } into else-if (variant 1 confirmed: same 13-mismatch count, no progress).
- **Tried:** variant 1: flattened nested else { if/else } into else-if/else chain (matches sibling ftCo_800AF... at line 3909) - no change in mismatch count, reverted. Looked at 1190/1195/1195-2 outputs - structural rewrite is not the lever.
- **Likely fix:** Permuter cannot break this register-naming pair. Likely needs cross-TU analysis: maybe a static helper or wrapper-call ordering elsewhere in the TU shifts register coloring. Or check if a different m2c-suggested temp ordering (e.g. introducing extra Fighter* alias before bitfield writes) shifts the constant-1 to r27. Worth a fresh subagent later with mama context, not subagent grind.
