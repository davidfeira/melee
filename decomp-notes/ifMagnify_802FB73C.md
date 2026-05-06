---
function: ifMagnify_802FB73C
tu: src/melee/if/ifmagnify.c
headline: permuter-queued
tags: [permuter-queued]
---
## ifMagnify_802FB73C (`src/melee/if/ifmagnify.c`) — permuter-queued

- **Tags:** `permuter-queued`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 96.96% manual match (28 register-allocation mismatches). Structure semantically correct: 3-arg void function (player entry pointer, Vec2* in, Vec2* out) that clamps in-vector to a bounding rectangle/diagonal and writes a state code (1-4) into the player entry's u8 unk:6 bitfield at +0xC. Constants ifMagnify_804DDB08 (0.0f), DDB28 (162.7f), DDB2C (-162.7f), DDB30 (0.6438464f), DDB34 (-0.6438464f), DDB38 (-252.70001f), DDB3C (252.70001f). Mismatches are mwcc allocating different float regs: target loads in->x to f2 and DDB08 to f1, ours allocates the opposite (f1 for in->x, f2 for DDB08). Cascades through entire function. Also one DIFF_DELETE where target reloads DDB08 from sda21 (compiler appears to have spilled) but ours kept it live. Header changed: ifmagnify.h now has 'void ifMagnify_802FB73C(void* player, Vec2* in, Vec2* out)' replacing UNK_RET, plus #include <dolphin/mtx.h>. Also added 7 sda2 extern f32 declarations to ifmagnify.c. Permuter-queued for register-allocation polish.

