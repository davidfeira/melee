---
function: grAnime_801C7C1C
tu: src/melee/gr/granime.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, string-pool, struct-typing]
---
## grAnime_801C7C1C (`src/melee/gr/granime.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `string-pool`, `struct-typing`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Function structure decompiled correctly (semantic model matches sibling grAnime_801C8138, sibling 801C683C/6A54/6C0C). 64.79% match, 198 mismatches. Structural blockers: (1) stack frame is 0x70 vs target 0x68 — 8 bytes extra, indicating mwcc spills 2 extra register-allocated locals because of the inline child-loop var declarations; (2) register allocation differs across the function (r27 base vs r31 target, r29 vs r28, r23 vs r30, r31 vs r29 — entire callee-saved palette shifted); (3) the assert string 'archive' resolves to grAnime_804D4550@sda21 in target but @724@sda21 in base — indicates the static const local string is being emitted differently. The unk4->unk8[arg1].unk4 loads compile to addi r0, r3, 4; lwzx r3, r4, r0 (indexed) instead of target add r3, r3, r0; lwz r3, 0x4(r3) — likely needs a struct-field access (UnkStageDat_x8_t needs unk4/unk8/unkC HSD_AnimJoint** etc fields added rather than byte-cast).
- **Tried:** Two source-shape attempts: (1) using ajp/mjp/sjp intermediate locals with *(T***)((u8*)&...+N) style cast — got 64.79%; (2) inlining the cast-deref directly into the if condition, removing intermediates — same 64.79%. Both attempts produce identical asm.
- **Likely fix:** Header change required: extend struct UnkStageDat_x8_t in src/melee/gr/types.h with HSD_AnimJoint** unk4, HSD_MatAnimJoint** unk8, HSD_ShapeAnimJoint** unkC fields (currently u8 _4[0xC]), then access via direct field syntax archive->unk4->unk8[arg1].unk4 etc. — this should produce target's add+lwz pattern instead of addi+lwzx. Also need to check if 'archive' static string needs to be a file-scope const char (likely already is, but emission differs). Likely also need to match local declaration order to coerce mwcc into target's r31/r28/r25/r26/r27 register palette and 0x68 frame size. Header modification touches struct shared with ground.c — REPORT AS HEADER CHANGE.

