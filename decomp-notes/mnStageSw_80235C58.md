---
function: mnStageSw_80235C58
tu: src/melee/mn/mnstagesw.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, data-anchor]
---
## mnStageSw_80235C58 (`src/melee/mn/mnstagesw.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `data-anchor`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 94.13%, 37 diffs. Manual structure work landed: added float array mnStageSw_803ED488 (15 floats) BEFORE mnStageSw_803ED4C4 in the data section -- this anchored the lbz disp 0x3C addressing form (saved 6 instr-delete diffs). Restructured none_unlocked flag from pre-init to post-loop set (do-while shape) -- saved 5 diffs. Remaining 37 diffs: ~32 pure regalloc renames (r28/r31, r27/r30, r29/r28 swaps), 2 DIFF_DELETE for clrlwi r30,r3,24 / clrlwi r28,r0,24 after first arg0<15 branch (target re-clrlwis the literals 0/14 already in u8 range -- target stores via u8-typed locals while base hoists them), and 1 symbol-name diff: target uses mnStageSw_803ED488@l while base emits anonymous '...data.0@l' (MWCC literal-pool alias since the float array is unused in this function -- only its address-base is borrowed for the 0x3C-displaced byte-array load). Subagent override: decomp-permuter offline so cannot --auto-permute.

