---
function: gmCamera_801A31FC
tu: src/melee/gm/gmcamera.c
headline: string-pool + tu-wide-data
tags: [string-pool, tu-wide-data, data-anchor, regalloc, frame-size, permuter-dispatched]
---
## gmCamera_801A31FC (`src/melee/gm/gmcamera.c`) — string-pool + tu-wide-data

- **Tags:** `string-pool`, `tu-wide-data`, `data-anchor`, `regalloc`, `frame-size`, `permuter-dispatched`
- **Best fuzzy:** 89.5268%
- **Diagnosis:** Stuck at 89% / 27 mismatches. Major blocker is TU-wide data layout ordering: target binary places literal strings 'SIS_VsCameraData' (gmCamera_803DA6A0), 'IfCamera' (lbl_803DA720), and 'IfCamera_Top_model_set' (lbl_803DA728+0x14) interleaved BETWEEN globals gmCamera_803DA630 and gmCamera_803DA6B4 (and gmCamera_803DA758 at the END), but mwcc emits literals after all globals in source order. This causes r30-relative offsets to mismatch (target 0xF0/0x10C/0x70 vs ours 0x120/0x12C/0x10C). Fix likely requires: (1) moving gmCamera_803DA758 from static to global declared LAST, (2) declaring gmCamera_803DA6A0/lbl_803DA720/lbl_803DA728 as named global char arrays at the right textual positions. This would also affect already-near-matched gmCamera_801A2650 (99.64%, identical string-pool blocker: target uses gmCamera_803DA6A0 vs our @215). Coordinated TU-wide layout rework recommended. Remaining mismatches after that fix would be regalloc/scheduling (extra register saved, frame 0x38 vs 0x20) — permuter territory.
- **Tried:** Two source-shape attempts. (1) Used local gcus pointer for gmCamera_80479BC8.gcus access — got 89% with 27 mismatches; r31 anchored well but data offsets diverged. (2) Removed gcus local, using direct gmCamera_80479BC8.gcus.* — dropped to 84% (more bss anchor reloads). Reverted to attempt 1. The semantic logic is correct (verified against m2c output and asm flow); only blocker is data layout order. NOTE: decomp-permuter is offline (do not auto-dispatch); permuter-dispatched tag used per closest canonical match for permuter-queued status.
- **Likely fix:** TU-wide rework: move gmCamera_803DA758 to file end (non-static), declare global char arrays for 'SIS_VsCameraData', 'IfCamera', and the 0x30-byte concatenated lbl_803DA728 block (containing 'Info_Top_model_set' + 'IfCamera_Top_model_set' + padding), then reference them by name. Will also fix gmCamera_801A2650 to 100%. After layout fix, queue permuter for remaining regalloc/frame-size diffs.

