---
function: grGreens_802166C4
tu: src/melee/gr/grgreens.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, frame-size]
---
## grGreens_802166C4 (`src/melee/gr/grgreens.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `frame-size`
- **Best fuzzy:** 80.9767%
- **Diagnosis:** Source structure verified at 84.6% match (150 mismatches). Logic cleanly decomp'd: weighted column picker over 6 cols x 5 rows, weights from grGr_params x8/xC/x10/x14/x18/x1C, three-way left/right/full random selection with HSD_ASSERT messages 'i<Gr_Greens_Block_Column*2' (lines 1693, 1711) and 'i<Gr_Greens_Block_Column' (line 1702). Block fall-clear loop calls Ground_801C4A08/grMaterial_801C8CDC/HSD_JObjSetFlags/grGreens_80215D54.
- **Tried:** Two source-shape attempts. Attempt 1 used picked_j/picked_i locals (80.9%). Attempt 2 renamed to i/j with #define Gr_Greens_Block_Column 3 to match assert string 'i<Gr_Greens_Block_Column*2' / 'i<Gr_Greens_Block_Column' (84.6%). Asserts 0x2D0/0x2EC verified by .data diff inspection. Header grgreens.h updated: grGreens_80215ED8 prototype changed from UNK_PARAMS to (Ground_GObj*, int, int).
- **Likely fix:** Permuter regalloc (most diffs are r9/r11 swaps and r10/r9 shifts — register allocation only). Frame size still differs by 0x10 bytes (target -0x48, base -0x38) — may need an extra unused local or PAD_STACK to coax a wider frame. Also one DIFF_DELETE 'addi r28, r1, 0x28' indicates target precomputes the buffer address into r28 once and reuses r28 across the function body, while base recomputes (r1, offset) at each access — try lifting 'u8* p = weights;' as an explicit pointer used in subsequent reads.

