---
function: gm_801BAC9C
tu: src/melee/gm/gm_1BA8.c
headline: permuter-blocked
tags: [permuter-blocked]
---
## gm_801BAC9C (`src/melee/gm/gm_1BA8.c`) — permuter-blocked

- **Tags:** `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 96.57%, 18 mismatches. Logic is structurally correct: picks random unused CharacterKind from gm_804D6900[idx]->x4 byte list (sentinel 0x21), excluding chars already assigned to first 'count' players' c_kind (offset 0x60 in StartMeleeData with stride 0x24). Remaining diffs: (1) register-allocation choices for 'found' (target r11 vs base r10), 'i' (target r9 vs base r11), 'matches' (target r10 vs base r12); (2) cmpwi vs cmplwi for outer 0x21 sentinel test; (3) buf stack offset target=r1+0x18 vs base=r1+0x20 — possibly extra padding/temp local in original. All classic permuter cases (reg-alloc, signed/unsigned cmpwi, stack layout). NOTE: also touched src/melee/gm/gm_1BA8.h to change UNK_RET gm_801BAC9C(UNK_PARAMS) -> u8 gm_801BAC9C(MinorScene*, int). decomp-permuter offline so cannot auto-permute.

