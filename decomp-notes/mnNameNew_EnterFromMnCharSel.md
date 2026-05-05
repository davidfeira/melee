---
function: mnNameNew_EnterFromMnCharSel
tu: src/melee/mn/mnnamenew.c
headline: tu-wide-data + rodata-typing
tags: [tu-wide-data, rodata-typing]
---
## mnNameNew_EnterFromMnCharSel (`src/melee/mn/mnnamenew.c`) — tu-wide-data + rodata-typing

- **Tags:** `tu-wide-data`, `rodata-typing`
- **Best fuzzy:** 99.8495%
- **Diagnosis:** 99.85% fuzzy. 31 mismatches all addi r0,r30,0xN — r30 = mnNameNew_803EDA58@ha+@l. Target offsets (e.g. 0x988,0x9A8,0x9C4,...,0xC50,0x934) are exactly 0x4F8 higher than base (0x490,0x4B0,...,0x758,0x43C). Section layout: ours .data=0xCD0, base .data=0x7C9 (delta 0x507); ours .sdata=0x390, base .sdata=0x28 (delta 0x368); ours .rodata=0x10, base .rodata=0x34. TU-wide drift: strings being placed in .data instead of .rodata, plus extra constants in .sdata. r30 anchor points into .data, so the *actual address* of every string referenced by lbArchive_LoadSections shifts. Caused by other unmatched functions in mnnamenew.c (16 left non-matching including mnNameNew_MainInput 67%, AddCharacterToName 80%, mnNameNew_8023D130 81%, mnNameNew_8023DA08 80%). Cannot fix in this function alone — need TU-wide rodata/data layout repair via fixing the upstream non-matching functions.
- **Tried:** prep+diff inspection, section size analysis via objdump on base vs ours
- **Likely fix:** Fix the structural non-matchers in mnnamenew.c first (especially mnNameNew_MainInput, AddCharacterToName, mnNameNew_8023D130 which likely cause string/const drift). Once .data shrinks by ~0x4F8 and .rodata grows accordingly, this function will match cleanly. Permuter cannot help — every mismatch is a real-symbol relocation arg, not a register/order issue.
