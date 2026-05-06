---
function: mnStageSw_80236548
tu: src/melee/mn/mnstagesw.c
headline: permuter-queued + r30-r31-swap
tags: [permuter-queued, r30-r31-swap, float-regalloc, instruction-scheduling, stack-offset]
---
## mnStageSw_80236548 (`src/melee/mn/mnstagesw.c`) — permuter-queued + r30-r31-swap

- **Tags:** `permuter-queued`, `r30-r31-swap`, `float-regalloc`, `instruction-scheduling`, `stack-offset`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 97.6% match, 61 mismatches. Source structure semantically correct (mirrors mnStageSw_80236178 inlined plus arg1/arg2 dispatch and final mn_8022ED6C call). Remaining diff is pure register allocation: target r30=inner / r31=highlight, base swaps to r31=inner / r30=highlight; target f30=frame / f31=delta, base swaps. Knock-on effect: stack frame 0xa0 vs target 0x80, sp44 at 0x40 vs 0x44 (different spill placement). One instruction-schedule miss around 'mr r3, inner' position before 'lbz r4, 0x1(inner)'. 802364A0 noinline pragma added so calls aren't inlined.
- **Tried:** (1) initial draft using HSD_GObj cast for inner with field accesses (user_data, user_data_remove_func, x34_unk) inline-evaluated 802364A0 (44%); (2) added #pragma dont_inline on/reset around mnStageSw_802364A0 to force non-inline (95.9%); (3) byte +1 access via ((u8*)inner)[1] instead of (u8)inner->classifier to match lbz vs lhz pattern (97.6%); (4) inlined tmp HSD_JObj* and merged ref_lo/ref_hi/new_y locals (97.6%, no further help).
- **Likely fix:** Permuter on register allocation. Likely needs reordering of local declarations or call sites to flip which variable gets r30 vs r31 first. Could also try declaring frame/delta as separate scopes or splitting the if (arg1) block.

