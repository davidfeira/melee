---
function: mpJointListAdd
tu: src/melee/mp/mplib.c
tags: [stack-offset, frame-size]
---
## mpJointListAdd (`src/melee/mp/mplib.c`)

- **Tags:** `stack-offset`, `frame-size`
- **Best fuzzy:** 99.98% (5 mismatches — Sonnet subagent, no commit)
- **Diagnosis:** Frame size delta — target wants `0x18`, base produces `0x20` (8 bytes too large). All 5 mismatches are stwu/stw-r31/epilogue offsets. Instruction count and opcodes match perfectly — mwcc inlines `mpLib_80057424` in both target and base, the full unrolled vtx loop matches.
- **Permuter status:** 6000+ iterations (cluster), best score 6975. Permuter outputs use permuter hacks (`volatile unsigned int new_var`, comma operator, `if (!joint_id){}`); none port cleanly.
- **Root cause:** One extra 4-byte stack slot in compiled version vs target. The inlined `mpLib_80057424` body reuses `r4 = joint_id * 0x34` in the target, but mwcc in our version spills something extra. Permuter found `joint_id & 0xFF` (score 7355) and `volatile` parameter hacks (score 6975, 7000) as proxies — neither is a semantically clean fix.
- **Likely fix:** `volatile` qualifier on `joint_id` param (permuter territory), or a different variable declaration order that changes mwcc's spill decision. Cluster permuter still running.
