---
function: ftCo_800AE7AC
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, frame-size, bitfield-reuse]
---
## ftCo_800AE7AC (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `frame-size`, `bitfield-reuse`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Manual decomp at 69.45% (141 mismatches). Function is structurally correct: sets fp->x1A88 bitfield flags (xF8_b0=1; xF9_b1/b3/b5/b7=0; xFA_b2/b34_lo/b6 conditional on arg2>1), inlined ftCo_800A5908 item-kind check (8/9/0x12), conditional path through ftCo_800A8210 vs blast-zone-center+ftCo_800A6FC4+ftCo_800A1CC4. Remaining diff is pure register allocation: target uses r28-r31+r7-temp for &fp->x1A88 (5-reg), base uses r28-r31 (4-reg); this cascades into a 0x10 frame-size mismatch and r29/r30/r31 swaps throughout. Bit-position 0x08 of xFA accessed via 'data->xFA_b34 = data->xFA_b34 | 1' (single-bit rlwimi 28,28) since struct has xFA_b34:2 combined. Header decls for ftCo_800A8210/ftCo_800A6FC4 are UNK_PARAMS so the calls use cast through fn-pointer types; that should be no-op for codegen but worth checking when permuter unblocked.

