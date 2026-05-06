---
function: hsd_803B5C4C
tu: src/sysdolphin/baselib/hsd_3B34.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc]
---
## hsd_803B5C4C (`src/sysdolphin/baselib/hsd_3B34.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 93.79% match (10 mismatches), all register allocation. Compiler allocates &hsd_804D2E70 to extra saved register r28 (4-reg save) and copies to r31, while target uses r31 directly (3-reg save). Two longjmp call sites use r28 in base vs r31 in target. Pure regalloc, classic permuter case.
- **Tried:** Attempt 1: m2c-style with else-if chain (92.83%). Attempt 2: explicit nested if/else for second longjmp (93.79%, eliminated b .L_803B5D18 mismatch).
- **Likely fix:** Permuter randomization of local var declaration order or call expression shape may pressure regalloc to keep address in r31 throughout, dropping r28 entirely. Permuter offline per override; flagged for cluster dispatch when available.

