---
function: ftMaterial_800BF2B8
tu: src/melee/ft/ftmaterial.c
headline: regalloc + stack-offset
tags: [regalloc, stack-offset, permuter-false-positive]
---
## ftMaterial_800BF2B8 (`src/melee/ft/ftmaterial.c`) — regalloc + stack-offset

- **Tags:** `regalloc`, `stack-offset`, `permuter-false-positive`
- **Best fuzzy:** 99.1761%
- **Diagnosis:** 26 mismatches: 20 regalloc (target uses r28 for mobj_rendermode/texp1, base uses r30/r28), 3 stack-offset (target frame is 4 bytes larger than base; locals at 0x1c/0x20/0x24 in target vs 0x18/0x1c/0x20 in base), 3 permuter-false-positive flagged. Source has explicit u32 unused; declaration that may be a hint at extra slot.
- **Tried:** Removed 'u32 unused;' declaration; mismatches went 26->51 (worse) - reverted immediately.
- **Likely fix:** Stack frame is 4B larger in target. Need to reduce by one 4B slot - possibly inline texp1 capture (avoid HSD_TExp* texp1 local), or reorder locals. The 'u32 unused' is NOT the extra slot. Could be that texp/pe layout pushes things. Permuter likely false-positive class given the 3 flagged mismatches; manual structural fix needed before any permuter dispatch.
