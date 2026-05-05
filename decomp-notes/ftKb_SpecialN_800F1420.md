---
function: ftKb_SpecialN_800F1420
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## ftKb_SpecialN_800F1420 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 99.4595%
- **Diagnosis:** 3 strict mismatches, all regalloc: target wants 'p' (entry->x4 inner loop pointer) in r3, our build puts it in r12. Target uses r3 because after 'lwz r7,0x2c(r3)' (load fp from gobj arg), r3 is freed and reused for the inner loop pointer. Function body is structurally correct (matches 100% in non-regalloc terms). Permuter has plateaued at score=40 (3 regalloc) for 689min.
- **Tried:** V1: declared p/entry/j at outer scope (no change). V2: removed 'new_var = fp;' indirection and used fp->fv.kb.hat.x14.data directly (no change, still 3 mismatches). The 'new_var = fp' assignment was a permuter-suggested workaround that doesn't affect the regalloc of p.
- **Likely fix:** Pure regalloc — needs permuter breakthrough. Or possibly a TU-wide pattern where adjacent functions affect register pressure. Note: the 'new_var = fp' pattern in current source IS a permuter find that fixed earlier mismatches (likely the inner dobj load); removing it doesn't break those. Could try declaring p as a non-pointer index, e.g. 'int k = entry->x4[j]' instead of 'u8* p', to change how mwcc allocates the increment.
