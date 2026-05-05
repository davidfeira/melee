---
function: grPura_80212FC0
tu: src/melee/gr/grpura.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive]
---
## grPura_80212FC0 (`src/melee/gr/grpura.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`
- **Best fuzzy:** 94.2857%
- **Diagnosis:** 2 instr off (94.29%): base emits 'addi r0, r3, grPu_803E6C0C@l ; mr r31, r0' (extra mov-via-r0) where target emits 'addi r31, r3, grPu_803E6C0C@l' directly. Identical compiler-quirk blocker as sibling grPura_80213030 (also 95.56%, same TU). Both functions iterate grPu_803E6C0C with 'u16* var_r31 = grPu_803E6C0C; u32 var_r30 = 0;' init; mwcc routes the @l add through r0 then mr's to r31, but original goes direct. Sibling notes confirm permuter outputs are scorer-only false positives that regress when ported.
- **Tried:** 1) Standard m2c shape with M2C_FIELD reads (var_r31 += 6, u32 var_r30 = 0) -> 94.29% with the known 2-instr pattern. 2) Swapped decl order (var_r30 first) -> regressed to 90.54% (r30/r31 roles swap).
- **Likely fix:** TU-wide regalloc blocker (see grPura_80213030 notes). Likely needs cluster permuter with creative source-shape (fn inlining, alias-ptr decl) or accept as permuter false-positive territory.
