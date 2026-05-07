---
function: grOnett_801E40E4
tu: src/melee/gr/gronett.c
headline: branch-pattern + sdata2-float
tags: [branch-pattern, sdata2-float, fuzzy-vs-strict]
---
## grOnett_801E40E4 (`src/melee/gr/gronett.c`) — branch-pattern + sdata2-float

- **Tags:** `branch-pattern`, `sdata2-float`, `fuzzy-vs-strict`
- **Best fuzzy:** 98.0392%
- **Diagnosis:** Switch with cases 0 and 3 (gap at 1-2) generates two consecutive unreachable 'b .default' instructions in the original binary (at 801E4114 and 801E4118). Our compiler generates only one. Neither break vs return in case 0 nor adding default: break changes the branch count. The two lfd mismatches are sdata2-float false positives (grOt_804DB2B0@sda21 vs @331@sda21, same bytes). Upstream/doldecomp marks this as matched with identical source, suggesting a toolchain version difference.
- **Tried:** 1. Changed case 0 second return to break — no change. 2. Added default: break — no change, sdata2 symbol index shifted from @331 to @332.
- **Likely fix:** Need to identify what CodeWarrior source pattern generates two consecutive b-to-default instructions for a switch with cases 0 and 3. May require a goto-based rewrite, an intermediate empty case (case 1: case 2:), or a compiler hint. Alternatively, this may be a toolchain-version divergence where our MWCC build settings are slightly different from the upstream reference build.

