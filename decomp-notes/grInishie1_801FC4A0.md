---
function: grInishie1_801FC4A0
tu: src/melee/gr/grinishie1.c
headline: permuter-false-positive + sdata2-float
tags: [permuter-false-positive, sdata2-float, sdata2-named-floats, float-regalloc]
---
## grInishie1_801FC4A0 (`src/melee/gr/grinishie1.c`) — permuter-false-positive + sdata2-float

- **Tags:** `permuter-false-positive`, `sdata2-float`, `sdata2-named-floats`, `float-regalloc`
- **Best fuzzy:** 99.9115%
- **Diagnosis:** At 99.82%, 3 mismatches: (a) two lfs of 0.0f use named sda21 symbol grI1_804DB5C8 in target while base emits anonymous @331 — sdata2 named-float false-positive class; (b) one fcmpu cr0,f2,f1 vs f1,f2 operand-swap that mwcc normalizes regardless of source ordering (tested vel != 0.0f and 0.0f != vel — same output).
- **Tried:** Two attempts: (1) initial decomp via gp/vars pointer caused mwcc to emit addi r31, r3, 0xc4 for vars base — fixed by accessing gp->gv.inishie1.X directly throughout (matches sibling 801FC018 style); (2) tried 0.0f != vel reordering to swap fcmpu operands — no effect.
- **Likely fix:** Source-shape is correct. Float-pool naming requires TU-wide named-constant decl for 0.0f at sdata2 slot grI1_804DB5C8 (same blocker as 801FC018, 801FC110). Fcmpu swap is a permuter-class register/scheduling difference, but combined with sdata2 false-positive the permuter would short-circuit on byte-equal bytes.

