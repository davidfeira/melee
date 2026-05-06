---
function: grGreens_80215D54
tu: src/melee/gr/grgreens.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-plateau]
---
## grGreens_80215D54 (`src/melee/gr/grgreens.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-plateau`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Implementation is structurally correct (rotates rows of grGreens block grid: when block at (i,j) has status 1 or 2 and (i-1,j) is empty, swap-shift rows i..4 up so empty bubbles to row 4, then promote any status=2 to status=1; restart i from 1). Stuck at 78% / 95 mismatches: differences are pure register allocation chains (target uses r6 for gp/blocks-base across function while compiler picks r3, propagating through all dependent regs) plus one inner-loop scheduling issue (target re-loads blocks pointer twice per inner iteration instead of pointer-subtracting). Status is read via byte access ((u8*)blocks)[ioff+joff]>>4 which compiles to lbzx + extrwi correctly; row swap is byte-offset arithmetic so compiler emits mulli r,r,0xc0 directly without folding j*0x20 into common index expression.
- **Tried:** (1) Used array-indexed access blocks[i*6+j] -> compiler folded into i*6 then slwi 5 (wrong shape, used cmpwi instead of cmplwi). (2) Switched to byte-offset arithmetic ((u8*)blocks + i*0xC0 + j*0x20), got correct cmplwi + mulli r,r,0xc0 shape, but register allocation differs throughout.
- **Likely fix:** Permuter on register hints / variable order. The structural form is right; this is a near-textbook regalloc plateau (r6/r7/r9 vs r3/r4/r5 chain assignment).

