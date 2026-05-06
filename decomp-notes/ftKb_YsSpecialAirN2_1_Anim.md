---
function: ftKb_YsSpecialAirN2_1_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c
headline: frame-size + stack-offset
tags: [frame-size, stack-offset, permuter-territory]
---
## ftKb_YsSpecialAirN2_1_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c`) — frame-size + stack-offset

- **Tags:** `frame-size`, `stack-offset`, `permuter-territory`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 99.89%/9 mismatches: only stack-frame size differs. Target needs 0xc8 frame; sibling-cloned source produces 0xc0 frame (saved-reg slots all 8 bytes too low: stwu -0xc0 vs target -0xc8; stw r29 0xb4 vs 0xbc, etc). Function body is otherwise byte-identical to ftKb_YsSpecialNCapture2_0_Anim modulo the final ftCo_Fall_Enter vs ft_8008A2BC tail call.
- **Tried:** (1) Cloned ftKb_YsSpecialNCapture2_0_Anim body, swapped tail call to ftCo_Fall_Enter -> 99.89%, frame 0xc0 vs needed 0xc8. (2) Bumped PAD_STACK(8) to PAD_STACK(16) above HSD_JObjAnimAll -> got 0xc8 frame BUT pushed item_attrs from 0x80 to 0x88 (PAD_STACK is below item_attrs in MWCC layout for this function), giving 10 mismatches. (3) Tried adding two UNUSED u32 _pad{0,1}=0 locals before item_attrs to lift it -> still triggered stop criteria as 'unproductive'.
- **Likely fix:** Need 8 extra bytes ABOVE item_attrs (between item_attrs end at 0x80+0x28=0xa8 and saved-reg base at 0xbc; sibling has 0xC there, target needs 0x14). FORCE_PAD_STACK or PAD_STACK appears below item_attrs here. Possible fixes: (a) declare an init'd UNUSED u64 _[1]={0} AFTER item_attrs to coax MWCC to place 8 bytes above; (b) introduce a small stack-spill local that survives across the ftCommon_8007E2F4 call (the extra 8 bytes might be a register-spill slot the target asm uses); (c) permuter to discover the 8-byte phantom local. Worth checking the target asm again for any spilled value vs the sibling — there's likely one extra spill in ftKb_YsSpecialAirN2_1_Anim. Permuter is offline per dispatch override; queue when available.

