---
function: gmCamera_801A33BC
tu: src/melee/gm/gmcamera.c
headline: permuter-queued
tags: [permuter-queued]
---
## gmCamera_801A33BC (`src/melee/gm/gmcamera.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** 97.3125%
- **Diagnosis:** Reached 96.875% strict / 97.31% fuzzy. Source shape converged. Remaining 11 mismatches are register allocation / scheduling: (1) target uses bge+b pattern for sp10<0 branch where mwcc emits a single blt for my source, (2) target reuses r3 from prior HSD_SisLib_803A6530 call as arg0 for gmCamera_801A2224 (1 lwz r4 vs my lwz r3 + mr r4); HSD_SisLib_803A6530 is declared void but the implementation in sislib.c returns the dst pointer in r3 implicitly. (3) Anonymous data-section / sda21 reloc names (...bss.0, @184) vs target's named gmCamera_80479C20/gmCamera_804DA9D8 are static-global emission style differences (consistent with already-100% gmCamera_801A34FC_OnFrame in same TU - fuzzy ignores them). Required structural fixes already applied: added dont_inline pragma to gmCamera_801A253C/25C8/2640 (else mwcc inlines them), removed unused _no_inline static wrappers, initialized static gmCamera_803DA758[12] array. Also reordered if/else chain to a goto-based form to match target's branch layout. Static.h kept static (matches OnFrame pattern). main.dol SHA1 still OK. Decomp-permuter offline at time of logging.

