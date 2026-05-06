---
function: ftKb_EatWait_IASA
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-queued + sda21-float-collision
tags: [permuter-queued, sda21-float-collision, r30-r31-swap, frame-size]
---
## ftKb_EatWait_IASA (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-queued + sda21-float-collision

- **Tags:** `permuter-queued`, `sda21-float-collision`, `r30-r31-swap`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Reached 91.72% from placeholder with semantic shape correct (4 motion-state branches: drink/spit gated by xF4_b0, then turn/jump/walk fall-through). Remaining 130 mismatches dominated by: (1) sda21 float pool collision — target uses ftKb_Init_804D93B0/C0/C4@sda21 for 0.0f/1.0f/-1.0f literals while my version generates fresh @193@sda21/@221@sda21 (linker-equivalent post-link, false-positive); (2) r30/r31 register swap — target allocates r30=gobj, r31=fp_first_half, r29=fp_walk_section; mine swaps r31=gobj, r29=fp; (3) frame size still 0xc0 vs target 0xa8 (PAD_STACK(0x70) overshoots by 0x18).
- **Tried:** Two manual source-shape attempts. (1) Initial implementation from m2c with single fp local — 91.49%. Fixed: x2222_b5 wrong (m2c misled with mask 0x20 = MSB-bit 2, not bit 5); fp->dat_attrs needs ftKb_DatAttrs cast. (2) Added PAD_STACK(0x70) — frame ended at 0xc0 (overshoot 0x18) — 91.72%, no register-allocation improvement.
- **Likely fix:** Permuter territory: register allocation + sda21 float ordering. Source shape appears semantically correct. Float pool collisions ARE permuter false-positive class (ftKb_Init_804D93xx are local-TU linker symbols equivalent to @N@sda21 post-link). If permuter rejects: structural frame-size investigation needed — possibly inline struct copy or hoisted dat_attrs aliasing pattern. Try declaring two distinct Fighter* locals (fp1, fp2) with non-overlapping live ranges to force r29 vs r31 split.

