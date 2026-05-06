---
function: grHomeRun_8021E500
tu: src/melee/gr/grhomerun.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, string-pool, permuter-territory]
---
## grHomeRun_8021E500 (`src/melee/gr/grhomerun.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `string-pool`, `permuter-territory`
- **Best fuzzy:** 91.7031%
- **Diagnosis:** 91.08% match. Source structure semantically correct: switch decoded to chained if/else with correct case bodies, all jobj scale/translate setters with grHr_804D6AE4 multiplication match, gp+0xD0 raw byte cast for unkD0 used (since grHomeRun_GroundVars only declares xC4-xCC), child translateX=0.0f, gp->gv.homerun.xC4/xC6 final stores match. Required header fix: grhomerun.h declared UNK_RET grHomeRun_8021E500(UNK_PARAMS) — changed to HSD_GObj* grHomeRun_8021E500(int).
- **Tried:** switch -> if/else if chain (broke jump table, +5pp); collapsed sel temp into inline (arg/grHr_804D6ADC)%4 expression; experimented with f32 part temp placement.
- **Likely fix:** (1) idx allocates to r29 instead of target's r28: would need different declaration ordering or live-range manipulation. (2) Division step reg alloc r0 vs r5 swap (target: divw r5,r27,r4 then srawi r0,r5,2; base: divw r0,r27,r4 then srawi r5,r0,2). (3) Frame 0x58 vs target 0x50 — extra 8 bytes locals/padding. (4) __FILE__ string for HSD_ASSERTMSG resolves to anonymous @682 sda21 vs target's grHr_804D49C0 named — this is mwcc string-pool ordering, needs the 'grhomerun.c' string to be declared/used in TU at right offset. Permuter would handle (1)(2)(3) easily.

