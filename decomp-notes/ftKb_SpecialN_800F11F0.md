---
function: ftKb_SpecialN_800F11F0
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + paired-siblings
tags: [regalloc, paired-siblings]
---
## ftKb_SpecialN_800F11F0 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + paired-siblings

- **Tags:** `regalloc`, `paired-siblings`
- **Best fuzzy:** 81.2037%
- **Diagnosis:** 81% (21 diff) with shape identical to matching siblings 0F0FC0/130C/14B4. Base uses 4 saved regs (r28-r31 individual stw) but target uses stmw r27 (5 saved regs r27-r31, gobj kept in r27, fp in r30, plus 'addi r29, r30, 0x0' early copy for the trailing ftCo_8009DB50(fp) call). The previously-matched sibling ftKb_SpecialN_800F10D4 (which has identical structural shape calling ftCo_8009D81C(fp) at end) is ALSO currently 81% locally, indicating a regression somewhere between 76cae8504 (last 100%) and HEAD.
- **Tried:** standard self-assign 'fp = fp = gobj->user_data' template (same as matched 0F10D4); split fp into fp+fp2 locals (optimizer collapses them, no change).
- **Likely fix:** Family-wide regression on the 'load-hat then call ftCo_8009D[BX]50(fp)' pattern. Header/struct change since 76cae8504 affects register pressure. Bisect commits between 76cae8504..HEAD touching ft headers/types.h to find the introducer. Once 0F10D4 is back to 100%, the same source shape should give 0F11F0 a match. Do NOT permute this in isolation - both functions need the same fix simultaneously.
