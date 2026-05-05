---
function: gm_801A9B30_OnEnter
tu: src/melee/gm/gm_1A4C.c
headline: data-symbols-missing + cross-tu-globals
tags: [data-symbols-missing, cross-tu-globals, mwcc-aliasing]
---
## gm_801A9B30_OnEnter (`src/melee/gm/gm_1A4C.c`) — data-symbols-missing + cross-tu-globals

- **Tags:** `data-symbols-missing`, `cross-tu-globals`, `mwcc-aliasing`
- **Best fuzzy:** 99.9748%
- **Diagnosis:** 99.97% fuzzy / 99.68% strict, 8 mismatches all in the switch-loaded thpfile lookup. Target uses named-symbol reloc 'lis r3, gm_803DB640@ha; addi r30, r3, gm_803DB640@l' with offsets 0x278/0x5B4/0x8D0 (which reach gm_803DB8B8/BBF4/BF10 from gm_803DB640+0x210 in the merged final .data). Base produces section-relative reloc 'lis r3, ...data.0@ha; addi r30, r3, ...data.0@l' with offsets 0x2D4/0x610/0x92C. Both resolve to the same final addresses, but the relocation symbol choice differs. In our compiled .o gm_803DB640 is at .data offset 0x5C (size 0x1A), while ...data.0 is the section anchor at 0x0; mwcc picks the section anchor because gm_803DB640+0x278 lies far outside the named symbol's declared range. Final binary identical, but objdiff sees the symbol-name mismatch and per-instruction strict diff penalizes it.
- **Tried:** (1) Sibling-style 'u8* data = (u8*) gm_803DB640;' anchor reassignment a la gm_801963B4_OnEnter dropped match to 94% (extra block scope spilled differently and added a separate lis/addi pair r4 used alongside r30). (2) Forward 'extern char gm_803DB640[];' before the definition - no effect (mwcc still uses ...data.0 anchor). Sonnet's existing pattern '((char**)(gm_803DB640 + 0x278))[temp_r31]' is the best 99.97% state and is preserved in working tree.
- **Likely fix:** Cross-TU. The sibling gm_801963B4_OnEnter matched because lbl_803D9F80 is genuinely *UND* in gm_18A5.o (defined in another TU) which forces mwcc to use the named reloc. To replicate here, gm_803DB640 needs to NOT be defined in gm_1A4C.c - extract its definition (the 'GmRegendSimpleCaptain.thp' string) plus likely the entire 0x210 bytes of preceding strings (assertion/character-name strings at .data:0x803DB430..0x803DB63F) into a separate TU/asm file so that gm_803DB640 appears extern in this TU. Same pattern as gricemt/itdosei tu-wide-data entries. Cannot be fixed at the function level.
