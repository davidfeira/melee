---
function: grHomeRun_8021CB20
tu: src/melee/gr/grhomerun.c
headline: string-pool + header-required
tags: [string-pool, header-required, struct-typing, permuter-queued]
---
## grHomeRun_8021CB20 (`src/melee/gr/grhomerun.c`) — string-pool + header-required

- **Tags:** `string-pool`, `header-required`, `struct-typing`, `permuter-queued`
- **Best fuzzy:** 81.4917%
- **Diagnosis:** Stage init function (726 instructions). Match plateaus at ~81% with 425 mismatches dominated by structural data-layout issues.
- **Tried:** Structurally correct decomp using HSD_JObjSet/Get inlines, HSD_ASSERT macros, and (u8*)gp + offset casts for fields beyond declared grHomeRun_GroundVars. Tried both alloc-then-assert vs assert-on-stored-value patterns; ~80% either way.
- **Likely fix:** Two structural blockers: (1) Target embeds all assert string literals ('grhomerun.c', 'gp->u.map.parts', 'gp->u.map.back', 'SIS_GrHomerunData', 'INIT_ADD_PARTS_RANGE*2<Gr_Homerun_Parts_Max', 'gp->u.map.parts[i]', 'gp->u.map.bg_gobj[0..3]') CONTIGUOUS with grHr_803E8140 array — single addi r30,grHr_803E8140@l drives all assert string args at +0x134..+0x25C. Need to define a packed StageData blob (similar to grHeal_803E851C) that places StageData struct + all literal strings inline. (2) Map_GroundVars in src/melee/gr/types.h needs 'parts' (HSD_GObj** at xC4), 'back' (HSD_GObj** at xC8?), and 'bg_gobj[4]' (HSD_GObj* array at xD8) fields so asserts get the right text. Also: stack frame uses one fewer save reg (target stmw r24, base stmw r23) — likely needs different local-var count. Function size (726 ins) past permuter scale; 425 mismatches and string-pooling cascade make this manual-only territory. Header changes to types.h required.

