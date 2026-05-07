---
function: grZakoGenerator_801CACB8
tu: src/melee/gr/grzakogenerator.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, mwcc-aliasing]
---
## grZakoGenerator_801CACB8 (`src/melee/gr/grzakogenerator.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `mwcc-aliasing`
- **Best fuzzy:** 91.6769%
- **Diagnosis:** All 11 mismatches are in the kind==0x9F branch: target uses r6 for &lbl_8049F030.x4 and r4/r3/r5 for data/load/sentinel-addr, base uses r4/r3 shifted by one register. Target also hoists li r3,-1 and li r0,0 before the cmplw, and pre-computes addi r5,r4,0x3c0 (sentinel addr) before the compare; base defers these after the branch. Both target and base reload lbl_8049F030.x4 after the sth (mwcc-aliasing confirmed). Source content is semantically identical to upstream match; the compiler makes different regalloc+scheduling choices. Prior attempts V1 (data local at function or block scope) and V2 (swapped assignment order) both increased mismatches.
- **Tried:** V1: grZakoGenerator_Data* data=lbl_8049F030.x4 local (10 mismatches, drops r6 pattern). V2: swapped sentinel.x0 and sentinel.x4 assignment order (12 mismatches). V3 (this session): grZakoGenerator_Entry* s=&lbl_8049F030.x4->sentinel with s->x0=-1 and lbl_8049F030.x4->sentinel.x4=NULL (still 11 mismatches, changes addi to sentinel-relative form but doesnt reduce mismatch count).
- **Likely fix:** Permuter territory: register allocation (r4 vs r6 for &x4-addr) and constant/address hoisting before cmplw. No source structural change available; requires permuter scheduling exploration.

