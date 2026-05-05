---
function: grBigBlue_801E8B84
tu: src/melee/gr/grbigblue.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive]
---
## grBigBlue_801E8B84 (`src/melee/gr/grbigblue.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`
- **Best fuzzy:** 97.9167%
- **Diagnosis:** 3 mismatches: 2 dead 'li r4, 0' / 'li r4, 1' instructions in target absent from base + 1 sdata2 named-vs-anonymous float reloc (grBb_804DB310@sda21 vs @175@sda21 for 0.0f literal). Loop is fully unrolled by mwcc. Target keeps a register-dead init 'li r4, 0' before the loop and a register-dead 'li r4, 1' inside iter 1's inner-most success branch (right after fmr f1, f0). r4 is never read anywhere. Iters 2-4 have no li r4. Pattern is consistent with a 'found' flag pattern (e.g. found = 0 init, found = 1 in inner if-block, dead afterwards) where mwcc emits the first store but constant-props subsequent ones to dead.
- **Tried:** Variant 1: Added 'int found = 0;' init + 'found = 1;' inside the inner-most update block plus '(void)found;'. mwcc DCE'd the stores entirely (no change in mismatch count: 3). Variant 2: Converted for-loop to do-while with explicit 'i++' at body bottom. Broke unrolling completely (40+ mismatches). Reverted to baseline 97.864%.
- **Likely fix:** (a) Find a variant that defeats mwcc's DCE on the dead 'i'/'found' var � maybe declare it volatile (would cause stores not just li, doesn't fit), or use an aliasing pointer. (b) Identify which sibling function uses grBb_804DB310 by name so the float pool symbol matches � would resolve the 1 sda21 mismatch. (c) Both 'li r4' instructions could potentially be matched if the unroll preserves a non-dead use of 'i' in iter 1 but elides later � maybe an intentional dead store via 'i = !!result' or similar. Permuter unlikely to find this since it's a structural source-shape difference. The existing TODO comment about 'i variable' confirms prior attempts couldn't crack this.
