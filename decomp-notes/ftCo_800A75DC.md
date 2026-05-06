---
function: ftCo_800A75DC
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-queued + frame-size
tags: [permuter-queued, frame-size, inlining, stack-offset, regalloc]
---
## ftCo_800A75DC (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-queued + frame-size

- **Tags:** `permuter-queued`, `frame-size`, `inlining`, `stack-offset`, `regalloc`
- **Best fuzzy:** 43.2468%
- **Diagnosis:** Source structurally correct (matches asm flow + m2c output); frame layout diverges. Target preserves r26 across whole air-branch as a hoisted &fp0->x1A88.x60 pointer (addi r26, r28, 0x1ae8) and uses 0x78 frame; base uses 0x58 frame, preserves only r27, recomputes &x60 each time. ftCo_800A1F3C is being inlined (good — matches target's inlined stores) but compiler picks different stack offsets (sp40 at 0x24 vs target 0x40, sp50 at 0x34 vs target 0x50). Stack args for mpCheckFloor land at 0x8(r1) in target vs 0x8(r1) in base too, but other stack ops differ. ftCo_800A2718_dontinline forced real call (good). Still 68.78% match.
- **Tried:** Attempt 1 (42.93%): direct ftCo_800A2718 call inlined → emitted inline body of ftCo_800A2718 with stage_info checks and Ground_801C5794 calls (worse than target). Attempt 2 (68.78%): switched to ftCo_800A2718_dontinline + ftCo_800A1F3C calls for x60==0 stores. Frame still 0x58 not 0x78.
- **Likely fix:** Need to coax compiler to preserve r26 as &fp0->x1A88.x60. Maybe explicit local int* x60_ptr = &fp0->x1A88.x60; threaded through calls. Also try adding more locals or reordering to push frame larger. Permuter territory: stack-offset + hoisting choices.

