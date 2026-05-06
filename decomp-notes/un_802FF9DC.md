---
function: un_802FF9DC
tu: src/melee/if/soundtest.c
headline: mwcc-loop-opt + mwcc-aliasing
tags: [mwcc-loop-opt, mwcc-aliasing, permuter-queued]
---
## un_802FF9DC (`src/melee/if/soundtest.c`) — mwcc-loop-opt + mwcc-aliasing

- **Tags:** `mwcc-loop-opt`, `mwcc-aliasing`, `permuter-queued`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Target asm is an 8x unrolled sum loop where un_804D6DB4 (running sum) is reloaded/stored every unroll iteration, and un_804D6DA8->[6] (arr base) is also reloaded each iter. MWCC computes ctr=count/8 then bdnz, with andi tail. My attempts produce either no unroll (acc in register) or different unroll shape with wholly different prologue (saves r30/r31, larger frame, addi-based pointer arithmetic instead of slwi+lwzx). Compiler refuses to emit the target shape from natural loop body 'un_804D6DB4 += arr[i];'.
- **Tried:** (1) for-loop with local sum acc, store back to un_804D6DB4 on each iter -- compiler hoists arr base, no unroll match. (2) direct 'un_804D6DB4 += ((int**)un_804D6DA8)[6][i];' -- compiler unrolls but with elaborate addi ladder over r12/r11/r10..., spills r30/r31, frame=0x28 vs target 0x20. Header decl updated to 'int un_802FF9DC(void)'. Discovered: un_803FA098 and un_803FA09C should be separate static floats, not part of struct SoundTestData (fields at +0xF4/+0xF8 from un_803F9FA4 anchor).
- **Likely fix:** Permuter territory once decomp-permuter is back online -- the structural shape (loop body, return value, calls) is correct; remaining diff is mwcc unroll-strategy / regalloc / prologue choices. May also need to express the loop in a way that signals 'arr base may alias the sum store' so MWCC keeps reloads inside the loop body. Try: writing as 'while(--ctr)' style or with explicit volatile-cast on the global to force per-iter reload pattern matching the target.

