---
function: grVenom_8020454C
tu: src/melee/gr/grvenom.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory, permuter-queued]
---
## grVenom_8020454C (`src/melee/gr/grvenom.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`, `permuter-queued`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Function structurally complete at 93.41% (109 mismatch). Outer 7-iter loop walking gp->gv.venom2.xC4..xDC and post-loop access of gp->gv.venom.xE4 / xE0_state via union, plus HSD_LObj walk over Ground_801C498C() lights, plus 13 frame-threshold-crossing if-chains. Loop register allocation differs: target uses i=r27, visible=r28, gp(advancing)=r29, gp_save=r31; base uses i=r29, visible=r27, gp=r28, gp_save=r31. Also temp-register pattern in HSD_LObj next-pointer ternary is collapsed by base (target preserves mr r27, r0 separate from lwz). Both are pure regalloc/scheduling differences.
- **Tried:** (1) Wrote initial source from m2c with proper HSD_LObj walk, threshold-crossing if-chains using grVe_804DB7XX@sda21 floats, and union-aliased venom2.xE0_state bitfield (b0..b6) bits matching rlwimi mask analysis. PAD_STACK(8) added to match 0x58 frame. (2) Reordered local declarations and used inline initializers (Ground* gp = ...; Ground* gp_save = gp;) to nudge register allocation; gained slight improvement (93.07->93.41) but loop iterator still allocates to r29 instead of r27. Replaced 0.0f literals with grVe_804DB740/grVe_804DB760 globals to match target's named-symbol usage.
- **Likely fix:** Permuter run on register allocation. The remaining diff is dominated by r27/r28/r29 swaps in the 7-iteration loop body and one extra mr in the HSD_LObj walker — classic permuter cases (regalloc + temp-lifetime collapse).

