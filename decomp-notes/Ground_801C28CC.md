---
function: Ground_801C28CC
tu: src/melee/gr/ground.c
headline: data-anchor + permuter-false-positive
tags: [data-anchor, permuter-false-positive, regalloc, mwcc-loop-opt]
---
## Ground_801C28CC (`src/melee/gr/ground.c`) — data-anchor + permuter-false-positive

- **Tags:** `data-anchor`, `permuter-false-positive`, `regalloc`, `mwcc-loop-opt`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Hand-unrolled inner loop matches structurally (4 iters x 8 stores then 3-iter tail of out[i] = ((s16*)param)[i+0x35] * ((s16*)bgm)[i+0xD]). Achieved 77.97% (105 mismatches). Frame size differs: target stwu -0x30 with stmw r27 (5 saved regs), mine -0x20 with 4 saved regs. Target uses r28 as anchor for Ground_803DFEA8 base, then references msg0/msg1/msg2 + __FILE__ as +0x218/+0x2BC/+0x300/+0x340 offsets. mwcc on my source picks .data.0 anchor instead, which is byte-equivalent post-link but cascades into different register allocation throughout. This is the data-anchor permuter false-positive class — permuter scorer would treat it as 100%, but report.json fuzzy would not.
- **Tried:** Attempt 1: simple single-loop for(i=0;i<0x23;i++) out[i]=a[i]*b[i] -> 41.6% (mwcc unrolled 2x, wrong factor). Attempt 2: hand-unrolled 4 iters x 8 stores then 3-iter cleanup using byte-offset casts (s16*)((u8*)param+n+0x6A) and (s16*)((u8*)b+0x1A..0x28) -> 77.97% structural match.
- **Likely fix:** Force target's anchor choice — possibly extract msg strings as struct members of Ground_803DFEA8 or relocate them adjacent so mwcc anchors them to Ground_803DFEA8 instead of synthetic .data.0. Or refactor so the OSReport pipeline uses an inline local pointer that pins the anchor reg. Alternatively, keep current source and accept this as data-anchor false-positive; permuter --keep-prob may resolve register cascade once anchor difference is masked.

