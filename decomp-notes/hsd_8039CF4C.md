---
function: hsd_8039CF4C
tu: src/sysdolphin/baselib/particle.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, data-anchor, permuter-false-positive]
---
## hsd_8039CF4C (`src/sysdolphin/baselib/particle.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `data-anchor`, `permuter-false-positive`
- **Best fuzzy:** 96.5873%
- **Diagnosis:** Two distinct blocker classes. (1) 4 instruction diff at offset 47628-47636: addi r4,r4,@l / slwi r0,r3,2 / add r30,r4,r0 vs slwi r3,r3,2 / addi r0,r4,@l / add r30,r0,r3 — both compute &hsd_804D08E8[index] identically but in different evaluation order using different temp registers. Pure regalloc/scheduling mismatch. (2) 4 mismatches at 47704-47716: lbl_8040C010/lbl_8040C01C vs @3586/@3587 — anonymous compiler-generated symbol names for string literals in ref_INC assert vs named labels from target .o (extracted from DOL). Post-link bytes are identical; this is a data-anchor false-positive. Function body is identical to upstream matched version.
- **Tried:** Attempt 1: extracted base address into separate variable (HSD_JObj** base = hsd_804D08E8; p = base + index) — caused extra stack slot (frame grew from 0x20 to 0x28), 19 mismatches. Attempt 2: &hsd_804D08E8[0] + index — same 8 mismatches as baseline, no change.
- **Likely fix:** Permuter needed for regalloc/scheduling. Data-anchor false-positive (lbl_8040C010 vs @3586) cannot be fixed in source — requires either accepting as equivalent or finding a way to name the string literals explicitly. Upstream achieved 100% with identical source, suggesting the data-anchor mismatches resolve under fuzzy matching or the permuter handles them.

