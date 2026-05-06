---
function: ftKb_YsSpecialNCapture2_0_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c
headline: permuter-territory + frame-size
tags: [permuter-territory, frame-size, stack-offset]
---
## ftKb_YsSpecialNCapture2_0_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c`) — permuter-territory + frame-size

- **Tags:** `permuter-territory`, `frame-size`, `stack-offset`
- **Best fuzzy:** 99.8977%
- **Diagnosis:** Manual pass landed at 99.90% (4 of 88 instr off). Source semantics 100% correct: walks fp->fv.kb.hat.jobj for HSD_JObjAnimAll, mirrors ftCommon_8007E2F4 + lb_8000B1CC + struct fill + it_802F2F34 from the matched ftYs_SpecialN.c counterpart. Only diff is stack frame size: target wants stwu -0xC8 with item_attrs at sp+0x80 and saved regs r29/r30/r31 at 0xBC/0xC0/0xC4; FORCE_PAD_STACK(0x4C) gets struct correctly to sp+0x80 but frame stays at 0xC0 (regs at 0xB4/B8/BC) — there's an 8-byte alignment slack between struct end (0xAC) and saved regs that manual padding doesn't open up. Tried adding FORCE_PAD_STACK_8/PAD_STACK(16) after struct, after FORCE_PAD: each shifts struct off 0x80 instead of growing trailing slack. Dat_attrs accesses use repeated GET_FIGHTER(gobj)->dat_attrs reload pattern (matches asm). vel.z uses extern f32 ftKb_Init_804D9558 (sda21 named float). Pure regalloc/frame-layout territory; permuter queued (decomp-permuter offline this session).

