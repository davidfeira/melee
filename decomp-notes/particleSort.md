---
function: particleSort
tu: src/sysdolphin/baselib/psdisp.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## particleSort (`src/sysdolphin/baselib/psdisp.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 90.2137%
- **Diagnosis:** 93.6% match after 2 attempts. All remaining 122 mismatches reduce to 3-5 root register allocation decisions: (1) r29/r30 swap for particle_ptr vs arg0*4 in prologue; (2) r3/r0 swap for the loaded bucket-head variable in the merge phase; (3) r4/r0 swap for head1; (4) r6/r4 swap for tail1 -- all cascading through 16 unrolled bucket merge iterations (~112 instructions total). Branch direction (bne vs beq for head1==NULL check) is a secondary effect of the register ordering, falling under mwcc-branch-inversion. No structural issues remain.
- **Tried:** (1) Direct static array access for merge phase, manually unrolled 16 buckets -- 90.2% match. (2) Pointer-walk using *(p += 2) idiom for merge phase -- 93.6% match, correctly generates lwzu for bucket iteration but register assignment for p/h/head1/tail1 is shifted vs target.
- **Likely fix:** Permuter should resolve: r29/r30 swap for particle_ptr/arg0*4, and r3/r0/r4/r6 register assignments for the merge-phase variables (h, head1, tail1, bucket-walk pointer).

