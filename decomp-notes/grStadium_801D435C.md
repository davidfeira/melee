---
function: grStadium_801D435C
tu: src/melee/gr/grpstadium.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive, sdata2-float]
---
## grStadium_801D435C (`src/melee/gr/grpstadium.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`, `sdata2-float`
- **Best fuzzy:** 98.8049%
- **Diagnosis:** 27 mismatches (98.80% fuzzy / 97.97% strict): 24 r29<->r30 swap on gp pointer (target gp=r29, loop counter r30; base gp=r30, loop counter r29). Plus 1 sdata2 named-vs-anonymous (grPs_804DAEF8@sda21=0.0f vs @203@sda21) and 2 instruction-reorder around the second loop body (lfs f0,0x1c(r3) vs lfs f1,0xd4(r30)).
- **Tried:** V1: hoist 'cur' decl into the if-block where it is used (no change, 27 mismatches). V2: drop redundant outer 'var_r28 = 0;' init and inner 'u32 var_r4 = 0;' init (no change, 27 mismatches). Both reverted.
- **Likely fix:** Pure permuter territory for the regalloc swap (r29<->r30 across gp lifetime). Sibling grStadium_801D2A60 already documented with same grPs_804DAEF8 orphan-symbol pattern (line 705-710 in decomp-notes.md): named in symbols.txt but not referenced by any source — TU-wide artifact. Recommend dispatching to cluster permuter for the regalloc; sdata2 mismatch will remain false-positive (post-link bytes match).
