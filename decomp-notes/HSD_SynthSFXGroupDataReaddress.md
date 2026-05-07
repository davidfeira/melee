---
function: HSD_SynthSFXGroupDataReaddress
tu: src/sysdolphin/baselib/synth.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling]
---
## HSD_SynthSFXGroupDataReaddress (`src/sysdolphin/baselib/synth.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`
- **Best fuzzy:** 94.0984%
- **Diagnosis:** At 97.3% (18 mismatches) after splitting the p-advance into two steps (count<<6 then +0x10). All remaining mismatches are a pure r3/r4/r5 swap: compiler emits i=r5, count=r3, q=r4 but target wants i=r4, count=r5, q=r3. Also causes base to use mr./r0 idiom for count-to-CTR and r3 as temp for p-advance, while target uses cmpwi/mtctr directly and updates r29 in-place.
- **Tried:** (1) swapped q=p before count=p[2]: no effect. (2) changed count=p[2] to count=q[2]: no effect. (3) split p=(u8*)p+(count<<6) then p=(u8*)p+0x10: fixed the structural DIFF_INSERT/DIFF_DELETE, improved from 94.1% to 97.3%. (4) register keywords on q/i/count: no effect. CodeWarrior ignores register hints for these variables.
- **Likely fix:** Permuter needed to swap r3/r4/r5 allocation for i/q/count triple. The split p-advance is now in source and structurally correct. Remaining 18 mismatches are pure regalloc shuffles.

