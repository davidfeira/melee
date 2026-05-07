---
function: grVenom_80204F20
tu: src/melee/gr/grvenom.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, permuter-territory]
---
## grVenom_80204F20 (`src/melee/gr/grvenom.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `permuter-territory`
- **Best fuzzy:** 90.9286%
- **Diagnosis:** 90.24% match (73 mismatches). Code structure and semantics are correct. Remaining diff is entirely register allocation: compiler picks r0 for idx load (vs target r4) causing slwi result to go into callee-saved r28 instead of volatile r0, producing an extra saved register (r28 vs target r29-r31 only), shifting stack frame from -0x38 to -0x28 and offsetting all stack slots by 0x10. All 73 mismatches cascade from this one extra GPR save.
- **Tried:** Attempt 1: idx local variable, base[] indexing, x10_flags.b2=0. Attempt 2: eliminated idx variable, used raw pointer cast - made it worse (112 mismatches). Best result is attempt 1 at 90.24%.
- **Likely fix:** Permuter should resolve register allocation: eliminate the extra r28 callee-save by finding expression ordering that makes the compiler keep idx in r4 (volatile) and slwi into r0, rather than idx in r0 and slwi into r28 (callee-save).

