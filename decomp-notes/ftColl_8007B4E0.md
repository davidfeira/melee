---
function: ftColl_8007B4E0
tu: src/melee/ft/ftcoll.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## ftColl_8007B4E0 (`src/melee/ft/ftcoll.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 96.7647%
- **Diagnosis:** Pure r5/r6 and r10/r11 register allocation swap throughout the loop body. Game binary assigns r5=byte-offset-counter, r6=hurt_capsule-walker, r11=init-temp-ptr; our compile assigns r6=byte-offset-counter, r5=hurt_capsule-walker, r10=init-temp-ptr. 30 mismatches, all DIFF_ARG_MISMATCH, no structural diff. Source code is correct and identical to upstream/master matched version.
- **Tried:** (1) Index-based loop (original): 96.76%, 30 mismatches all register. (2) Pointer-based loop with hurt++ and FighterHurtCapsule* hurt: 93.6%, 39 mismatches, worse. Reverted to index-based.
- **Likely fix:** Permuter should resolve the r5/r6 and r10/r11 swap -- these are exactly the kind of register allocation choices the permuter handles. Note: upstream/master already has this function matched with identical source, suggesting this is a TU-context-dependent regalloc difference.

