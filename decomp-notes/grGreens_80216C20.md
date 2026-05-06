---
function: grGreens_80216C20
tu: src/melee/gr/grgreens.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, instruction-scheduling]
---
## grGreens_80216C20 (`src/melee/gr/grgreens.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `instruction-scheduling`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Structural shape correct but mwcc hoists/sinks pointer subexpressions differently from target. Best attempt 75.6% (76 mismatches). Target keeps (i-1)*0xC0 and (i+1)*0xC0 as bare integer strides used inside inner loop with lbzx/lwzx; my source either over-hoists base pointer (arwing.xCC+joff) or recomputes too aggressively. Required header change: grGreens_802150C4 prototype updated from UNK_RET/UNK_PARAMS to (Ground_GObj*, int, int).
- **Tried:** Attempt 1: cached base = (u8*)x8_blocks+joff inside if-branch, used base[(i-1)*0xC0] indexing. 75.6%. Attempt 2: hoisted prev_i_off/next_i_off to outer loop scope, kept base computation. 74.0%. Both produce too many live values, mwcc reshapes register allocation from r22-r31 (target) to r17-r31 (mine), bumping frame size from 0x40 to 0x50/0x58.
- **Likely fix:** Try writing as fully redundant per-byte access (no temp variables): use ((u8*)gp->gv.greens.x8_blocks)[(i-1)*0xC0 + joff] directly inline at every neighbor read instead of caching base. Re-fetch x18 separately. Permuter pass should resolve remaining hoisting/scheduling once shape is closer.

