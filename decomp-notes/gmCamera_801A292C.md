---
function: gmCamera_801A292C
tu: src/melee/gm/gmcamera.c
headline: rodata-typing + permuter-false-positive
tags: [rodata-typing, permuter-false-positive, data-anchor, regalloc]
---
## gmCamera_801A292C (`src/melee/gm/gmcamera.c`) — rodata-typing + permuter-false-positive

- **Tags:** `rodata-typing`, `permuter-false-positive`, `data-anchor`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Re-attempt 2026-05-05 confirms prior diagnostic. Implemented fresh with f32[12] non-static global gmCamera_803DA630 placed first in .data, achieved 72.58% match (69 mm) - kept in place as net improvement over 0% baseline. Function source-shape semantically correct (matches m2c output, asm semantics). Blocker remains: mwcc emits the .data:0x0 reference as anonymous '...data.0@ha/@l' reloc instead of named 'gmCamera_803DA630@ha/@l'. This is the data-anchor false-positive class - permuter cannot fix because post-link bytes are equivalent but report.json fuzzy treats them as different. Cascades into ~30 register-name shifts (target r29 union base + r26 cached &x48[0] + r28 i + r31 cached NULL across loops; base allocates differently).
- **Tried:** (1) Non-static f32[12] global definition first in .c, with extern in gmcamera.h - still emits ...data.0 reloc; reverted header edit since it didn't help. (2) Restructured to use HSD_Text** texts cache + iterating union-base pointer + do-while loops mirroring asm flow - improved from 71.01% to 72.58% (75 mm to 69 mm) confirming source-shape direction is right. Both attempts blocked at the data-symbol-naming layer regardless of source structure.
- **Likely fix:** Cannot fully solve in this function alone. Coordinated TU fix needed: (a) Decompile gmCamera_801A31FC (still asm) which also references gmCamera_803DA630 - dual referrers may force named reloc. (b) Move gmCamera_803DA630 to NOT be first .data block by adding another initialized global before it. (c) Once data symbol emits as named, dispatch to permuter for the regalloc cascade. Current source-shape preserved at 72.58% as best-known-good baseline for future TU-coordinated work.

