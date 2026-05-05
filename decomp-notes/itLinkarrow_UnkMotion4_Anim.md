---
function: itLinkarrow_UnkMotion4_Anim
tu: src/melee/it/items/itlinkarrow.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive, sdata2-named]
---
## itLinkarrow_UnkMotion4_Anim (`src/melee/it/items/itlinkarrow.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`, `sdata2-named`
- **Best fuzzy:** 99.1016%
- **Diagnosis:** 29 mismatches: ~25 are r30/r31 swap on ip vs jobj (target r30=ip,r31=jobj; base r31=ip,r30=jobj); 2 are 'lfs f3, it_804DCE28@sda21' vs 'lfs f3, @277@sda21' (named sdata2 leak from float consts other agent added at top of TU); 4 'real' lfs from r3 same offsets (likely register-window scheduling differences). Source uses deg_to_rad (math.h static) so target shouldn't reference named it_804DCE28 unless the explicit 'float const it_804DCE28 = 0.017453292f' at file scope is being interned and reused by the compiler in preference to the deg_to_rad pool entry @277.
- **Tried:** (1) swap declaration order: jobj before ip — no change. (2) split decl/init: declare locals then assign GET_ITEM/GET_JOBJ later — no change. mwcc allocation here is insensitive to local-decl shuffling.
- **Likely fix:** Either (a) remove the 'float const it_804DCE28 = 0.017453292f' from the .sdata2 block in this TU (other agent added it; target should keep using deg_to_rad's @277 pool), AND find a structural change for the regalloc swap; or (b) the named float is a real symbol that should appear, but only via use, not declaration — investigate whether the original game referenced it_804DCE28 by name elsewhere in TU first. For regalloc, suspect a missed early-use or temp lifetime in the prologue forces ip into the wrong save reg; consider a no-op early-use of jobj before ip (e.g. read jobj->flags into a UNUSED temp). Permuter classifies sdata2 mismatches as false-positive class so dispatching now risks reporting a non-actual match.
