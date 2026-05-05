---
function: grBigBlue_801EACE8
tu: src/melee/gr/grbigblue.c
headline: stack-offset + frame-size
tags: [stack-offset, frame-size, permuter-false-positive, tu-wide-data]
---
## grBigBlue_801EACE8 (`src/melee/gr/grbigblue.c`) — stack-offset + frame-size

- **Tags:** `stack-offset`, `frame-size`, `permuter-false-positive`, `tu-wide-data`
- **Best fuzzy:** 99.799%
- **Diagnosis:** At 99.5477% / 32 mismatches. Two coupled false-positive classes (same blocker as grBigBlue_801E8D64): (1) Frame-size mismatch: target frame is 0x14 (20B) smaller than base. All hw_left (sp+0x44 vs 0x58), hw_right (sp+0x38 vs 0x4c), route_pos (sp+0x1c vs 0x40), pos (sp+0x5c vs 0x64) stack slots are shifted by 8-20 bytes. Base packs the locals tighter than target (target=20B more local space = an unused 16B Vec3 + 4B alignment, or 5x f32 unused). (2) sdata2 named-vs-anonymous floats: grBb_804DB3A0, grBb_804DB310 (-FLT_MAX), grBb_804DB2F4 (0.0f), grBb_804DB38C (68.0f), grBb_804DB350 (0.5f) all emit as named extern in our build vs anonymous @N@sda21 in target. These named externs are referenced extensively across the TU (lines 1425-4857), so they must remain declared - the named-vs-anon split is a TU-wide MWCC merge artifact. (3) Minor: fnmsubs f25 has swapped multiplicand operands (f1,f2 vs f2,f1) - likely tied to expression form '68.0F * Ground_801C0498() * 0.5F' associativity but won't matter while frame is wrong.
- **Tried:** prep+diff inspection only - no source edits attempted; this is the established permuter-false-positive class for the grbigblue TU per existing grBigBlue_801E8D64 stuck note. The stuck note explicitly documents that (a) removing named sdata2 externs breaks more than it fixes due to TU-wide use, (b) PAD_STACK adjustments overshoot due to MWCC 8-byte alignment behavior, and (c) the permuter scorer treats named-vs-@N as equivalent so it would dispatch but never produce a report.json-100% match.
- **Likely fix:** Same as grBigBlue_801E8D64 fix path: identify a 4-byte local that survives optimization but doesn't trigger 8-byte alignment bump. Candidates: (1) collapse hw_left/hw_right Vec3 into single Vec3 reused (requires verifying that grBb_803B8114 copy can fit a tighter pattern); (2) re-examine PAD_STACK(0x24) - maybe PAD_STACK(0x10) or removing it entirely yields the smaller frame; (3) declare 'f32 dist' inside the if-block instead of outer scope (currently dist is shared between inner and outer scopes); (4) move route_pos declaration into the conditional block where it's used. DO NOT dispatch permuter - false-positive.
