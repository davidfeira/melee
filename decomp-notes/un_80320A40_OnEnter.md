---
function: un_80320A40_OnEnter
tu: src/melee/vi/vi1201v2.c
headline: permuter-queued + permuter-territory
tags: [permuter-queued, permuter-territory, regalloc, reloc-symbol-false-positive, sdata2-anonymous-floats, string-pool]
---
## un_80320A40_OnEnter (`src/melee/vi/vi1201v2.c`) — permuter-queued + permuter-territory

- **Tags:** `permuter-queued`, `permuter-territory`, `regalloc`, `reloc-symbol-false-positive`, `sdata2-anonymous-floats`, `string-pool`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 98.77% (66 mismatches, 427 instr). Source structure mirrors matched siblings vi1201v1 (98%) and vi1202 (100%). Stack frame, control flow, and inlined HSD_JObj helpers all match. Remaining diff is dominated by: (a) register-name shifts r28<->r29 throughout (mwcc allocator preference; arg goes to r29 in target vs r28 in base), and (b) data-anchor relocation differences where target uses un_804002F8-anchored offsets for string literals vs base's anonymous @N relocs. The lfs un_804DE124@sda21 vs @152@sda21 mismatch is the sdata2-anonymous-float false positive (post-link bytes equivalent). Sibling vi1201v1 has same residual pattern at 98%, suggesting whole-TU mwcc layout dependency.
- **Tried:** Mirrored vi1202 OnEnter structure exactly (matched at 100%). Added char pad[16] which fixed the stack frame from -0x28 to -0x38 (correct). Used arg[0]/arg[1] direct access vs cached input[0] -- no register-allocation change. Reordered local declarations and tried both u8* arg and void* arg signatures.
- **Likely fix:** Permuter on register allocation -- 66 mismatches exceeds 15-cap but most are pure register-name swaps (r28<->r29 chain). Some mismatches are reloc-symbol false positives that the permuter scorer treats as equivalent. Worth dispatching but heads-up: many diffs may be the sdata2-anonymous-float / data-anchor false-positive class which permuter cannot resolve. May require static linker-table pinning or whole-TU rewrite to drive mwcc into the same register choices.

