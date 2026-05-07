---
function: lbMemory_8001564C
tu: src/melee/lb/lbmemory.c
headline: frame-size + mwcc-branch-inversion
tags: [frame-size, mwcc-branch-inversion, mwcc-loop-opt, regalloc]
---
## lbMemory_8001564C (`src/melee/lb/lbmemory.c`) — frame-size + mwcc-branch-inversion

- **Tags:** `frame-size`, `mwcc-branch-inversion`, `mwcc-loop-opt`, `regalloc`
- **Best fuzzy:** 38.7826%
- **Diagnosis:** Function initializes the Allocator free lists (x62C freeslot array via 0xC-stride FreeNode cast, x698 via 6 Handle structs at x638-x688). Three blockers: (1) Frame is 0x28 in target but we generate 0x20 despite saving r29/r30/r31 - unknown reason for extra 8 bytes; (2) ARGetSize comparison needs ble+b+ARGetSize layout (MWCC-specific: 'if (first > limit) {}' with empty true branch generates ble.else; b.end; .else:ARGetSize pattern using preloaded r0=limit as the result without explicit reload) but we generate bgt layout; (3) Main loop needs CTR=8 with bdnz for 8-iteration do-while of 16 elements each, we get comparison-based loop instead.
- **Tried:** (1) if(ARGetSize()>0x01000000){}else{...} - generates bgt layout; (2) ternary (ARGetSize()<=limit)?ARGetSize():limit - generates inverted ternary bgt layout; (3) FreeNode struct with p[j].x8=&nodes[i+j+1].x8 unrolled 16x do-while - loop body instruction-matches but uses wrong registers and no CTR; (4) Handle x638_handles[6] in Allocator (same size 0x60 as u8 x638[0x60]).
- **Likely fix:** Frame: may need extra local variable or array to push sp14 to sp+0x14. ARGetSize: may need the u32 initialized-before-ARGetSize pattern where variable IS the comparison value, letting compiler avoid reload. CTR loop: may need explicit 8-iteration do-while with CTR decrement that MWCC recognizes as counted loop.

