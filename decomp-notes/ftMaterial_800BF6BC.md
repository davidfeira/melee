---
function: ftMaterial_800BF6BC
tu: src/melee/ft/ftmaterial.c
headline: frame-size + regalloc
tags: [frame-size, regalloc]
---
## ftMaterial_800BF6BC (`src/melee/ft/ftmaterial.c`) — frame-size + regalloc

- **Tags:** `frame-size`, `regalloc`
- **Best fuzzy:** 99.4726%
- **Diagnosis:** Target frame is 0x188 vs base 0xe8 (160 bytes larger). Source declares unused 'HSD_TExp* sp100' (4 bytes); naming + 0x100 stack offset suggests it should be a struct local consuming ~104 bytes. Changing to 'HSD_TExp sp100' (variant 2) shifts base frame to 0x150, still 0x38 (56 bytes) short of target 0x188 — meaning sp100 is a larger type or there is another unused local. Separate fix (variant 1): swap declaration order of color_hex/fp_color in the inner overlay branch (declare fp_color first); this dropped strict mismatches 75->62 by getting 'addi r4,r27,0x610' before 'addi r5,r3,0x2c'.
- **Tried:** (1) Swapped order of 'GXColor* color_hex' and 'GXColor* fp_color' declarations in inner else-branch — dropped strict mismatches 75->62, fixed addi r4/r5 order. (2) Changed 'HSD_TExp* sp100' to 'HSD_TExp sp100' — frame went from 0xe8 to 0x150 (added 0x68=104 bytes), still 0x38 short of target 0x188.
- **Likely fix:** Apply variant 1 (swap fp_color/color_hex decl order) AND find correct type for sp100. Possibilities: HSD_TExp sp100 PLUS another unused local (~56 bytes — maybe HSD_TExpRes or HSD_TevDesc duplicate), OR sp100 is a different/larger struct (~160 bytes, e.g. HSD_TExpTev variant with extra fields), OR there is an unused HSD_TExpRes local. After both fixes, remaining diff should be regalloc-only (5 mismatches) — permuter territory.
