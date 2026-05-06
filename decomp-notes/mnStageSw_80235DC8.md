---
function: mnStageSw_80235DC8
tu: src/melee/mn/mnstagesw.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, frame-size, permuter-territory]
---
## mnStageSw_80235DC8 (`src/melee/mn/mnstagesw.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `frame-size`, `permuter-territory`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Source structure matches at 94.39% (29 mismatches). Switch-with-hoisted-constants pattern via 'lo'/'hi' s32 locals reproduces hoisted 'li r28, 0xe; li r27, 0x1c' before loop. Remaining diffs: (1) register-allocation rotation r26<->r27<->r28 in both branch-1 and branch-2 loops, and r0 vs r3 for the (u8)hov clrlwi result; (2) instruction-scheduling: target uses 'add r3, base, r30; lbz r3, 0(r3)' (2 instr) for arr[hov] load while base picks the fused 'lbzx r3, base, r30' (1 instr); (3) frame-size delta of 8 bytes: target stwu -0x28 / stmw r26,0x10 vs base stwu -0x30 / stmw r26,0x18 — same 6-reg save area, base just reserves 8 extra bytes of stack with no apparent live local backing it.
- **Tried:** Attempt 1: chained if/else if (== 0xF, > 0xF default subtract, == 0 wrap) -> 64.38%, mwcc emitted cmplwi+bne instead of cmpwi+beq tree; constants not hoisted. Attempt 2: switch ((s32)hov) {case 0xF: case 0: default: hov-1;} with 'lo'/'hi' s32 locals holding wrap values 0xE/0x1C and 0/0xF -> 94.39%; 's32' compare type matches target's signed cmpwi, hoisted constants now in saved registers. Tried inserting 'u8* p = arr + hov' to coax 'add+lbz' instead of 'lbzx' -> regressed to 79.9% because it broke the loop hoist. Removing 'u16* hov_ptr' local (using struct field directly) had no effect on 94.39% — local was already optimized away. Frame-size delta is independent of the hov_ptr local.
- **Likely fix:** Permuter should clear regalloc rotation and the lbzx-vs-add+lbz scheduling automatically — both are textbook permuter wins. The 8-byte frame-size delta may resolve once an unrelated source perturbation (e.g., declaration order, extra (void) cast on lo/hi to inhibit some optimization, or moving 'arr = mnStageSw_803ED4C4' assignment) shifts mwcc's stack-pad heuristic. If permuter plateaus, suspect an unused stack slot the source must explicitly request — perhaps swap 's32 lo, hi' for a single 's32 wrap[2]' array forcing 8 bytes of stack, or add a u64 buttons-coerced local. Sibling mnStageSw_80235C58 (queued at 94.13%) has the exact same flavor of register-rotation residue.

