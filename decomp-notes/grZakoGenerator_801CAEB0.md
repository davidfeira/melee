---
function: grZakoGenerator_801CAEB0
tu: src/melee/gr/grzakogenerator.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling]
---
## grZakoGenerator_801CAEB0 (`src/melee/gr/grzakogenerator.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`
- **Best fuzzy:** 81.25%
- **Diagnosis:** At 81.25% strict, 10 mismatches: 7 regalloc + 3 real where target hoists 'li r0, 0' (NULL constant for sentinel.x4) above the cmpwi/bnelr branch and uses 'addi r6, r5, 0x3c0' to materialize the sentinel address pre-branch, while base schedules these post-branch. Source is the obvious shape: load lbl_8049F030.x4, check sentinel.x0==-1, set x0/x8/x4=NULL. Function is tiny (~16 instr) so few source-shape levers.
- **Tried:** V1: cached lbl_8049F030.x4 in local pointer 'data' for the if check only - dropped to 9 mismatches but match% worsened (79.31%) by removing the sentinel address calc entirely (wrong direction). V2: introduced grZakoGenerator_Entry* sentinel = &lbl_8049F030.x4->sentinel for if + first store - identical 10 mismatches at 81.25% (no effect).
- **Likely fix:** Permuter territory: pure instruction scheduling + register allocation. Dispatch with --auto-permute --cluster. No structural source change appears to push MWCC into the desired schedule; the function is too small for source rearrangement to matter much.
