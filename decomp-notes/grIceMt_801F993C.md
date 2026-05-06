---
function: grIceMt_801F993C
tu: src/melee/gr/gricemt.c
headline: bss-anchor + data-anchor
tags: [bss-anchor, data-anchor, frame-size, permuter-blocked]
---
## grIceMt_801F993C (`src/melee/gr/gricemt.c`) — bss-anchor + data-anchor

- **Tags:** `bss-anchor`, `data-anchor`, `frame-size`, `permuter-blocked`
- **Best fuzzy:** 77.41%
- **Diagnosis:** Function compiles to 76.39% match (81 mismatches). Two structural blockers: (1) compiler emits TWO anchors data.0@ha (string literals) and bss.0@ha (grIm_803E4068 array) where target uses single grIm_803E4068@ha covering both. Sibling matched function grIceMt_801F686C uses the same single anchor 'addi r3, r31, 0x690' (grIm_803E4068+0x690 = string "gricemt.c"). (2) Extra register save (r27 via stmw r27 vs target's separate stw r28-r31) inflates stack from -0x28 to -0x40. Likely root cause: grIm_803E4068[6] is declared uninitialized (BSS) in source line 83, but symbols.txt places it in .data. Initializing the array would put it in .data alongside string literals, allowing single-anchor merge. Other matched siblings work because they only use grIm_803E4068, not grIm_803E4068+string-literal pairs in same frame.
- **Tried:** (1) Clean for-loop with break on match: 76.39%, single-block break form. (2) for(...&&...){} comma-loop variant: regressed to 35.78%, kept attempt 1.
- **Likely fix:** Initialize grIm_803E4068[6] with its actual data values (m2c suggested {1,180.0f,-180.0f},{2,190.0f,-180.0f},{3,190.0f,-195.0f},{4,195.0f,-185.0f},{5,190.0f,-200.0f},{6,180.0f,-190.0f} but these need cross-checking against linked binary bytes at 0x803E4068). Also fix struct: x4/x8 should be f32 not u32 (lfs loads). With array in .data, both string literal anchor and array anchor merge into single grIm_803E4068@ha reference, eliminating 2 lis loads, 1 register spill, and freeing r27. Will likely also unblock anchor matching for other functions in TU touching both array and strings.

