---
function: fn_801FC9AC
tu: src/melee/gr/grinishie1.c
headline: tu-data-osreport + cross-tu-globals
tags: [tu-data-osreport, cross-tu-globals]
---
## fn_801FC9AC (`src/melee/gr/grinishie1.c`) — tu-data-osreport + cross-tu-globals

- **Tags:** `tu-data-osreport`, `cross-tu-globals`
- **Best fuzzy:** 99.7812%
- **Diagnosis:** Best fuzzy 99.78%/strict 99.47% with 18 mismatches, all downstream of missing TU-wide sdata2 const declarations. Target grinishie1.o has 12 named sdata2 globals (grI1_804DB5C0..804DB608, mix of f32/f64, totaling 0x50 bytes) emitted as 'g' symbols. Base obj has only TU-local @NNN pool entries. Mismatch breakdown: 4x lfd reloc target=grI1_804DB608@sda21 (the s32->f32 magic cookie 0x4330000000000000) vs base=@840@sda21 (local pool); 14x stack offset deltas (0x30 vs 0x28 frame; 0x2c/0x28 vs 0x24/0x20 stores) - downstream of the magic cookie symbol-class change triggering different scratch slot layout. Function source itself is correct (matches m2c output and grZebes/sibling pattern).
- **Tried:** Manual diff inspection only - no source-shape attempts since the function is structurally correct and per Permuter Boundary 'Do not use permuter for false diffs caused by equivalent BSS/global base symbols'.
- **Likely fix:** TU-wide refactor: declare static const f32/f64 globals matching the 12 named sdata2 entries (grI1_804DB5C0/C4/C8/CC/D0/D4/D8/E0/E8/F0/F4/F8/600/604/608 - some referenced as 1.0f/4000.0f/5.0f in grInishie1_801FA90C, others throughout the TU per asm grep). Same pattern as it_80274DAC and Exception_ReportStackTrace. Beyond single-function scope - mama Claude or human refactor required. Sibling grInishie1_801FA9B4 matched (5b90a7064) by adding StageData/cb-table data declarations; this case needs the float-pool counterpart.
