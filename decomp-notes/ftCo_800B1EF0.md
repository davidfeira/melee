---
function: ftCo_800B1EF0
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, r30-r31-swap, stack-offset]
---
## ftCo_800B1EF0 (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `r30-r31-swap`, `stack-offset`
- **Best fuzzy:** 39.467%
- **Diagnosis:** Structure correct (control flow, calls, all 8 bit-field assigns in both branches). Match 39.46%, 196 mismatches dominated by register-allocation diffs: target uses r30=fp,r31=temp_r31 with r28/r29 as int sentinels (var_r28, const 0); base places fp in r28 instead. Also sp28 stack offset 0x28 (target) vs 0x2c (base) -- 4-byte gap above Vec3 in target's frame. Stack total matches at 0x48. Target has unique pattern: bit-stores in second branch use r28 (= 1) which is also reused as kind-switch sentinel after bl ftCo_800A4BEC, producing 'b L_END / mr r28,r29' switch shape (vs B00F8's 'li r0,1 / li r0,0' shape). Mwcc CSE'd the constant 1 across the bit-stores and kind switch because they straddle a function call.
- **Tried:** Followed sibling ftCo_800B00F8 (matched) source style verbatim with adjusted bit values (b3=true, b6=false, b7=true) and ftCo_800A5F4C(fp, It_Kind_L_Gun_Ray) instead of ftCo_800A61D8; tail uses ftCo_800A53DC inline-assignment-test. Removed PAD_STACK to land stack at 0x48 (matched B00F8 pattern). Tried PAD_STACK(0xC) and PAD_STACK(4) -- both bumped stack to 0x50/0x58.
- **Likely fix:** Permuter for register-allocation shuffle. Source-shape change unlikely to help: structure already matches sibling matched function ftCo_800B00F8 verbatim. May need source that hoists 'int var_r28 = 1' explicitly so mwcc CSEs constant 1 between bit stores and kind switch -- though semantic equivalence is tricky given !ftCo_800A5908 idiom doesn't naturally produce the 'b L_END / mr r28,r29' shape.

