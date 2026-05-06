---
function: ftKb_SpecialLw1_Coll
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-queued + sdata2-float
tags: [permuter-queued, sdata2-float, frame-size]
---
## ftKb_SpecialLw1_Coll (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-queued + sdata2-float

- **Tags:** `permuter-queued`, `sdata2-float`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Source rewritten from stub to 99.75% match (118 instructions, 13 mismatches). Pattern modeled on matched sibling ftKb_SpecialAirLwEnd_Coll. Used a local struct cast (struct {char pad[0x74]; Vec3 vec;}*) over ftKb_Init_803CB490 to produce the @ha+@l reloc shape lwz r5, 0x74(r31) etc., since ftKb_Init_803CB490 (bool[]) is the closest reloc base for the constant Vec3 at 0x803CB504 (which is also ftKb_Init_803CB4EC.vec). Remaining 13 mismatches are: (a) 8 stack-offset/frame-size diffs (target stwu -0x38 vs base -0x28; needs +0x10 of locals/padding), and (b) 4 sdata2 float reloc symbol diffs (@193@sda21 vs ftKb_Init_804D9390@sda21; permuter false-positive class — post-link bytes are equivalent).
- **Tried:** Attempt 1: Vec3* vec = (Vec3*)((u8*)ftKb_Init_803CB490 + 0x74) — got 93.36%, base reloc folded into local pointer arith (lost &symbol@ha shape). Attempt 2: struct {char pad[0x74]; Vec3 vec;}* p = (...) ftKb_Init_803CB490 — got 99.75%, recovered the asm shape.
- **Likely fix:** Stack frame size: try PAD_STACK(16) or adding a Vec3/float local that gets spilled. Float pool: that's the permuter false-positive class — verify post-link equivalence with --with-fuzzy when sibling TUs build cleanly (currently mnsoundtest.c and grgreens.c are broken-WIP from other agents). May already be 100% under fuzzy.

