---
function: ftKb_SpecialN_800F10D4
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + paired-siblings
tags: [regalloc, paired-siblings, upstream-regression, header-prototype]
---
## ftKb_SpecialN_800F10D4 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + paired-siblings

- **Tags:** `regalloc`, `paired-siblings`, `upstream-regression`, `header-prototype`
- **Best fuzzy:** 81.2037%
- **Diagnosis:** Function matches 100% upstream at 76cae8504 but regressed when 800EF438 was implemented in same TU (commit aa287de8d). Root cause: 800EF438's return type changed from UNK_RET (stub, header-only) to void (in-TU definition visible). With void definition visible at the 800F10D4 call site, the compiler reduces register pressure after the 800EF438 call, causing it to allocate 5 saved registers (stmw r27-r31) instead of 4 (individual stw r28-r31), adding an extra fp copy in r29. Sibling functions without the final ftCo_8009D81C(fp) call match fine regardless.
- **Tried:** (1) fp = gobj->user_data (no double-assign): same 5-reg pattern, 23 mismatches. (2) Reverted header 800EF438 to UNK_RET: no effect because in-TU void definition overrides header declaration for MWCC. Both attempts at 81.2% or worse.
- **Likely fix:** Move the void ftKb_SpecialN_800EF438 definition to after line 4450 (after all its callers: 800F0FC0 at 4270, 800F10D4 at 4301, 800F11F0 at 4335, 800F130C at 4371, 800F14B4 at 4434). With definition after callers, MWCC sees only the UNK_RET header declaration at all call sites, restoring original register pressure. Sibling 800F11F0 has identical issue and same fix. Re-verify 800F0FC0, 800F130C, 800F14B4 still match after move.

