---
function: ftCo_800B8A9C
tu: src/melee/ft/ftcpuattack.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, permuter-territory]
---
## ftCo_800B8A9C (`src/melee/ft/ftcpuattack.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `permuter-territory`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Target uses stmw r27 (5 saved regs, frame -0x90) but base generates only 4 saved regs (stw r28-r31, frame -0x50). All 165 mismatches are downstream register-number shifts (r28->r29, r29->r30, r30->r31) plus missing addi precomputed-address instructions (addi r31,r28,0x1acc; addi r5,r28,0x1b74) that MWCC emits as scheduling artifacts when r31 holds &cpu->x44 base. Structural shape is correct: bitfield guards, motion_id range check, item weapon switch, edge-guard floor check, 5 attack table lookups. Both attempts reached 84-85% — the gap is entirely regalloc and scheduling.
- **Tried:** Attempt 1: naive function-scope locals. Attempt 2: scoped target2/target3 blocks to extend item/target lifetime hoping to force 5th saved reg; did not change register count.
- **Likely fix:** Permuter: introduce a dummy variable that extends lifetime of one local across the function body (e.g. assign item early and use it late), forcing MWCC to allocate r27. Alternatively try making weapon_reach a saved-reg candidate by using it after a function call boundary.

