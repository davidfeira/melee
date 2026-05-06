---
function: ftCo_800A6D2C
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: inlining + frame-size
tags: [inlining, frame-size, regalloc]
---
## ftCo_800A6D2C (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — inlining + frame-size

- **Tags:** `inlining`, `frame-size`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Source structurally correct (76% match from 0%). ftCo_800A2718 (small static helper, also has inlineL0/inlineL1 inline calls) gets force-inlined by mwcc -inline auto into ftCo_800A6D2C, even through a static-inline _dontinline wrapper (mwcc inlines through one level of forwarding). The inlining inserts extra arg0==NULL test, both inlineL0/inlineL1 calls, plus stage_info pointer load (r27=stage_info@l), shifting register allocation everywhere and shrinking stack frame by 0x18 bytes. Target asm has clean bl ftCo_800A2718.
- **Tried:** Attempt 1 direct call ftCo_800A2718(cur) -> 67%. Attempt 2 added static inline ftCo_800A2718_dontinline wrapper -> 76% (still inlined through wrapper since 800A2718 body is small). Both attempts: float constants, mpCheckFloor signature with 4 stack args, sda21 0.0/-1.0/0.5/5.0/20.0 constants, Vec3 a/b locals across HSD_Randf spill, hit_pos.y >= cur_pos.y - x558 invert via cror eq,gt,eq, four blast-zone bound checks all confirmed correct via bl Stage_GetBlastZone* calls.
- **Likely fix:** Either: (a) wrap ftCo_800A2718 definition in #pragma dont_inline on/off (used elsewhere in same TU at L2334) — but this would touch a matched function and risks regressing it; (b) source must use indirect call or some construct that mwcc cannot constant-fold. Permuter cannot solve this without source restructure that affects ftCo_800A2718's compilation. Permuter-queued: not productive — structural inlining barrier.

