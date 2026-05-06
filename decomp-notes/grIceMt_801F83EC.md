---
function: grIceMt_801F83EC
tu: src/melee/gr/gricemt.c
headline: header-prototype + header-required
tags: [header-prototype, header-required, regalloc]
---
## grIceMt_801F83EC (`src/melee/gr/gricemt.c`) — header-prototype + header-required

- **Tags:** `header-prototype`, `header-required`, `regalloc`
- **Best fuzzy:** 84.2586%
- **Diagnosis:** Recovered call structure (grIceMt_801F8CDC + 2x grIceMt_801FA500 + grIceMt_801F91EC w/ fn_801F9558 callback) plus rlwimi b0=0 and joint_indices init from grIm_804DB598/59C, taking match from 64.22% to 83.40%. Remaining 68 mismatches are register-allocation cascade: target uses 4 saved regs (r28-r31), base uses 5 (stmw r27, with r30 holding the function-pointer address). Cause: header gricemt.h declares 'int grIceMt_801FA500(HSD_GObj*)' as 1-arg, but asm calls it with 2 args (HSD_GObj*, HSD_JObj*). Workaround uses a local function-pointer cast to int(*)(HSD_GObj*,HSD_JObj*), which forces an indirect call and consumes an extra callee-saved reg, cascading reg usage throughout. Structural fix: change gricemt.h prototype for grIceMt_801FA500 (and likely all other similar 2-arg sites: 801F7F70, 801F8850 share this issue). Same cast pattern is in-use for those siblings (recently added by another agent) at 80.5% match. Header edit out of scope for permuter-attempter; needs Mama Claude follow-up.

