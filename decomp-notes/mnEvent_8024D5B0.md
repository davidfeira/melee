---
function: mnEvent_8024D5B0
tu: src/melee/mn/mnevent.c
headline: permuter-queued + sdata2-anonymous-floats
tags: [permuter-queued, sdata2-anonymous-floats, regalloc, header-required]
---
## mnEvent_8024D5B0 (`src/melee/mn/mnevent.c`) — permuter-queued + sdata2-anonymous-floats

- **Tags:** `permuter-queued`, `sdata2-anonymous-floats`, `regalloc`, `header-required`
- **Best fuzzy:** 81.3643%
- **Diagnosis:** Brought from 0% to 98.7% (17 fuzzy mismatches). Source structure verified semantically: name_text reset, HSD_SisLib_803A6754 alloc, position/color/font_size init, gmMainLib_8015CF5C(gm_801BEBC0(idx)) value lookup, then 4-way branch on gm_801BEB8C/gmMainLib_8015CEFC for time-format vs %d vs blank. Required header change: mnEvent_8024D5B0 second arg from u8 to s32 (target re-masks idx via clrlwi each call, indicating wider param). PAD_STACK not needed once chars became s32 locals. Used 'u32 val' (not s32) for unsigned mulhwu div-by-60. Remaining diffs: 16 are @N@sda21 anonymous floats / @221 anonymous string for %s:%s %s — fuzzy reloc that resolves at link. 1 real diff: target masks gm_801BEBC0 return with clrlwi r3,r3,24 before passing to gmMainLib_8015CF5C; mwcc optimizes away (u8) cast on u8-returning function.
- **Tried:** (1) Initial m2c-style impl at 80.8% with u8 idx + char locals + s32 val. (2) Switched to int sp10/sp14/sp18 (taking address) for 4-byte stride match. (3) u32 val (not s32) for mulhwu unsigned div. (4) s32 idx (header change) plus (u8) casts at every gm_801BEBC0 call. (5) (u8) cast on gm_801BEB8C result for clrlwi. before zero-test. (6) Tried (s32) cast, temp var, & 0xFF, (int) cast — none coerce mwcc to emit clrlwi on u8-returning func result.
- **Likely fix:** Permuter on regalloc patterns (r27↔r28, r29↔r30, r30↔r31 shifts); the anonymous floats/string become named at link so they're cosmetic. The single real clrlwi diff at offset 1992 may need a different source pattern — possibly assigning gm_801BEBC0 result to s32 local with type that mwcc widens, or different cast chain.

