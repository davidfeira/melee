---
function: un_80311AB0_OnEnter
tu: src/melee/ty/toy.c
headline: string-pool + data-symbols-missing
tags: [string-pool, data-symbols-missing, frame-size, regalloc, permuter-blocked]
---
## un_80311AB0_OnEnter (`src/melee/ty/toy.c`) — string-pool + data-symbols-missing

- **Tags:** `string-pool`, `data-symbols-missing`, `frame-size`, `regalloc`, `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Reached 99.4% (22 mismatches). Three remaining blockers: (1) string-pool: target's .data section has the literal strings 'ScToyLightMaster0_scene_lights' / fog / etc placed adjacent to un_803FDD18 such that asm references them as r30+0xAF0, +0xAFC, +0xB08, +0xB18, +0xB28, +0xB34, +0xB44, +0xB54 — base lacks these strings entirely so 8 addi instructions flag DIFF_ARG_MISMATCH (instruction bytes match, relocation differs). (2) frame-size: target frame is 0x58 but base only generates 0x30 — need ~40 more bytes of locals that survived inlining of the 4-pad polling helper. Tried PAD_STACK(4) inside static inline OnEnter_pollPads — mwcc collapses stack slots when inlined 4x. (3) regalloc on the 0x3E8/0x3EC trophyCount comparison block (4 instructions, lha-to-r3 vs lha-to-r0 + cmpw operand swap) — likely permuter territory but cannot dispatch (cluster offline).
- **Tried:** (a) Loop bodies as 4 unrolled inline copies vs single static inline helper -- inline helper produces same shape but slightly different stack. (b) Switched if-else to goto-style for the un_804A26B8[0x1F4] >= 0 branch (saved 4 instructions). (c) Variable declaration order to get r30=fname/r31=toy correct. (d) Use of UNK_T for arg0 to match toy.h prototype.
- **Likely fix:** Add the missing string literals (ScToyLightMaster{0,1,2,3,4,5,6}_scene_lights and corresponding _fog names) as static char arrays in toy.c at the position immediately after un_803FDD18 so the linker places them at the expected offsets. The byte layout from the .data diff shows: 'TyLight.dat\0ScToyLightMaster0_scene_lights\0\0ScToyLightMaster1_scene_lights\0...' through 6 entries. This will fix the addi r30+offset relocations AND likely fix the frame-size delta since adding more static data may shift mwcc's inline-frame allocation. Remaining ~4 trophy-block regalloc mismatches need permuter once cluster is online.

