---
function: Ground_801C20E0
tu: src/melee/gr/ground.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc, frame-size]
---
## Ground_801C20E0 (`src/melee/gr/ground.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`, `frame-size`
- **Best fuzzy:** 88.9455%
- **Diagnosis:** Reached 88.95%/67 mismatches: control flow, ctr loop, byte loads, bitfield extracts, increment ordering all match. Remaining diff is GPR allocation choices (r3/r4/r5/r6/r7/r8/r9 vs target's r3/r4/r5/r6/r7/r8/r9 in different positions) and a +0x8 stack frame (-0x30 vs target -0x28) suggesting one local is stack-allocated where target keeps it in a register. Three separate lbz loads from same byte address now correctly emitted via local pointer + 3 reads. Header types.h: replaced UnkStageDat::x18_fill[8] with explicit unk18/unk1C fields.
- **Tried:** (1) Initial pass with cast-based access of unk4+0x18/+0x1C fields, do/while loop and inline byte reads — got 83.7% (frame too large, CSE'd byte reads, hoisted arr). (2) Switched to for(i=0,byte_off=0; i<count; byte_off+=8, i++) loop, added named struct fields unk18/unk1C in UnkStageDat, used LightOverrideFlags bitfield struct ordered MSB-first (a:1, b:1, c:1, _:5) to suppress byte CSE — got 88.95%. Bit-extract positions match exactly (extrwi 24/25/26).
- **Likely fix:** Permuter run: this is mostly register allocation pressure. The remaining structural pieces (extra 'b' branch from break, stack frame +0x8) likely fall out once a permuted variant lets mwcc keep one more value in registers. Inner loop body is fully shape-matched.

