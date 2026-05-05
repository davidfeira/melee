---
function: mnCount_GetRowValue_Character
tu: src/melee/mn/mncount.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive]
---
## mnCount_GetRowValue_Character (`src/melee/mn/mncount.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`
- **Best fuzzy:** 99.3333%
- **Diagnosis:** 3 of 4 mismatches are jumptable label false-positives (jumptable_803EFAE8 vs @486 — same data). The 1 real diff is r30 init at SHORTEST_TIME entry: target does 'li r31,0; addi r30,r31,0' (chained zero materialization, c then i), our build emits 'li r30,0; li r31,0' (independent). Net: target has 2 zero-init insns where r30 is derived from r31; base has 2 independent li. Both produce r30=r31=0 so semantically equivalent.
- **Tried:** (1) for(c=0,i=0;...) merged init: zero change (4 mismatches). (2) swap 'int i; int c;' decl order: regressed to 11 mismatches — c=r30, i=r31 swap, much worse. Original decl order is correct. The asm pattern shows mwcc target reuses r31's just-loaded zero to seed r30, while our build materializes both zeros directly. Source-shape variants tested don't influence this — likely needs permuter or a TU-wide reordering trick (sibling function above might pin a register coloring). Not classic permuter territory since base is also valid; might just be permuter-eligible if scorer counts 'addi rX,rY,0' = 'li rX,0' as equivalent.
- **Likely fix:** Either: (a) accept as permuter-false-positive — final linker output identical for both regalloc choices; or (b) try permuter, since it's only 1 'real' instruction off and permuter scorer will likely treat them as equivalent. Given it's 99.17% strict and only the regalloc shape differs, this is plausibly permuter territory but may also dispatch as scoring noise.
