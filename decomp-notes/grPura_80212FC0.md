---
function: grPura_80212FC0
tu: src/melee/gr/grpura.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive, permuter-queued]
---
## grPura_80212FC0 (`src/melee/gr/grpura.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`, `permuter-queued`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 2 instr off (94.29%): base emits 'addi r0, r3, grPu_803E6C0C@l ; mr r31, r0' (extra mov-via-r0) where target emits 'addi r31, r3, grPu_803E6C0C@l' directly. Reproduces prior diagnosis exactly. Identical compiler-quirk blocker as sibling grPura_80213030 (matched). Permuter offline -- queued for cluster.
- **Tried:** 1) Standard m2c shape with M2C_FIELD reads (var_r31 = grPu_803E6C0C, var_r30 = 0) -> 94.29% with the known 2-instr regalloc pattern. 2) Same shape with &grPu_803E6C0C[0] init -> identical 94.29% (no change in codegen). Prior session also tried: swapped decl order (var_r30 first) -> regressed to 90.54%.
- **Likely fix:** TU-wide regalloc blocker; needs cluster permuter when online. Sibling grPura_80213030 matched via same source-shape pattern, but FC0's lha early-load may force a different reg allocation order in mwcc. Source improvement (94.29% vs 0% stub) kept in tree.

