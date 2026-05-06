---
function: ftKb_SpecialNYs_8010AC78
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c
headline: permuter-plateau + frame-size
tags: [permuter-plateau, frame-size, sdata2-named, data-anchor, sdata2-named-floats, inlining]
---
## ftKb_SpecialNYs_8010AC78 (`src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c`) — permuter-plateau + frame-size

- **Tags:** `permuter-plateau`, `frame-size`, `sdata2-named`, `data-anchor`, `sdata2-named-floats`, `inlining`
- **Best fuzzy:** 85.776%
- **Diagnosis:** Translation written from sibling ftCo_800BBED4 in ftCo_YoshiEgg.c. Match plateaus at 85.5% (79 mismatches). Three issues remain: (1) Frame size 0xb8 vs target 0x78 (~0x40 byte unexplained reservation persists even after dont_inline pragma on helper ftKb_SpecialNYs_801093A0); locals layout (Vec3 scale + ftHurtboxInit hurt) takes 0x34 bytes which fits target's 0x78 frame fine but base reserves an extra 0x40. (2) ~24 mismatches are sdata2-named-floats / data-anchor false-positives (lfs f1, ftKb_Init_804D9568@sda21 vs @207@sda21 for 0.0f literal; ftKb_Init_804D3DE8 string-pool symbol vs anchor names @505/@506 for HSD_ASSERT __FILE__/__FUNCTION__ strings emitted by inlined HSD_JObjSetScale/HSD_JObjGetScale/HSD_JObjMtxIsDirty asserts at lines 0x2F8/0x234/0x337/0x338). (3) Target has dead mr r3, r29 before bl ftKb_SpecialNYs_801093A0 (which takes void) - implies original source called helper with gobj as arg even though signature is void; comma operator (gobj, helper()) trick untried.
- **Tried:** Wrote function from sibling ftCo_800BBED4 template. Added forward decl for static fn_8010AA64. Cast ftKb_SpecialNYs_801093A0() return to HSD_Joint*. Tried #pragma dont_inline on around our function (regressed to 59% - blocked HSD_JObjSetScale inline that target wants). Removed pragma. Wrapped helper ftKb_SpecialNYs_801093A0 in dont_inline (gained 3pts to 77.4%). Restructured to inline hurtbox setup (not in nested block), moved mv.co.yoshiegg.scale=scale assignment AFTER lb_8000C2F8 (gained 8pts to 85.5%). Tried Vec3 scale before/after hurt declaration (no change in match%, just shifted stack offsets uniformly).
- **Likely fix:** The +0x40 frame mystery + dead mr r3,r29 both point to original source possibly calling ftKb_SpecialNYs_801093A0(gobj) (passing gobj despite void signature), or possibly some intermediate helper variable spilled to stack. Need permuter to explore arg-list / temp-var permutations. The 24 sda21/anchor false-positives won't ever match in fuzzy report.json but might match on linker pass.

