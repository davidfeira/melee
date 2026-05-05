---
function: grIceMt_801F71E8
tu: src/melee/gr/gricemt.c
headline: TU-wide problem
tags: [tu-wide-data]
---
## grIceMt_801F71E8 (`src/melee/gr/gricemt.c`) — TU-wide problem

- **Tags:** `tu-wide-data`
- **Best fuzzy:** 99.95% (Opus subagent, attempted gr/ pattern, no improvement)
- **Diagnosis:** NOT a single-function fix. The whole TU has ~1.1KB of missing data symbols — `grIm_803E40B0` should span 0x494 bytes (target) but source has only 30 bytes. This pushes ALL downstream symbols (`grIm_803E4544`, `grIm_803E4718`, format strings, etc) to wrong offsets, rippling through 20+ functions in this TU that are all below 100%.
- **Likely fix:** wholesale data section RE — populate `grIm_803E40B0` (s16 array per usage pattern), `grIm_803E4544` (0x1B4 bytes of s16 indices), and the actual StageData fields. Single-function attempts here are doomed; needs a multi-function effort.
