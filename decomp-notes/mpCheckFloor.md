---
function: mpCheckFloor
tu: src/melee/mp/mplib.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, stack-offset]
---
## mpCheckFloor (`src/melee/mp/mplib.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `stack-offset`
- **Best fuzzy:** 99.6772%
- **Diagnosis:** 60 mismatches: 40 stack-offset + 13 permuter-false-positive + 4 regalloc + 3 frame-size. TU mp/mplib.c has 4 prior stuck siblings indicating TU-wide structural blocker (likely missing/wrong data symbols affecting frame layout across all functions in this TU). compact-brief recommends log-stuck-immediately.
- **Tried:** picker selection only; compact-brief showed TU-wide blocker before any source attempts
- **Likely fix:** Resolve TU-wide data layout for mplib.c (likely missing globals or struct field that causes cascading stack-offset shifts). Permuter-false-positive subset suggests reloc-symbol equivalence (BSS/sdata anchors) that won't be fixed by permuter.
