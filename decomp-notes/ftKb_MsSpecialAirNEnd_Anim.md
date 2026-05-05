---
function: ftKb_MsSpecialAirNEnd_Anim
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive, float-literal]
---
## ftKb_MsSpecialAirNEnd_Anim (`src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`, `float-literal`
- **Best fuzzy:** 98.871%
- **Diagnosis:** Diff is 14 register-allocation mismatches (target: r26=gobj, r27=fp, r28=iter, r25=lis_0x4330; base: r27=gobj, r31=fp, r28=iter, r26=lis_0x4330) plus 1 sdata2 float-literal mismatch (target: 'lfd f31, ftKb_Init_804D9578@sda21' for the int->f32 conversion magic double 0x4330000080000000; base: '@623@sda21'). Function structure is correct - same instructions in same order, only register names differ. The double constant ftKb_Init_804D9578 lives at 0x804D9578 within ftKb_SpecialNYs.c's own sdata2 split (0x804D9554..0x804D95B0) but is named with an 'ftKb_Init_' prefix in symbols.txt.
- **Tried:** Variant 1: replaced 'iter = fp; iter = (Fighter*)((u8*)iter + sizeof(HitCapsule))' pattern with for-loop 'fp->x914[i]' indexing. Mismatches went from 15 to 25 (regressed). Reverted.
- **Likely fix:** Pure-regalloc portion is permuter territory, but the float-literal false-positive will block 100% in report.json fuzzy. Need to (a) dispatch permuter to find regalloc fix AND (b) introduce a named 'extern double ftKb_Init_804D9578' reference in source so the int->f32 magic constant emits with the named symbol instead of compiler-generated @623@sda21. Possibly via an explicit cast helper or an unused static initializer that forces the named double into the literal pool. Same 'magic 0x4330_00008000_0000 int->float bias' false-positive likely affects sibling Kirby Fighters with similar (s32)->(f32) idioms.
