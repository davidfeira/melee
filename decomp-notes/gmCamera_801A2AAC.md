---
function: gmCamera_801A2AAC
tu: src/melee/gm/gmcamera.c
headline: regalloc + branch-direction
tags: [regalloc, branch-direction]
---
## gmCamera_801A2AAC (`src/melee/gm/gmcamera.c`) — regalloc + branch-direction

- **Tags:** `regalloc`, `branch-direction`
- **Best fuzzy:** 98.3077%
- **Diagnosis:** 2 strict mismatches at the inner switch entry: target emits 'cmpwi r0, 0x0; bge .CALL6_BLOCK; b .SWITCH_BLOCK' (call(6) reached only via taken bge, switch block via unconditional b) while current source produces 'cmpwi r0, 0x0; blt .SWITCH_BLOCK' (call(6) is fallthrough). Difference is block ordering of the then/else basic blocks. The condition is '(x44 < 2) && (x44 >= 0)' guarding call(6), else => switch on x44.
- **Tried:** (1) Inverted to 'if (x44 >= 2 || x44 < 0) { switch } else { call(6) }' -> match dropped to 89.15%, 8 mismatches; whole switch block got moved. (2) Reordered conjuncts to '(x44 >= 0) && (x44 < 2)' -> 5 mismatches at 98.27%, both compares swapped order.
- **Likely fix:** permuter-territory: looks like compiler heuristic for which side of an if-else gets the fall-through path. Try an unsigned cast trick like 'if ((u32)x44 < 2u)' to collapse range check into one compare, OR a goto-based source layout. Permuter randomization on the then/else block structure is appropriate.
