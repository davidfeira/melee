---
function: ftCo_800B4AB0
tu: src/melee/ft/ftcpuattack.c
headline: permuter-blocked + struct-typing
tags: [permuter-blocked, struct-typing, inlining, float-regalloc]
---
## ftCo_800B4AB0 (`src/melee/ft/ftcpuattack.c`) — permuter-blocked + struct-typing

- **Tags:** `permuter-blocked`, `struct-typing`, `inlining`, `float-regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Large 511-instr CPU AI attack-selection function at 0% match with no source skeleton (currently '/// #ftCo_800B4AB0' stub). Performs two parallel 3-iteration Newton-Raphson sqrtf expansions (via frsqrte) for projectile trajectory math on X and Y axes, walks an arg2 array of 0x24-byte AttackEntry structs filtering candidates by hitbox/range against fp+0x1A88 substruct and arg1 fighter, copies up to ~15 candidates into a 0x4F0-ish stack array (sp3C+), HSD_Randf-weighted select via sum/accumulate over .unk18 weights, and writes 4 floats to temp_r31->unk6C..78 scaled by fp->unk38. Touches many unnamed Fighter fields (unkB0/B4/C8/CC/16C/170/1AF4..1B00/1FE4/1FE8/1FF0/1FF8) and fp->x1A88 substruct (unk10, unkEC, unk80, unkA8, unkC8) — a lot of correct typing+inline work needed before any permuter pass can help.
- **Tried:** No source attempt made; m2c output reviewed. Confirmed: cror eq,lt,eq and cror eq,gt,eq patterns (MWCC <= and >= with negative-zero handling), 3-iter sqrtf NR expansion shape standard for math.h sqrtf inline used elsewhere in TU (see ftCo_0A01.c). Fighter struct fields not yet named for this region; AttackEntry only has cmd/weight defined (need ~7 more f32 fields at +0x4/8/C/10/14/1C and 0x20).
- **Likely fix:** Define remaining ftCo_AttackEntry fields (probably: s32 cmd, f32 t, f32 vx, f32 vy, f32 minX, f32 maxX, f32 weight, s32 mod, s32 flags or similar at the right offsets), name relevant Fighter fields in that region, write skeleton using sqrtf() (math.h inline) for the projectile reach math. Then dispatch to permuter for register/scheduling cleanup. Sibling ftCo_800BB220 in same TU is already 77% — its struct usage may guide naming.

