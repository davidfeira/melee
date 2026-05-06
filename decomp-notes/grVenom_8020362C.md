---
function: grVenom_8020362C
tu: src/melee/gr/grvenom.c
headline: instruction-scheduling + regalloc
tags: [instruction-scheduling, regalloc, bitfield-reuse, permuter-blocked]
---
## grVenom_8020362C (`src/melee/gr/grvenom.c`) — instruction-scheduling + regalloc

- **Tags:** `instruction-scheduling`, `regalloc`, `bitfield-reuse`, `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Function went from 0% (placeholder) to 77.38% match in 2 attempts. Decompiled the full structure: outer switch on grVe_804D6A40, two branches with bit-flag testing of Ground_801C2BA4(7)->user_data->[0xE0] (bits 2-4 OR bits 5-7 grouped, encoding low-2-bits combined dispatch), with HSD_Randi-driven idx selection loops in 4 different shapes. Remaining 156 mismatches are mwcc instruction scheduling interleaving the bit-extraction extrwi sequences across both group-a (bits 2-4) and group-b (bits 5-7) computations, plus register allocation drift (r3/r4/r5 swaps) in the bitfield section, and likely a structural issue in the multi-slot loop init using lwzu (load-with-update). Above 15-instr permuter threshold; permuter offline per orchestrator.
- **Tried:** (1) Initial decomp from m2c+asm at 71.25% with u8 ground_flags (mwcc emitted srawi signed shift). (2) Switched to u32 ground_flags forcing srwi unsigned (72.58%). (3) Restructured bit extraction into separate s32 b4/b3/b2/b7/b6/b5 locals with explicit (x>>n)&1 masking and split if-else for group_a/group_b, achieved extrwi emission at 77.38%.
- **Likely fix:** Need to interleave bit-2-4 and bit-5-7 computation into a single intermixed sequence to match mwcc's scheduling. Also probably need different local ordering for multi-slot loop (lwzu pattern suggests pointer pre-increment). Permuter likely needed for register/scheduling polish above this baseline.

