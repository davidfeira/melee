---
function: powi
tu: src/melee/lb/lb_00CE.c
headline: mwcc-loop-opt + permuter-plateau
tags: [mwcc-loop-opt, permuter-plateau]
---
## powi (`src/melee/lb/lb_00CE.c`) — mwcc-loop-opt + permuter-plateau

- **Tags:** `mwcc-loop-opt`, `permuter-plateau`
- **Best fuzzy:** 77.973%
- **Diagnosis:** Target uses mwcc CTR-loop optimization (mtctr+bdnz) for both inner loops (8x mullw and remainder mullw). Base codegen uses subic.+bne. Source-shape do{}while(--var!=0), do{var--}while(var!=0), and do{...}while(var!=0) all produce identical non-CTR codegen. for(;var!=0;var--) variant produces dramatically worse (96 mismatches, 0%) because mwcc partially unrolls the body. Permuter has plateaued at score=665 (lowest output drops the inner do-while entirely and changes loop condition from <exponent to <remaining post-subtract — semantically broken; this is MSL-style libc helper, can't accept that).
- **Tried:** (1) do{...}while(--iters!=0) predecrement form — same 11 mismatches as baseline, no codegen change. (2) for(;iters!=0;iters--){} explicit for-loop — 0% match, 96 mismatches; mwcc partially unrolls or restructures.
- **Likely fix:** Either accept the non-matching codegen (semantic equivalence holds), or find an mwcc CTR-loop trigger pattern. Possible angle: investigate -funroll/-O flags for this TU; check if neighbor functions in lb_00CE.c (expf/powf) get CTR loops to confirm mwcc is willing to emit bdnz here. The 11-mismatch diff is pure register-ordering+CTR codegen; semantics are fully matched. May be permuter-false-positive class if the .o links to identical bytes — but report.json fuzzy=77.97% says no.
