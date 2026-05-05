---
function: mnEvent_8024CE74
tu: src/melee/mn/mnevent.c
headline: regalloc
tags: [regalloc]
---
## mnEvent_8024CE74 (`src/melee/mn/mnevent.c`) — regalloc

- **Tags:** `regalloc`
- **Best fuzzy:** 99.4231%
- **Diagnosis:** Single mismatch at insn 44: target emits 'addi r30, r31, 0x0' but base wants 'li r30, 0x0'. Compiler reuses r31's freshly-loaded zero (count=0) for i=0 in the for-loop init, instead of independently materializing 0 in r30.
- **Tried:** (1) Removed redundant 'count = 0;' reassignment before the for-loop -> regressed to 3 mismatches (li r31, 0 got moved/eliminated). (2) Rewrote loop as do-while with explicit count=0; i=0; init -> still 1 mismatch, identical addi r30, r31, 0 vs li r30, 0. Source-shape didn't break the regalloc preference.
- **Likely fix:** Permuter territory — pure register-allocation choice. Cluster permuter dispatched.
