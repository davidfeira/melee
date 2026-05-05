---
function: grKinokoRoute_80208564
tu: src/melee/gr/grkinokoroute.c
tags: [stack-offset, float-literal, rodata-typing]
---
## grKinokoRoute_80208564 (`src/melee/gr/grkinokoroute.c`)

- **Tags:** `stack-offset`, `float-literal`, `rodata-typing`
- **Best fuzzy:** 99.97% (Opus subagent, eliminated 5 of 8 strict mismatches)
- **Float externs:** declare `extern f32 grNKr_804DB854; extern f32 grNKr_804DB878;` and replace inline `0.0F`/`7.0F` literals with these. Fixes 5 of the 8 mismatches.
- **Typed rodata symbol:** `static const grNKr_DepthArr grNKr_803B82F4 = {{1,...,51}};` (typedef'd struct), with local struct copy via cast. Eliminates the relocation diff for the depth array.
- **Blocker:** 3 remaining stack-offset shifts (4 bytes off — target sp+0x10, ours sp+0xc): `addi r6, r1, 0x4` should be `0x8`, `addi r28, r1, 0xc` should be `0x10`, plus a related `subi`. The depths-related local needs to start at `r1+0x10` instead of `r1+0xc`. mwcc DSE eats unused locals so padding doesn't help.
- **Likely fix:** permuter — this is stack-allocation noise.
