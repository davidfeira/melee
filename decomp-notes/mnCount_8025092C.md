---
function: mnCount_8025092C
tu: src/melee/mn/mncount.c
headline: frame-size + stack-offset
tags: [frame-size, stack-offset, regalloc]
---
## mnCount_8025092C (`src/melee/mn/mncount.c`) — frame-size + stack-offset

- **Tags:** `frame-size`, `stack-offset`, `regalloc`
- **Best fuzzy:** 99.3538%
- **Diagnosis:** Frame size 0x110 vs target 0x118 (+8 bytes), array at 0x20 vs 0x1c, tmp scalars at 0x18/0x1c vs 0x14/0x18, plus regalloc r6/r8 vs r8/r9 in inner sort loop. Adding PAD_STACK(4) at function top fixes the +8 byte frame size (drops to 29 mismatches from 34) but does not shift the array down to 0x1c — pad lands at low addresses. Tried _pad[16] at top: bumped frame to 0x120 (overshoot). Need pad bytes to land BETWEEN array end and stmw save area to push everything down by 4.
- **Tried:** 1) declare CountEntry tmp at function scope (no change); 2) PAD_STACK(8) at top after entries-block { (29 mismatches, frame correct, array still 0x20); 3) PAD_STACK(4) at top (same 29 mismatches); 4) PAD_STACK(8) declared after int locals, before if (made array at 0x28, worse); 5) UNUSED unsigned char _pad[16] at function top (overshot to 0x120 frame).
- **Likely fix:** Need a way to add 16 bytes pad ABOVE the array (between array end and stmw). PAD_STACK with sibling mnCount_8025035C uses PAD_STACK(4) and matches — that function's frame is 0x108 with array at 0x18. Possibly mode parameter being bool vs s32 affects layout, or callee-saved register count differs causing different alignment. Inner loop regalloc (r6/r8 indices vs r8/r9) is permuter-territory once frame is fixed.
