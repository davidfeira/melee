---
function: un_8031F714_OnEnter
tu: src/melee/vi/vi1101.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc, data-anchor, sdata2-named-floats, paired-siblings]
---
## un_8031F714_OnEnter (`src/melee/vi/vi1101.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`, `data-anchor`, `sdata2-named-floats`, `paired-siblings`
- **Best fuzzy:** 97.6326%
- **Diagnosis:** 97.46% match, 44 mismatches. ~38 are pure register-allocation shuffle (r26<->r28, r27<->r29, r28<->r31 across HSD_GObj/HSD_CObj/HSD_JObj locals through the camera and model loop) plus 2 'mr rD,rS' vs 'addi rD,rS,0' instruction-form choices in the GObjGXLink callback setup — classic permuter territory. The remaining ~6 are decomp-blocked false-positives: target uses 'un_80400200@ha/@l' as the named anchor for a 0x58 .data block holding the Vec3 init pos + 2 camera Vec3s + 3 strings ('Vi1101.dat','visual1101Scene','visual1101Cam2Scene'), but our compilation only emits the 3 strings (anonymous '...data.0@l') because the Vec3 init data lives in the still-undecompiled sibling un_8031F294. Likewise 'lfs f1, un_804DE0DC@sda21' (the named 0.0f) vs our 'lfs f1, @N@sda21' anonymous float-pool entry — un_804DE0DC is a sdata2 global referenced by un_8031F294. Both anchor diffs auto-resolve once un_8031F294 is decompiled in the same TU. Source structure semantically correct: SceneDesc model loop, light->cam ordering, gm_80164840(7) chooses scene, lbArchive_LoadSymbols varargs match (crclr cr1eq emitted), HSD_GObj/HSD_JObj/HSD_CObj plumbing matches the vi0102/vi0501/vi0401 sibling pattern.
- **Tried:** (1) initial decomp matching the vi0102/vi0501 OnEnter shape with separate locals for light_gobj/cam_gobj/model_gobj — 97.46%/44 mismatches. (2) collapsed to single 'gobj' local reused across 3 GObj_Create calls — went DOWN to 97.39%/46. Reverted to attempt-1 source. Casts fn_8031F56C through (GObj_RenderFunc) since GObj_SetupGXLinkMax wants (HSD_GObj*, int) but the existing matched fn_8031F56C is (HSD_GObj*). HEADER CHANGE: vi1101.h had 'UNK_RET un_8031F294(UNK_PARAMS)'; updated to 'void un_8031F294(int char_index, int costume_index)' so the call site type-checks.
- **Likely fix:** Dispatch to permuter (currently offline per override) for the regalloc shuffle — should land 100% on the .o-only diff. The 6 false-positives WILL persist in the strict diff until un_8031F294 is decompiled into the same TU; at that point the un_80400200 named data anchor and un_804DE0DC named sdata2 float will be referenced by name in this TU and the anchor symbols will materialize. Linker bytes already match (post-link the rodata anchor and sdata2 0.0f are at the same addresses), so this matches the data-anchor/sdata2-float false-positive class.

