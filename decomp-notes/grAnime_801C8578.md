---
function: grAnime_801C8578
tu: src/melee/gr/granime.c
headline: permuter-queued + branch-pattern
tags: [permuter-queued, branch-pattern, dead-loads]
---
## grAnime_801C8578 (`src/melee/gr/granime.c`) — permuter-queued + branch-pattern

- **Tags:** `permuter-queued`, `branch-pattern`, `dead-loads`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 89.13% match (15 mismatches). Recursive 4-way pre-order traversal of HSD_Joint tree (child=+8, next=+C) with shared counter. Source compiles cleanly but mwcc emits bne+b unconditional pairs at the 'if (*ctr==0) goto end' joins where the source generates direct beq. Also target has redundant lwz/cmpwi r0 reloads at merge labels (.L_801C8620, .L_801C86B8) that the source doesn't reproduce. Header signature changed void*,void* -> HSD_Joint*,s32* and call site at grAnime_801C86D4 cast-adjusted; both required to compile. Permuter territory: branch direction inversion + dead reload patterns are classic mwcc artifacts.

