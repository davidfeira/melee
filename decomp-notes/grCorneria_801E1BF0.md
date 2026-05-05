---
function: grCorneria_801E1BF0
tu: src/melee/gr/grcorneria.c
headline: permuter-false-positive
tags: [permuter-false-positive]
---
## grCorneria_801E1BF0 (`src/melee/gr/grcorneria.c`) — permuter-false-positive

- **Tags:** `permuter-false-positive`
- **Best fuzzy:** 99.9817%
- **Diagnosis:** 55 mismatches: all reloc-symbol false positives. Strict 99.14% fuzzy 99.98% — diff dominated by permuter false-positive class; permuter scorer treats as equivalent so dispatch is wasted.
- **Tried:** compact-brief inspection only; no source variants
- **Likely fix:** needs cross-TU symbol/data layout fix or wait for adjacent TU work, not permuter
