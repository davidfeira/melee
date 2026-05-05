---
function: gmCamera_801A26C0
tu: src/melee/gm/gmcamera.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## gmCamera_801A26C0 (`src/melee/gm/gmcamera.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 97.963%
- **Diagnosis:** 9 strict mismatches all centered on r29/r30 swap for loop iterator i + a single 'addi r31, r30, 0' vs 'li r31, 0' for the NULL store source. Target picks r30 for i, base picks r29. Function does setup with multiple calls then a 3-iter loop clearing unk->x48[i] = NULL. The addi-vs-li picks r31 from r30 (which holds 0 since i=0) — equivalent code, mwcc just chose to copy from the existing zero register.
- **Tried:** (1) hoisted NULL into 'void* zero = NULL' temp before the loop, no diff change. (2) moved 's32 i' declaration into the inner if-block scope, no diff change. Both variants produced identical 9-mismatch output.
- **Likely fix:** Pure permuter territory — register allocation (r29 vs r30 for i) plus instruction-selection (addi vs li for NULL materialization). Manual source-shape changes don't shift mwcc's regalloc here. Dispatch to cluster permuter.
