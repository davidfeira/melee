---
function: grIceMt_801FA364
tu: src/melee/gr/gricemt.c
headline: permuter-false-positive + tu-data-osreport
tags: [permuter-false-positive, tu-data-osreport, sdata2-named]
---
## grIceMt_801FA364 (`src/melee/gr/gricemt.c`) — permuter-false-positive + tu-data-osreport

- **Tags:** `permuter-false-positive`, `tu-data-osreport`, `sdata2-named`
- **Best fuzzy:** 100%
- **Diagnosis:** 99.94%/1 mismatch (100% fuzzy on report.json). Sole diff: 'lfd f1, grIm_804DB580@sda21' vs 'lfd f1, @782@sda21' — int-to-float magic constant 0x4330000000000000. Target TU has the symbol named (anchored by other refs in same TU); base TU emits anonymous @782. This is the documented tu-data-osreport / sdata2-named-vs-anon false-positive class — permuter cannot fix sdata2 naming. Function is structurally complete with state struct {phase,delay,lerp_count,burst_count,idx,cur} and key trick: ((f32*)((u8*)grIm_804D69F4 + 4))[state->idx] generates target's slwi+add+lfs 0x4(r3) form (not lfsx).

