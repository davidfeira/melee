---
function: lbSnap_8001DC0C
tu: src/melee/lb/lbsnap.c
headline: struct-split + permuter-false-positive
tags: [struct-split, permuter-false-positive, data-symbols-missing, regalloc]
---
## lbSnap_8001DC0C (`src/melee/lb/lbsnap.c`) — struct-split + permuter-false-positive

- **Tags:** `struct-split`, `permuter-false-positive`, `data-symbols-missing`, `regalloc`
- **Best fuzzy:** 99.9688%
- **Diagnosis:** Was 99.85% with 4 mismatches. Discovered Unk803BACC8 struct in lbsnap.static.h is 0x20 but should be 0x2C (3 trailing words: 0x00000000 at +0x1C, 0xFFFFFFFF at +0x20, 0x00000000 at +0x24/+0x28). Original layout placed -1 at +0x1C; correct layout has x1C field=0 and -1 at +0x20. Extending struct + initializer brings strict to 99.875% (3 reloc false-positives + 1 real regalloc remain). 3 reloc false-positives are permuter-false-positive class (data anchor): target uses lbSnap_803BACC8+0x54/0x80/0xAC for format strings while we emit @308/@309/@310 separate symbols (same final addresses post-link, but objdiff strict mismatches). Real diff: 'mullw r3, r28, r6' (target uses r28=0 as high word of u64*u64) vs 'mullw r3, r3, r6' (we use r3, the actual high word of u64 quotient from __div2i). The compiler somehow proves seconds high word is 0 — could not reproduce by changing 'OSTime seconds' to 'u32 seconds' or casting OSSecondsToTicks((u32)seconds) (both collapse to a single 32-bit mullw and break the rest of the function). Needs a source shape that keeps the u64*u64 multiply expansion AND zeros r28.
- **Tried:** 1) Extended Unk803BACC8 struct by 0xC bytes with init { -1,-1,-1,-1,0,0,0,0,0,0,0,0 } at pad20. SUCCESS for 3 layout-related fixes. 2) Changed 'OSTime seconds' -> 'u32 seconds'. FAIL — collapses to 32-bit mullw (10+ stb regalloc cascade). 3) Kept OSTime seconds, cast OSSecondsToTicks((u32)seconds). FAIL — same collapse.
- **Likely fix:** Header change is real and should be committed. For the regalloc/reloc-anchor remainder: do NOT dispatch permuter (3 of 4 are false-positives that permuter cannot fix). Manual: maybe '__OSBusClock' definition or OS_TIMER_CLOCK macro needs a u64 cast to force u64*u64 with provably-zero high word in the literal. Or maybe seconds is an OSTime + a separate u32 hi=0 hint. Try declaring 'seconds = (u64)(u32)(ticks / TIMER_CLOCK)' — explicit truncate-then-zero-extend pattern.
