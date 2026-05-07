---
function: grBigBlueRoute_8020C530
tu: src/melee/gr/grbigblueroute.c
headline: instruction-scheduling + regalloc
tags: [instruction-scheduling, regalloc, reloc-symbol-false-positive, permuter-territory]
---
## grBigBlueRoute_8020C530 (`src/melee/gr/grbigblueroute.c`) — instruction-scheduling + regalloc

- **Tags:** `instruction-scheduling`, `regalloc`, `reloc-symbol-false-positive`, `permuter-territory`
- **Best fuzzy:** 98.7192%
- **Diagnosis:** 98.67% match with 5 mismatches: (1) mtctr placement in pass-2 CTR setup (instruction scheduling), (2) addi r5,r6,0x0 vs li r5,0x0 (r6 known-zero regalloc), (3) __FILE__ string symbol named @185 vs grBb_Route_803E61D4 (data-anchor false positive - post-link bytes identical). Function counts free RouteEntry slots (bit7==0) over 30-item array then picks random one, returning the index.
- **Tried:** Attempt 1: manually unrolled CTR loop with explicit offset/idx variables, generated lbz with hardcoded offsets (61%). Attempt 2: simple for(i<30) loop with i*0x2C offset, compiler auto-unrolled to CTR=3 x 10 (98.67%).
- **Likely fix:** Permuter can resolve the mtctr scheduling and addi-vs-li. __FILE__ reloc mismatch is a data-anchor false positive (objdiff strict only). Fuzzy match already 98.72%.

