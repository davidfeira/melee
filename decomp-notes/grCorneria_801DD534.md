---
function: grCorneria_801DD534
tu: src/melee/gr/grcorneria.c
tags: [tu-data-osreport, stack-offset]
---
## grCorneria_801DD534 (`src/melee/gr/grcorneria.c`)

- **Tags:** `tu-data-osreport`, `stack-offset`
- **Best fuzzy:** 99.95% (Haiku subagent attempted, reverted x2)
- **Status:** Haiku failed twice to improve from baseline 99.78%. gr/ pattern partly applied but stack frame size + 2 data offsets remain wrong.
- **Likely path:** retry with Opus and the pattern from `940801c05` / `842c69cbb` references; structurally similar to the closed gr/ cases.
