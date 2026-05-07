---
function: ftColl_8007BAC0
tu: src/melee/ft/ftcoll.c
headline: r30-r31-swap + regalloc
tags: [r30-r31-swap, regalloc]
---
## ftColl_8007BAC0 (`src/melee/ft/ftcoll.c`) — r30-r31-swap + regalloc

- **Tags:** `r30-r31-swap`, `regalloc`
- **Best fuzzy:** 98.9552%
- **Diagnosis:** All 13 mismatches are a pure r30/r31 swap: target has max=r31 and arr=r30, our build produces max=r30 and arr=r31. The code logic, structure, and control flow are identical to upstream/master which is marked as matched. Swapping local declaration order did not change the register assignment; removing the extra nested braces also failed to change allocation.
- **Tried:** 1) Moved arr declaration before max (made it worse, +2 mismatches due to stack offset change). 2) Removed nested braces around the main body (same 13 mismatches). Upstream implementation is byte-identical to our source and is marked matched, suggesting this may be a permuter-territory or tooling-environment difference.
- **Likely fix:** Permuter with r30/r31 swap exploration; alternatively try a VOLATILE or register keyword hint on max to force earlier allocation, or investigate if upstream was matched against a different build environment.

