---
function: grAnime_801C83D0
tu: src/melee/gr/granime.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, permuter-false-positive, paired-siblings]
---
## grAnime_801C83D0 (`src/melee/gr/granime.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `permuter-false-positive`, `paired-siblings`
- **Best fuzzy:** 99.8302%
- **Diagnosis:** Same regalloc-result-in-r0-vs-r3 pattern as documented sibling grAnime_801C84A4. Wrapper form (current) compiles to frame 0x28 (calls grAnime_801C8318) but target wants frame 0x30 with inlined logic — gives 99.83%, 9 mismatches, all frame-size related (stwu/stw/lwz/addi offsets). Inline form with u8 _[8] padding produces correct frame 0x30 but exposes the same 3-instruction regalloc diff as sibling 801C84A4: target keeps result var in r0 across both predecessor blocks of HSD_AObjGetFlags join (li r0, 0; lwz r0, 0x14(r1); mr r3, r0), base uses r3 directly (li r3, 0; lwz r3, 0x14(r1)). Sibling 801C84A4 documented this as permuter-blocked due to varargs cr1eq in HSD_ForeachAnim — same blocker applies here. Note mentions 801C83D0 'matched as wrapper' historically but it currently doesn't (likely sibling 801C8318 changed since).
- **Tried:** (1) wrapper form via grAnime_801C8318 — 99.83%, 9 frame-size mismatches; (2) inline form mirroring 801C84A4 with u8 _[8] frame padding — 97.92%, 3 mismatches matching documented permuter-blocked regalloc pattern
- **Likely fix:** Same as 801C84A4: (a) tooling fix — patch decomp-permuter import.py to translate crclr cr1eq -> crclr 6 then cluster permute. (b) source-shape — coax mwcc to use r3 directly across early-NULL + fall-through join with HSD_AObjGetFlags(result). (c) potentially this needs sibling grAnime_801C8318 to be re-shaped first since the prior matched form was wrapper-based.
