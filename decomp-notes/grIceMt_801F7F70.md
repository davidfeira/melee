---
function: grIceMt_801F7F70
tu: src/melee/gr/gricemt.c
headline: permuter-queued
tags: [permuter-queued]
---
## grIceMt_801F7F70 (`src/melee/gr/gricemt.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** 86.0331%
- **Diagnosis:** Recovered missing trailing block (rlwimi xC4 flag, grIceMt_801F8CDC, two grIceMt_801FA500+grIceMt_801F91EC pairs with fn_801F9338/fn_801F9448 callbacks), bringing match from 63.06% to 85.62%. Remaining 67 mismatches are pure register-allocation: target saves 4 callee-saves (r28-r31) using individual stw/lwz; base allocates 5 (r27-r31) emitting stmw/lmw and a -0x30 frame vs -0x28. Need workaround for grIceMt_801FA500's wrong 1-arg prototype (its asm impl takes (HSD_GObj*, HSD_JObj*)); I used an inline function-pointer cast at call sites to avoid touching the prototype. Permuter could likely match by trying register-order tweaks; decomp-permuter offline.

