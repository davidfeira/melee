---
function: grAnime_801C84A4
tu: src/melee/gr/granime.c
headline: regalloc + permuter-blocked
tags: [regalloc, permuter-blocked, varargs-cr1eq, upstream-regression]
---
## grAnime_801C84A4 (`src/melee/gr/granime.c`) — regalloc + permuter-blocked

- **Tags:** `regalloc`, `permuter-blocked`, `varargs-cr1eq`, `upstream-regression`
- **Best fuzzy:** 97.9245%
- **Diagnosis:** Pure regalloc diff at the join point feeding HSD_AObjGetFlags: target uses r0 as join vehicle (li r0,0 / b join; lwz r0,0x14(r1); mr r3,r0 / bl) while base uses r3 directly (li r3,0; lwz r3,0x14(r1); bl). Source structure is identical to upstream matched version. Permuter blocked by 'crclr cr1eq' reloc in variadics HSD_ForeachAnim call -- binutils rejects it as unsupported relocation. Attempts to eliminate 'result' intermediate or invert the jobj==NULL condition either increase mismatch count or break control flow shape.
- **Tried:** (1) Inverted condition (jobj!=NULL) + use sp14 directly in HSD_AObjGetFlags call -- broke to 5 mismatches due to bne/beq flip in branch direction. (2) Restored original source which already matches upstream exactly -- confirmed 97.92% is the ceiling without permuter.
- **Likely fix:** Patch decomp-permuter import.py to translate 'crclr cr1eq' to 'crclr 6' before assembly, then dispatch cluster permuter -- 3-instruction pure regalloc noise should land in low iterations. Alternatively wait for upstream to be pulled; local source already matches upstream implementation exactly.

