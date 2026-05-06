---
function: grKongo_801D7BBC
tu: src/melee/gr/grkongo.c
headline: permuter-queued + r30-r31-swap
tags: [permuter-queued, r30-r31-swap, sdata2-named-floats, frame-size, permuter-territory]
---
## grKongo_801D7BBC (`src/melee/gr/grkongo.c`) — permuter-queued + r30-r31-swap

- **Tags:** `permuter-queued`, `r30-r31-swap`, `sdata2-named-floats`, `frame-size`, `permuter-territory`
- **Best fuzzy:** 96.8166%
- **Diagnosis:** Source-shape match at 96.64% / 54 mismatches. Real diffs are register-allocation cascade (gp/var_r31 r30↔r31 swap), 8-byte frame-size diff (target 0x38 vs base 0x30, fctiwz spill site), 2 fmuls/fmadds operand-order swaps, and known sda2 named-float vs anon @180/@244 false-positive class shared with grKongo_801D55D8. No remaining structural diffs in control flow, FP math, or symbol references.
- **Tried:** V1 (86%): initial draft with shared temp_f3/temp_f4 hoisted unk10/unk18 into callee-saved regs. V2 (96.64%): inlined unk10/unk18 reads, split unk10*unk18 into named prod, isolated HSD_Randf() result into block-local temp before xE4 store to drop unnecessary f30 hoist of unk0. Reordered local declarations (var_r31 before gp) — no effect on r30/r31 assignment.
- **Likely fix:** Permuter cluster: register allocation noise + 2 commute swaps + frame-size flip should resolve in standard permuter run. Anon sda2 floats (@180=0.0f, @244=1.0f) vs named grKg_804DAFA0/A4 is the same TU-wide false-positive class noted in grKongo_801D55D8.md — worth landing additional sibling functions in this TU first to shift sda2 anchor allocation.

