---
function: ftKb_SpecialN_800EED50
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: permuter-territory + data-anchor
tags: [permuter-territory, data-anchor, regalloc]
---
## ftKb_SpecialN_800EED50 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — permuter-territory + data-anchor

- **Tags:** `permuter-territory`, `data-anchor`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 76.3% match (40 mismatches). Source structure mirrors matched ftData_80085820. Mine consolidates four nearby globals (ftKb_Init_803CA9D0, ft_80459B88, ftKb_Init_803CB3E8, ftKb_Init_803C9FC8, ftKb_Init_803CB46C) into a shared data.0 base register (r29) with large offsets, plus saves an extra r28; target recomputes each lis/addi independently. Pure register-allocation / data-base-consolidation difference. Added lb/lbarchive.h include to fix missing crclr cr1eq varargs sentinel (jumped 72.5% to 76.3%). Permuter queued (auto-permute disabled per session override).

