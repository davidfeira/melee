---
function: grZakoGenerator_801CACB8
tu: src/melee/gr/grzakogenerator.c
headline: regalloc + mwcc-aliasing
tags: [regalloc, mwcc-aliasing]
---
## grZakoGenerator_801CACB8 (`src/melee/gr/grzakogenerator.c`) — regalloc + mwcc-aliasing

- **Tags:** `regalloc`, `mwcc-aliasing`
- **Best fuzzy:** 91.6769%
- **Diagnosis:** 11 mismatches all in kind==0x9F branch. Target hoists 'addi r6, r29, 0x4' (=&lbl_8049F030.x4) and pre-loads constants (li r3,-1; li r0,0) BEFORE the cmplw/bne. Target also pre-computes 'addi r5, r4, 0x3c0' (=&sentinel) and uses 'sth r3, 0(r5)' for sentinel.x0 store, then 'lwz r3, 0x0(r6)' to RELOAD lbl_8049F030.x4 (overwritten by sentinel.x4 load), then 'stw r0, 0x3c4(r3)' for sentinel.x4 store. Base just uses r4=&x4_field and r3=x4-deref directly with no hoisting. Else branch matches perfectly using r6 alias pattern; if branch in base does NOT use r6 because compiler doesn't see alias pressure. Source structure mirrors sister fn grZakoGenerator_801CAC14 which uses 'data = lbl_8049F030.x4' intermediate but that produces yet a different pattern (10 mismatches, drops the addi r6 entirely).
- **Tried:** V1: introduced 'grZakoGenerator_Data* data = lbl_8049F030.x4;' intermediate (mirrors sister fn) -> 10 mismatches, eliminates r6 hoisting (wrong direction). V2: swap order of sentinel.x0 and sentinel.x4 assignments -> 12 mismatches, worse.
- **Likely fix:** Permuter scheduling territory: hoisting constants and pre-computing sentinel addr before compare. May need a synthetic source pattern that forces mwcc to materialize &lbl_8049F030.x4 as register-resident pointer (r6) AND keep r4 alive long enough for the sentinel addr precomputation. Possible: an inline helper or address-of expression like 'volatile' or '&lbl_8049F030.x4' tag forcing pointer materialization. Try permuter on if-branch variants.
