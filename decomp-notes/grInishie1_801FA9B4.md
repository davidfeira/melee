---
function: grInishie1_801FA9B4
tu: src/melee/gr/grinishie1.c
headline: regalloc + r30-r31-swap
tags: [regalloc, r30-r31-swap, permuter-territory, data-symbols-missing]
---
## grInishie1_801FA9B4 (`src/melee/gr/grinishie1.c`) — regalloc + r30-r31-swap

- **Tags:** `regalloc`, `r30-r31-swap`, `permuter-territory`, `data-symbols-missing`
- **Best fuzzy:** 98.9831%
- **Diagnosis:** After adding grI1_803E48C8 (u32[11] data anchor) and StageData grI1_803E4950 to fix OSReport string offsets, reached 98.90% with 12 mismatches. All remaining mismatches are r29/r30 swap: r29=cb/r30=gobj in target vs r30=cb/r29=gobj in base. Data layout fix was essential: grI1_803E48C8 must be first global in .data section so compiler uses it as @ha/@l base. Format string ends up at grI1_803E48C8+0xBC and filename at grI1_803E48C8+0xE0 due to StageData struct interleaving.
- **Tried:** 1. Removed unk44-unk50 fields from grInishie1_stuff struct (upstream sync). 2. Added u32 grI1_803E48C8[11] as first data global and StageData grI1_803E4950 declaration to produce correct data section layout.
- **Likely fix:** Permuter r29/r30 register allocation swap. The cb and gobj variables need r29=cb, r30=gobj instead of r30=cb, r29=gobj. Try reordering local variable declarations or adding a volatile hint to swap allocation.

