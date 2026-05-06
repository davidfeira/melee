---
function: HSD_SObjLib_803A477C
tu: src/sysdolphin/baselib/sobjlib.c
headline: permuter-plateau
tags: [permuter-plateau]
---
## HSD_SObjLib_803A477C (`src/sysdolphin/baselib/sobjlib.c`) — permuter-plateau

- **Tags:** `permuter-plateau`
- **Best fuzzy:** 75.5359%
- **Diagnosis:** 77.8% match with semantically-correct decomp. Structural shape correct (HSD_ObjAlloc, GXInitTlut/TexObj/TexObjCI calls, all field stores, GXGetTexObj{Width,Height} + 1.0/x divisions, HSD_SObjLib_803A44D4 tail). Three persistent register-allocation diffs that flip throughout: target uses {r31=image, r30=back_image, r29=sobj}, base uses {r30=image, r29=back_image, r31=sobj}. Target reserves stwu -0x78 with stfd f31,0x70 to save inverse-width across the GXGetTexObjHeight call; base picks 0x70 frame and avoids f31 save (different scheduling around the divide). Also assert string lis pooled as @92 vs HSD_SObjLib_8040C3B0 in target. Tried two source-shape attempts (intermediate-cast removal, hoisting image= load into both branches of the flag if/else). Permuter territory: reg alloc rotation + small constant placement + division/call scheduling. Source kept (improvement from 0% to 77%). Note: decomp-permuter is offline so cannot dispatch.

