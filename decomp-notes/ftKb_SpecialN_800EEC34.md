---
function: ftKb_SpecialN_800EEC34
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: data-anchor + permuter-false-positive
tags: [data-anchor, permuter-false-positive, regalloc, frame-size]
---
## ftKb_SpecialN_800EEC34 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — data-anchor + permuter-false-positive

- **Tags:** `data-anchor`, `permuter-false-positive`, `regalloc`, `frame-size`
- **Best fuzzy:** 86.6479%
- **Diagnosis:** At 86.37%, structure correct (lbDvd_800178E8 calls + costume loop + efAsync_LoadAsync match target). Base caches the .data.0 section anchor in r29 to share across 3 globals (ftKb_Init_803CA9D0, ftKb_Init_803CB3E8, ftKb_Init_803CB46C); target uses 3 separate lis/addi pairs and never caches. Anchor cache forces saving r25 (stmw r25 vs target stmw r26) -- shifts entire register window by 1 (r25/r26 swap, r26/r27 swap, etc). Frame -0x40 vs -0x38.
- **Tried:** (1) baseline ftdata_800855C8-shaped C with int args and arg2 reused as hi; (2) intermediate locals for filename/costumes_slot -- regressed to 81.7% (added mr r4,r0). Header prototype is (int,int,int) so s32 redeclares as long.
- **Likely fix:** Permuter could explore regalloc shifts to drop the anchor cache, but the core lis-vs-anchor diff is post-link equivalent -- report.json fuzzy will not see it as a match (data-anchor false-positive class).

