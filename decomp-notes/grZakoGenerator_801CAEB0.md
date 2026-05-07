---
function: grZakoGenerator_801CAEB0
tu: src/melee/gr/grzakogenerator.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-territory]
---
## grZakoGenerator_801CAEB0 (`src/melee/gr/grzakogenerator.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-territory`
- **Best fuzzy:** 81.25%
- **Diagnosis:** All 10 mismatches are pure regalloc (r6 vs r7 for &x4 address, r4 vs r7 for sign-extended arg1, r5 vs r0 for sentinel.x0 value) plus one scheduling difference (li r0,0 hoisted before bnelr in target, after in base). No source-shape lever can change MWCC register assignment for this tiny 16-instruction leaf function.
- **Tried:** V1: grZakoGenerator_Data** data = &lbl_8049F030.x4 + sentinel pointer pre-computed — dropped to 41.8% due to lhau instruction change, wrong direction. V2: s16 arg1 parameter type instead of int arg1 + s16 val local — identical 10 mismatches at 81.25%, no effect on regalloc.
- **Likely fix:** Permuter cluster dispatch. Pure regalloc/scheduling on a 16-instruction leaf — ideal permuter case. Should converge quickly.

