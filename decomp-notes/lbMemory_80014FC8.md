---
function: lbMemory_80014FC8
tu: src/melee/lb/lbmemory.c
headline: regalloc
tags: [regalloc]
---
## lbMemory_80014FC8 (`src/melee/lb/lbmemory.c`) — regalloc

- **Tags:** `regalloc`
- **Best fuzzy:** 99.3243%
- **Diagnosis:** 10 mismatches, all DIFF_ARG_MISMATCH: pure r24/r30 swap for arg0/size params. target keeps arg0 in r24, size in r30; ours keeps arg0 in r30, size in r24. mwcc colors saved-regs in opposite order from target.
- **Tried:** V1 reordered aligned_size before start=arg0->x4_lo (no change). V2 swapped 'available_space >= aligned_size' to 'aligned_size <= available_space' (worse, +1 op-mismatch from cmplw swap).
- **Likely fix:** permuter — pure regalloc noise, well below 15-instr threshold and exactly the kind of register-coloring permutation it handles.
