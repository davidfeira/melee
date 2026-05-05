---
function: ftYs_SpecialAirSLoop_2_Coll
tu: src/melee/ft/chara/ftYoshi/ftYs_SpecialS.c
headline: stack-offset + regalloc
tags: [stack-offset, regalloc, paired-siblings]
---
## ftYs_SpecialAirSLoop_2_Coll (`src/melee/ft/chara/ftYoshi/ftYs_SpecialS.c`) — stack-offset + regalloc

- **Tags:** `stack-offset`, `regalloc`, `paired-siblings`
- **Best fuzzy:** 99.8167%
- **Diagnosis:** Frame size 0x98 matches target. 23 real-byte diffs all from uniform stack-offset shift of 0x1C: target places named locals at [0x54..0x70), ours places them at [0x38..0x54). Both 28 bytes used, both 0x98 frame. Pad[28] expands frame correctly but doesn't shift inline-Vec3+f32 locals to higher addresses. 13 additional float-literal diffs are reloc-equivalence false positives (sibling 3_Coll at 100% has same '@1162@sda21' pattern as ours). Real signal: MWCC is packing the inline call locals at LOW frame addresses while target places them HIGH.
- **Tried:** (1) removed pad entirely - frame shrank to 0x80, made worse. (2) tried FORCE_PAD_STACK(28) - identical layout. (3) tried volatile u8 pad[28] - identical. (4) compared with sibling 3_Coll (100% match, no pad, 0x78 frame) and 0_Coll/1_Coll which use same SpawnWallBounceEffect inline pair without pad and match.
- **Likely fix:** May need an early-allocated USED Vec3/scratch local at function top so MWCC reserves its slot at [0x38..0x54) before the inline-call locals get assigned later (higher) offsets. Or insert a real local that the function reads/writes before the if-else inline calls. Permuter searching over local declaration order/volatility/usage would likely find it. NOT a permuter false-positive at the byte level - bytes really differ.
