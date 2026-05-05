---
function: grZebes_801DA254
tu: src/melee/gr/grzebes.c
headline: tu-wide-data + permuter-false-positive
tags: [tu-wide-data, permuter-false-positive]
---
## grZebes_801DA254 (`src/melee/gr/grzebes.c`) — tu-wide-data + permuter-false-positive

- **Tags:** `tu-wide-data`, `permuter-false-positive`
- **Best fuzzy:** 99.9802%
- **Diagnosis:** 6 mismatches at 99.78% strict / 99.98% fuzzy. 4 are SDA21 literal-pool index drift TU-wide: target uses @604/@605 (int pair), @309 (f64), @625 (f64); base uses @625/@626/@319/@646. Constant deltas: +21 int literals, +10 f64 literals before this function. Means earlier functions in grzebes.c TU emit too many literals -- same TU-wide rodata blocker as grZebes_801DC9DC and grZebes_801DA0C4 (30.5%). Remaining 2 are local layout: target has result_passed at sp+0x1c (adjacent to result_built at 0x20), base has result_passed at sp+0x14 with 8-byte gap before result_built at 0x20. Same 0x78 frame size in both. Permuter plateaued at score 5 over 121 outputs (180min wall) -- best output added a dead inline_fn wrapper and unreachable code which slightly improved layout but didn't reach 0.
- **Tried:** (1) Removed PAD_STACK(8) entirely -> 46 mismatches/99.39%, frame shrank to 0x70. Reverted. (2) Moved PAD_STACK(8) inside the if-block before c1/c2 declarations -> identical 6 mismatches (no change). Reverted. (3) Reordered locals so GXColor result comes first before c1/c2 -> 19 mismatches/99.65%, c1/c2 shifted to lower offsets. Reverted. The 4 SDA literal mismatches are unfixable from this function alone -- they require fixing earlier functions' literal emission patterns to reduce the int/f64 pool counts by 21/10 respectively.
- **Likely fix:** Two-part: (a) TU-wide -- fix grZebes_801DA0C4 (30.5% match, 100 instructions, the function from the grZebes_801DC9DC note re @595 literal pool). Reducing its literal emissions cascades to fix the @604/@605/@309/@625 indices in grZebes_801DA254. (b) Local layout -- find a source shape that makes mwcc allocate result_passed adjacent to result_built (eliminate the 8-byte gap at sp+0x18). May require an explicit 8-byte temp or different expression order. Note: permuter-false-positive tag because the 0x14 vs 0x1c offset is a real byte difference, not a reloc-symbol equivalence -- post-link they will differ.
