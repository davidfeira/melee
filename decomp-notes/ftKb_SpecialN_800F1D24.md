---
function: ftKb_SpecialN_800F1D24
tu: src/melee/ft/chara/ftKirby/ftKb_Init.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## ftKb_SpecialN_800F1D24 (`src/melee/ft/chara/ftKirby/ftKb_Init.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 99.5588%
- **Diagnosis:** 99.55882% strict with only 3 mismatches: x60 countdown temp is allocated to r3 in base but r4 in target (lwz/cmpwi/subi). Control flow, frame, coll_data pointer setup, env_flags checks, and stores otherwise match.
- **Tried:** Pointer-to-field shape consumed r31 for the x60 address and regressed to 10 mismatches. Assignment-in-condition shape compiled to the same 3 r3-vs-r4 mismatches. Both edits were reverted.
- **Likely fix:** Pure permuter territory. Seed from current source; manual source-shape levers are exhausted unless a known r3/r4 temp-lifetime pattern is found in a sibling Kirby function.
