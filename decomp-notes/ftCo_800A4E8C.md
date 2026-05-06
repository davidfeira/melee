---
function: ftCo_800A4E8C
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-territory + regalloc
tags: [permuter-territory, regalloc, r30-r31-swap, branch-pattern]
---
## ftCo_800A4E8C (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-territory + regalloc

- **Tags:** `permuter-territory`, `regalloc`, `r30-r31-swap`, `branch-pattern`
- **Best fuzzy:** 88.589%
- **Diagnosis:** Source structurally complete: iterates fighters, blast-zone gate, IsAlly, 4-flag continue, inlineD1, 3D distance to pos arg, sqrtf__Ff. 88.6% match (77 mismatches). Used inlineD0/inlineD1/ftCo_IsAlly_dontinline to force out-of-line calls (matches sibling ftCo_800A4A40 pattern); without those wrappers MWCC inlined static helpers and dropped to 54%. Remaining diffs: (a) full register permutation across all GPRs (target=r25..r31 vs base=r25..r31 different roles), (b) base stack frame -0x50 vs target -0x68 (fewer spill slots — likely from || flag chain compressing the bool var), (c) one branch-inversion at the x2219_b1/x2164/x2168 if-else chain. The flag chain in target uses explicit var=1/var=0 ladder (m2c shows it); my source uses ||. Permuter should resolve regalloc easily; flag-chain may need branch-pattern shuffling. Permuter offline; queued.

