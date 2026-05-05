---
function: grStadium_801D2A60
tu: src/melee/gr/grpstadium.c
headline: permuter-false-positive + rodata-typing
tags: [permuter-false-positive, rodata-typing, regalloc]
---
## grStadium_801D2A60 (`src/melee/gr/grpstadium.c`) — permuter-false-positive + rodata-typing

- **Tags:** `permuter-false-positive`, `rodata-typing`, `regalloc`
- **Best fuzzy:** 99.899%
- **Diagnosis:** 4 mismatches: 2 sdata2 named-vs-anonymous float reloc symbol diffs (grPs_804DAEF8@sda21 vs @203@sda21 for 0.0f literal; grPs_804DAF18@sda21 vs @386@sda21 for the int-to-double bias 0x4330_0000_0000_0000 used in s16->float conversion). These are mwcc-internal anonymous float-pool constants with no source-level way to name them; post-link bytes are identical. Plus 2 regalloc diffs (fsubs f1 vs f0 and dependent fcmpo) on the deepest nested condition. Permuter ran 23 outputs all stuck at score=10 (these 4 mismatches). Fuzzy match: 99.899%, strict: 99.798%.
- **Tried:** Reviewed permuter outputs (all output-10-N at same score, only added no-op constructs). Confirmed grPs_804DAEF8/grPs_804DAF18 are orphan named slots in symbols.txt (only referenced from splits.txt boundary, not from any source). Function source structure already matches base.c m2c output.
- **Likely fix:** Either (a) accept as wontfix permuter false-positive — bytes match post-link, or (b) reorder symbols.txt to demote these to anonymous slots, or (c) figure out which other symbol(s) cause mwcc to emit a named const at addresses 0x804DAEF8/0x804DAF18 in the original TU (likely a sibling function in same TU that uses those exact constants via a named extern; if a sibling makes them emit named, this function would too). The 2 regalloc diffs may resolve once the sdata2 layout matches.
