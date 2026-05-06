---
function: ftKb_SpecialN_800F11F0
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + paired-siblings
tags: [regalloc, paired-siblings, upstream-regression, permuter-resistant]
---
## ftKb_SpecialN_800F11F0 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + paired-siblings

- **Tags:** `regalloc`, `paired-siblings`, `upstream-regression`, `permuter-resistant`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Stuck at 81.2% (21 mismatches), reproducing prior note's diff exactly. Source matches 0F10D4 sibling shape (fp = fp = gobj->user_data, hat.x14.data NULL check, ftCo_8009DB50(fp) trailing call). Base compiles to 4 saved regs (r28-r31, individual stw/lwz, no early r29 copy). Target uses stmw r27 with 5 saved regs and a hoisted 'addi r29, r30, 0x0' before the if-check, dedicating r29 to fp solely for the trailing ftCo_8009DB50(fp) call. Sibling 0F10D4 (same shape, calls ftCo_8009D81C(fp)) was 100% at 76cae8504 but is also 81% currently — family-wide regression introduced between 76cae8504 and HEAD.
- **Tried:** (1) standard 'Fighter* fp = fp = gobj->user_data' template matching sibling 0F10D4 — 81.2% same diff. (2) Split into 'fp = gobj->user_data; fp2 = fp;' with ftCo_8009DB50(fp2) — optimizer collapses fp2 into fp, identical 81.2% diff.
- **Likely fix:** Bisect 76cae8504..HEAD for any change to ft headers (Fighter struct layout, KirbyHatStruct, ftKb types.h, ftCo prototypes) that altered register pressure on this 'load-hat then call ftCo_8009DXxx(fp)' pattern. Re-match sibling 0F10D4 first as canary — same source fix should restore 0F11F0 simultaneously. Permuter-resistant: register-pressure delta requires a struct/header source change, not regalloc shuffling. Do not permute in isolation.

