---
function: grHomeRun_8021EA30
tu: src/melee/gr/grhomerun.c
headline: cross-tu-globals + permuter-false-positive
tags: [cross-tu-globals, permuter-false-positive, tu-wide-data]
---
## grHomeRun_8021EA30 (`src/melee/gr/grhomerun.c`) — cross-tu-globals + permuter-false-positive

- **Tags:** `cross-tu-globals`, `permuter-false-positive`, `tu-wide-data`
- **Best fuzzy:** 99.2%
- **Diagnosis:** 99.2% fuzzy / 98.6% strict, 11 mismatches. 6 are sdata2 named-vs-anon false-positives (target named grHr_804DBC30/38/50/64/68/70@sda21, base anon @298/@299/@303/@204/@300/@301). 5 remaining are register-allocation diffs (fmuls f5/f2 swap, fmuls operand orders, fmul f31 operand order) that cascade from the literal-pool layout differences. Permuter plateau best score=45 found a new_var reordering (assignment-as-expression) that flips one fmul order locally but does not fix named-vs-anon root cause — strict diff unchanged.
- **Tried:** Permuter ran to plateau (best=45 across 4 outputs). Permuter's new_var trick at result /= grHr_804D6AE4 * (...) reorders one expression but is permuter-territory polish, not the cause. Confirmed source has zero grHr_804DBC30/38/50/64/68/70 declarations — these globals must be added as named sdata2 statics in symbol-table order before any regalloc fix can land.
- **Likely fix:** TU-wide sdata2 reconstruction (multi-function refactor, beyond single-function subagent scope). Declare grHr_804DBC30..grHr_804DBC70 as static const float/double sdata2 anchors matching symbols.txt layout, then mwcc emits named lfs <reg>, grHr_804DBC30@sda21 directly and the cascading regalloc diffs should self-resolve. Same blocker family as it_80274DAC, mpGetSpeed, fn_801803FC, un_80317A60.
