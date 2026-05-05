---
function: Camera_8002FEEC
tu: src/melee/cm/camera.c
headline: regalloc + permuter-tooling-failure
tags: [regalloc, permuter-tooling-failure, sda21-float-collision]
---
## Camera_8002FEEC (`src/melee/cm/camera.c`) — regalloc + permuter-tooling-failure

- **Tags:** `regalloc`, `permuter-tooling-failure`, `sda21-float-collision`
- **Best fuzzy:** 99.4792%
- **Diagnosis:** 6 real mismatches are pure f1<->f2 register swap on (x*x)+(y*y)+(z*z) sqrtf input; 3 false-positive sda21 reloc mismatches (cm_804D7E60/cm_804D7EA8/cm_804D7E14 named globals vs anonymous @N@sda21 literal pool entries). Fuzzy=99.4792%, strict=99.32%. Permuter dispatch failed due to import.py path-style mismatch (ninja command uses backslashes 'src\melee\cm\camera.c' but import.py searches for forward slashes 'src/melee/cm/camera.c').
- **Tried:** Tried restructuring the addition associativity (z*z) + ((y*y) + (x*x)) -- made it worse (10 mismatches, 95.35%). Reverted. Source order of multiplications and loads is already correct -- this is purely register allocation noise on the final fadds chain feeding sqrtf.
- **Likely fix:** Permuter would solve the 6 regalloc mismatches once import.py path-style is fixed. The 3 sda21 mismatches are tu-data-osreport class: named float consts (cm_804D7E60=0.017453292f deg2rad, etc) used here are ALSO defined as globals in camera.static.h and shared across the TU; mwcc CSEs the literal into the named global. Original game .o keeps them as anonymous literal pool entries. Likely unsolvable without restructuring how those float globals are declared TU-wide.
