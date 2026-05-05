---
function: ftPp_SpecialAirHiStart_0_Anim
tu: src/melee/ft/chara/ftPopo/ftPp_SpecialS.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## ftPp_SpecialAirHiStart_0_Anim (`src/melee/ft/chara/ftPopo/ftPp_SpecialS.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 95.5758%
- **Diagnosis:** At 95.57% with 17 mismatches; mostly regalloc shuffling (target uses r28/r29/r30/r31 differently than base across the nana-range check). One real mismatch around fp2->cur_pos load: target emits 'lfsu f2,0xb0(r3)' + 'lfs f0,0x4(r3)' (load with update on r3, then read y via +4 offset), while base emits 'lfs f2,0xb0(r3)' + 'lfs f0,0xb4(r3)' (two independent loads from r3). Permuter cluster ran to score=250 plateau (output-250-1 hoists nana_gobj decl and uses 'int new_var=0' constant). Tested manually: dropped 17->14 mismatches but didn't reach 0; remaining diff still has the lfsu codegen and extensive regalloc churn.
- **Tried:** Variant 1: hoist Fighter_GObj* nana_gobj and 'int new_var = 0' to outer scope per permuter output-250-1. Result 95.88% / 14 mismatches (small regalloc win but lfsu issue and most reg shuffles persist). Reverted.
- **Likely fix:** May need a different fp2 cur_pos access pattern that forces base ordering (separate temps for fp2_x, fp2_y before computing dx/dy), or accept that this requires deeper permuter exploration of the SQ() macro evaluation order. Consider moving 'int found' decl outside the if-block to free up register pressure.
