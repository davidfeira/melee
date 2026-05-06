---
function: ftKb_SpecialN_800EF0E4
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc, mwcc-const-fold]
---
## ftKb_SpecialN_800EF0E4 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`, `mwcc-const-fold`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 94.46% match, 57 mismatches. Source structurally correct (modeled on ftmetal ft_800C85B8 + sibling ftKb_SpecialN_800EF438). Remaining diffs are all regalloc/scheduling: arg2 saved-copy register choice (r26 vs r24), part_off register (r24 vs r25), and target keeps 'slwi r24, r28, 4' / 'slwi r30, r28, 2' instructions for 'part_off = total_dobjs << 4' and 'byte_off = total_dobjs << 2' that MWCC constant-folds in our base (since total_dobjs=0). Also missing 'addi r25, r26, 0x0' arg2 cursor init from a saved arg2 copy.
- **Tried:** Modeled on ftmetal pattern. Used named asserts via ftKb_Init_assert_msg_0/1/2 and ftKb_Init_804D3DAC. Added PAD_STACK(8) at end (fixed frame size). Reduced local count to match 11 saved registers. Tried multiple variable orderings; could not coax MWCC into preserving the slwi-from-zero pattern that target retains.
- **Likely fix:** Permuter to shuffle regalloc. Possibly a different expression form for part_off/byte_off init that MWCC doesn't constant-fold (e.g., expressing through a non-zero-known temp), but unclear what unfolds into 'slwi r24, r28, 4' when total_dobjs is 0. Sibling ftKb_SpecialN_800EF438 still in flight by another agent; matching it first may reveal the canonical idiom.

