---
function: ftCo_800ADE48
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: inlining + frame-size
tags: [inlining, frame-size, regalloc, permuter-resistant]
---
## ftCo_800ADE48 (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — inlining + frame-size

- **Tags:** `inlining`, `frame-size`, `regalloc`, `permuter-resistant`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 601-instr CPU AI dispatch function with deeply nested if/else chain (16+ states checked sequentially). Initial source-shape attempt produces 61% match with 455 mismatches. Primary structural blockers: (1) mwcc inlines ftCo_800A1B38 wrapper at this call site in my source but does NOT inline at the target (other matched call sites at line 442, 1170 also do not inline, suggesting mwcc inline-budget heuristic fires differently here). (2) Stack frame size (target 0x90, base 0x78) and saved-register choice (target stmw r27, base stmw r25) differ — driven by different live-range analysis through the nested branches. (3) f30/f31 register usage in bounds-check block differs because target keeps Vec2 components in fp regs across blast-zone calls while my version uses fresh locals.
- **Tried:** Wrote initial source from m2c reconstruction matching all bitfield positions (xF8_b5, xF8_b12, xF8_b34, xF9_b0, xFA_b1, xFA_b2, x221A_b3, x221B_b5), 5.0 vs 5.0f literal distinction for first mpCheckFloor, sqrtf-via-Newton-Raphson, uninitialized-do_state_12 pattern matching mwcc's r31 read-before-write in the level-Randf branch. Verified all field offsets and mpCheckFloor argument positions against existing matched calls in the same TU. Result: 61% match.
- **Likely fix:** Need to (a) prevent mwcc from inlining ftCo_800A1B38 at this site — possibly by reordering local variable declarations to push the inline budget over before reaching the call, or by a wrapper variable trick; (b) restructure the bounds-check block to keep data->x54.x and data->x54.y live in f30/f31 across the four Stage_GetBlastZone* calls (avoid intermediate cx/cy locals); (c) potentially move ftCo_800ADE48 BEFORE ftCo_800A1B38 in the source file so mwcc only has the prototype at the call site (cannot inline). Permuter not viable: 455 mismatches dominated by structural decisions, not register/scheduling noise. Recommend manual second pass focused on inlining-budget control + f30/f31 live-range.

