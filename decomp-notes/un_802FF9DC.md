---
function: un_802FF9DC
tu: src/melee/if/soundtest.c
headline: permuter-queued + mwcc-loop-opt
tags: [permuter-queued, mwcc-loop-opt, mwcc-aliasing]
---
## un_802FF9DC (`src/melee/if/soundtest.c`) — permuter-queued + mwcc-loop-opt

- **Tags:** `permuter-queued`, `mwcc-loop-opt`, `mwcc-aliasing`
- **Best fuzzy:** 23.1263%
- **Diagnosis:** UPDATE 2026-05-06: Improved baseline from 0%/155-mismatch to 23%/95-mismatch by switching to 'if(count>0) do{...}while(i<count)' shape -- removed spurious r30/r31 spills, shrank frame from -0x28 to -0x18. Remaining structural gap: target has mwcc auto-unroll-by-8 (srwi.,mtctr,bdnz inner body x8, andi tail loop), our shape keeps a single-iteration bdnz loop -- compiler refuses to unroll under do-while. Ironically the for-loop version that DID auto-unroll-by-8 also spilled r30/r31 with addi-ladder regalloc, also 0%. So mwcc has two strategies (do-while no-unroll OR for-loop unrolled-with-spills), neither matching target's unrolled-no-spills shape. Permuter territory: regalloc + loop-strategy interplay. Source shape verified correct (stack=-0x20, no callee-saves, per-iter store of un_804D6DB4 via @sda21, final lwzx uses r0=count*4 from preserved r7, lfd/fsubs/stfs to 0xf4/0xf8 of un_803F9FA4 = un_803FA098/un_803FA09C). Baseline left at do-while (23%/95) since structurally closer than for-loop variant.

