---
function: ftKb_SpecialAirLwEnd_Coll
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: data-anchor + permuter-false-positive
tags: [data-anchor, permuter-false-positive, reloc-symbol-false-positive]
---
## ftKb_SpecialAirLwEnd_Coll (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — data-anchor + permuter-false-positive

- **Tags:** `data-anchor`, `permuter-false-positive`, `reloc-symbol-false-positive`
- **Best fuzzy:** 82.4186%
- **Diagnosis:** Body identical to matched ftKb_SpecialHi_800F36DC (same speciallw fan-out + 0x84/x88 zeroing), wrapped with leading ft_80081D0C(gobj) and trailing ftPartSetRotX(fp,0,0). Source compiles to 80.9% / 84 mismatches but the residual is anchor-symbol disagreement: target uses ftKb_Init_803CB490@ha + 0x74/0x78/0x7c (bool[23]+pad indexed past array end) as anchor for ftKb_Init_803CB4EC.vec, while base picks ftKb_Init_803CB4EC@ha + addi 0x18. Both resolve to 0x803CB504 post-link so bytes are identical, but objdiff strict-diff scores them as different reloc symbols. mwcc anchor-pick is likely driven by callee-saved hoist: r31 is loaded with the anchor in prologue to survive bl ft_80081D0C, and the optimizer chose the prior @ha reference symbol.
- **Tried:** (1) Two-Fighter-pointer cache (fp pre-call, fp2 = GET_FIGHTER post-call) plus literal speciallw fan-out copied verbatim from ftKb_SpecialHi_800F36DC. Result: 80.9%/84 mismatches, all DIFF_ARG_MISMATCH centered on r31->r30 anchor swap and base address arithmetic; same instruction count overall. (2) Variant collapsing fp2 reuse (delegate to a helper) abandoned: would emit a bl that doesnt exist in target.
- **Likely fix:** Force compiler to anchor on ftKb_Init_803CB490 instead of ftKb_Init_803CB4EC. Possible source-shape: read a sentinel byte off ftKb_Init_803CB490 inside the function before the speciallw block (e.g. dummy use of the bool[]) so mwcc emits @ha for _803CB490 first, then offsets. Alternative: add a static const pointer alias casting ftKb_Init_803CB490 + 0x74 to Vec3* and use that. Permuter is a no-op here because linked bytes are already equivalent (false-positive class).

