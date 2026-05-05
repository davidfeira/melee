---
function: grMuteCity_801F290C
tu: src/melee/gr/grmutecity.c
headline: stack-offset + regalloc
tags: [stack-offset, regalloc]
---
## grMuteCity_801F290C (`src/melee/gr/grmutecity.c`) — stack-offset + regalloc

- **Tags:** `stack-offset`, `regalloc`
- **Best fuzzy:** 99.2952%
- **Diagnosis:** 16 mismatches at baseline PAD_STACK(16). Two issues: (1) stack offsets for two locals differ by exactly 16 bytes (target=0x34/0x30 base=0x24/0x20) while frame size matches at 0x50 -- suggests target has an additional 16-byte local placed at lower offset, possibly a temporary GXColor[4] or Vec4 buffer that gets reused vs the C source accessing gp->gv.mutecity2.saved_colors[i] directly. (2) r27/r28 are swapped in the else-branch loop (i counter vs lobj pointer).
- **Tried:** Variant 1: PAD_STACK(32) -> went to 21 mismatches (frame too big). Variant 2: removed PAD_STACK -> 21 mismatches (frame too small). Baseline PAD_STACK(16) gives correct frame size but local offsets still differ.
- **Likely fix:** Try introducing an explicit local GXColor saved_colors[4] (or similar 16-byte local) that is then copied to gp->gv.mutecity2.saved_colors, OR investigate whether HSD_LObjGetColor was originally called with a stack-temporary GXColor* then assigned to the struct member. Also possible: HSD_LObjSetColor takes GXColor by value not pointer and the C source needs &local_color.
