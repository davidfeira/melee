---
function: itLinkboomerang_UnkMotion1_Phys
tu: src/melee/it/items/itlinkboomerang.c
headline: regalloc + sdata2-float
tags: [regalloc, sdata2-float, permuter-false-positive, paired-siblings]
---
## itLinkboomerang_UnkMotion1_Phys (`src/melee/it/items/itlinkboomerang.c`) — regalloc + sdata2-float

- **Tags:** `regalloc`, `sdata2-float`, `permuter-false-positive`, `paired-siblings`
- **Best fuzzy:** 99.05%
- **Diagnosis:** 99.05% with 14 mismatches: 3 are sda21 reloc-symbol mismatches (target uses named globals it_804DCD68/0.0f, it_804DCD88/0.5, it_804DCD90/3.0; base uses anonymous @N@sda21 from inlined my_sqrtf doubles _half=.5/_three=3.0 and 0.0f literal). Other 11 are downstream f4 vs f5 register allocation cascade through my_sqrtf inline body (lfs/fadds/fcmpo/frsqrte/3x fnmsub/fmul) plus stack 0x14 vs 0x10 spill slot for the hypot-attrs->xC subtract. UnkMotion2_Phys is identical source and identical 99.05%, so same fix would unlock both.
- **Tried:** (1) Inlined attrs->xC into subtract: dropped to 90.21% (worse, 20 mismatches, eliminated lfs f4,0xc(r4) entirely). (2) Split hypot/subtract into separate statements with intermediate var: no change, still 14 mismatches at 98.8% strict. The xC load can't be repositioned by source rearrangement.
- **Likely fix:** The named-symbol issue may be permuter-false-positive class — sdata2 anchor deduplication post-link. But 11/14 mismatches are real register-allocation diffs in the inlined my_sqrtf, suggesting the source's my_sqrtf inline form may need adjustment (e.g., volatile sequencing of the 3-iteration newton refinement, or the static const double declaration ordering). Worth trying: extract sqrt to a helper that mirrors the target asm shape, or alter the order of static const _half/_three declarations. Also: this entire TU has many functions referencing it_804DCD68/88/90 named symbols — those globals may need a forward extern declaration in source so MWCC emits them as named externs instead of anonymous literals. Investigate why other functions in the TU (e.g. it_802A0E70, itLinkboomerang_UnkMotion1_Anim) match 100% despite same 0.0f literal usage.
