---
function: ftCo_800B5AB0
tu: src/melee/ft/ftcpuattack.c
headline: struct-typing + frame-size
tags: [struct-typing, frame-size, permuter-blocked]
---
## ftCo_800B5AB0 (`src/melee/ft/ftcpuattack.c`) — struct-typing + frame-size

- **Tags:** `struct-typing`, `frame-size`, `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 470-instruction CPU AI weighted-attack-picker. Iterates ftCo_AttackEntry array (size 0x24) filtering by: level (entry.x20 <= x1A88.level), already-tried list (cmd not in x1A88.xCC[..xEC]), and a 4D collision/overlap test against opponent that uses 3 separate inlined sqrtf() calls when op->xC0==1 (gravity-projected ballistic prediction). Matching entries are struct-copied to a 24-slot stack buffer. Final stage runs the same weighted-random-pick logic as ftCo_800B6208 (already matched). Function returns int (cmd) and ends in __assert("ftcpuattack.c", 0x26A, "0").
- **Tried:** Wrote a structural translation but reverted: requires resolving multiple Fighter struct fields not in current type definitions (xC0, xC24/xC28/xC1C/xC20, xCC pointer to hit-state struct with x10/x14 floats). Without those typed properly, the attempt does not compile. The arg2 ftCo_AttackEntry struct also needs fields fleshed out beyond cmd/weight: x4 (s32 used as float), x8/xC (x-bounds), x10/x14 (y-bounds), x1C (modulus operand), x20 (level threshold).
- **Likely fix:** Two-step approach needed: (1) define the missing Fighter fields and the hit-state struct accessed via Fighter+0xCC; (2) flesh out ftCo_AttackEntry fields. Then write a structural translation matching the 4 sqrtf branches (op->xC0==1 path with t<ta vs t>=ta sub-cases for both Y prediction and X-overlap test). Final stage matches ftCo_800B6208's weighted-pick logic: 8x unrolled sum loop + tail loop, then 1.0/sum * acc >= r test. Pipe to permuter cluster only after a structurally-sound source reaches >=85% match. Decomp-permuter is offline currently per orchestrator note.

