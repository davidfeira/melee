---
function: grPushOn_802190D0
tu: src/melee/gr/grpushon.c
headline: permuter-queued
tags: [permuter-queued]
---
## grPushOn_802190D0 (`src/melee/gr/grpushon.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** 85.5065%
- **Diagnosis:** 86.61% match. Structural code correct (loop iterates 9 lobjs from gobj->hsd_obj->next, asserts LOBJ_POINT, applies color/scaled-pos/dist-attn from 9-entry config table at grPushOn_803E7B90+0x1C). Two blockers: (1) MWCC pools all 3 data refs in target (file string 803E7B68, expr string 803E7CA8, light array 803E7BAC) under single 'lis grPushOn_803E7AC8@ha' base via offsets 0xa0/0x1e0/0xe4 — my source only references 803E7B90 so MWCC emits 3 separate lis loads. (2) Register allocation differs (target r27..r31 stmw 0x24, mine r26..r31 stmw 0x20) due to extra regs for separate string bases. Permuter could find correct pooling/scheduling. Array data lives inside grPushOn_803E7B90 (0x13C in symbols.txt) — accessed via (u8*)&sym+0x1C cast to grPushOn_LightConfig{GXColor;Vec3;f32;f32;s32}.

