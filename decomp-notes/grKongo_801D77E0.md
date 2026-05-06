---
function: grKongo_801D77E0
tu: src/melee/gr/grkongo.c
headline: permuter-territory + sdata2-named-floats
tags: [permuter-territory, sdata2-named-floats, float-regalloc]
---
## grKongo_801D77E0 (`src/melee/gr/grkongo.c`) — permuter-territory + sdata2-named-floats

- **Tags:** `permuter-territory`, `sdata2-named-floats`, `float-regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Source-shape match at 99.07% / 20 mismatches. Real diffs are: (1) 4 sda2 named-float vs anon (@180=0.0f, @433=0.5f, @434=0.0174f) — same TU-wide false-positive class noted in grKongo_801D55D8.md and grKongo_801D7BBC.md; (2) 2 fmuls operand-order swaps (fmuls f2,f1,f3 vs f2,f3,f1) on the 0.5*step branches; (3) register allocation cascade in the abs-value zero-test block (target uses f5 throughout, base uses f2/f1 mix), introducing one extra fmr f2,f5. No structural diffs, no FP math diffs. Tried: (a) initial draft using f32* p iterator (98.11%); (b) switched to Ground* q stride 0x10 (98.43%); (c) rewrote limit calc as 0.0174*(unkB8 - 0.0174*unkAC) to get fnmsubs (99.07%); (d) inlined av/av2 negation as in-place v=-v (regressed to 99.03% with frame-size flip 0x30 vs 0x28). Extended grkongo.static.h struct with unkA8/AC/B0/B4/B8.

