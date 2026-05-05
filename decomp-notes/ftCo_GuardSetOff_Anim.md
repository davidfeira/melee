---
function: ftCo_GuardSetOff_Anim
tu: src/melee/ft/chara/ftCommon/ftCo_Guard.c
headline: stack-offset + permuter-false-positive
tags: [stack-offset, permuter-false-positive, rodata-typing]
---
## ftCo_GuardSetOff_Anim (`src/melee/ft/chara/ftCommon/ftCo_Guard.c`) — stack-offset + permuter-false-positive

- **Tags:** `stack-offset`, `permuter-false-positive`, `rodata-typing`
- **Best fuzzy:** 99.8833%
- **Diagnosis:** 99.88% fuzzy / 99.66% objdiff. Two distinct mismatch classes mixed: (1) target uses sdata2 named float globals ftCo_804D8538 (0.0f) and ftCo_804D8568 (1.0f), base uses anonymous @212@sda21 / @289@sda21 - this is the rodata-typing/permuter-false-positive class; post-link bytes match but report.json fuzzy does not. (2) Stack frame is 0x68 in target, 0x58 in base; 16 bytes of extra slack at the bottom of the frame. AbsorbDesc local lives at sp+0x30 in target vs sp+0x10 in base; Vec3 scl at sp+0x48 vs sp+0x38. Both classes coexist.
- **Tried:** (a) Added u8 _[16] = { 0 }; at function top - frame size went 0x58 to 0x68 (matches target prologue), and fuzzy improved 99.88 to 99.93, but locals stayed at low offsets so the +0x20 displacement on every struct field still mismatches. (b) FORCE_PAD_STACK_16 same behavior. (c) FORCE_PAD_STACK(32) overshoots: frame becomes 0x78.
- **Likely fix:** The 0x10 of slack at sp+0x08..sp+0x18 in target is between linkage area and the inlined ftCo_80092450 AbsorbDesc, so a true fix needs the inliner to allocate ftCo_80092450's AbsorbDesc at a higher offset. May require explicit non-static inline helper or a forced PAD_STACK that mwcc cannot elide and is allocated FIRST in declaration order. The named-float side is a known permuter-false-positive; needs a global float definition somewhere (ftCo_804D8538/8568 in rodata) for the linker to dedupe. Before further work, check if ftCo_804D8538 / ftCo_804D8568 are declared as named extern floats anywhere in src - if not, naming them in a static.h or .c may unblock both branches simultaneously since they share lfs targets.
