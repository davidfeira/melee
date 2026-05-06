---
function: lbColl_8000A78C
tu: src/melee/lb/lbcollision.c
headline: stack-offset + permuter-territory
tags: [stack-offset, permuter-territory, paired-siblings, string-pool, permuter-queued]
---
## lbColl_8000A78C (`src/melee/lb/lbcollision.c`) — stack-offset + permuter-territory

- **Tags:** `stack-offset`, `permuter-territory`, `paired-siblings`, `string-pool`, `permuter-queued`
- **Best fuzzy:** 99.8362%
- **Diagnosis:** At 99.83% fuzzy match (99.66%/20 instr at .o-level diff). Sibling functions in same TU (lbColl_8000A584/8000A95C/8000AB2C) all exhibit identical mismatch class at 99.5-99.86% fuzzy. Mismatches are stack-offset shifts: target places sp24/sp30 Vec3 locals at low addrs (0x24/0x30) and outgoing-arg Vec3 copies at 0x6c-0x80 between Mtx sp3C(0x3c) and sp84/sp90; mwcc on my source places locals at 0x6c/0x78 and arg copies at 0x24-0x38 instead. Plus systematic @790/@791 vs lbColl_804D3700/3708 string-pool symbol naming difference (literal 'jobj.h'/'jobj' from HSD_ASSERT in HSD_JObjGetMtxPtr inline).
- **Tried:** (1) Wrote function mirroring 8000A95C exactly — same TU sibling that's labeled 'matched' but actually 99.66% (.o-level). Got 99.66%/23 instr. (2) Reordered locals to match 8000AB2C (Vec3s before Mtx sp3C) — 99.69%/20 instr, slightly better but still off. Both attempts cleanly compile and produce same systematic offset shifts as siblings.
- **Likely fix:** Permuter can shuffle local declaration order to coax mwcc stack layout. But all sibling functions in same TU share this exact issue — a TU-wide compiler flag or rodata/string-pool ordering fix could resolve all four at once. The string-pool symbol naming (@NNN vs lbColl_804D3700) requires either dtk symbol-mapping or explicit string-literal-as-static. NOTE: decomp-permuter is currently offline per session override; queued for later dispatch.

