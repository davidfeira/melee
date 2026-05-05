---
function: lbHeap_80015DF8
tu: src/melee/lb/lbheap.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## lbHeap_80015DF8 (`src/melee/lb/lbheap.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 99.8765%
- **Diagnosis:** 2 regalloc mismatches at the merge-point reload of p->size after the if/else OSReports. Target uses lwz r5, base uses lwz r0 (same address @ 0xc(r27)). After volatile clobber by OSReport, r0 (volatile) vs r5 (saved/temp) for a 1-use value. Source is semantically correct; a hoisted size local doesn't change codegen, and reordering if/!=0 first regresses match.
- **Tried:** V1: hoisted u32 size = p->size before final OSReport (no change). V2: inverted if/else order to put destroy branch first (regressed to 89.7% / 13 mismatches due to label/ordering churn).
- **Likely fix:** Permuter has plateaued at score=50 with junk rewrites. The remaining diff is squarely register-coloring; either dispatch fresh permuter run with seed reset, or accept as a near-miss requiring exotic source shape (e.g., volatile cast / asm-equivalent reordering of the var_r25 computation that frees r5 at merge point).
