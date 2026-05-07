---
function: grHomeRun_8021EA30
tu: src/melee/gr/grhomerun.c
headline: sdata2-named-floats + regalloc
tags: [sdata2-named-floats, regalloc, sdata2-float]
---
## grHomeRun_8021EA30 (`src/melee/gr/grhomerun.c`) — sdata2-named-floats + regalloc

- **Tags:** `sdata2-named-floats`, `regalloc`, `sdata2-float`
- **Best fuzzy:** 98.1%
- **Diagnosis:** 4 sdata2-float mismatches: target uses named globals grHr_804DBC64 (70.0f), grHr_804DBC30 (160.0f), grHr_804DBC68 (0.304788 double), grHr_804DBC70 (100.0f) while base generates anonymous @N@sda21 entries. Plus 4 FPR allocation mismatches (f2/f5 swap around the int-to-float region) and 1 fmul operand order swap. The FPR layout cascade is tied to the sdata2 symbol load order: replacing the literals with named globals also disturbs the int-to-float bias load (grHr_804DBC50) register, making things worse (9->13 mismatches).
- **Tried:** Attempt 1: Added extern declarations for grHr_804DBC30, grHr_804DBC38, grHr_804DBC64, grHr_804DBC68, grHr_804DBC70 and replaced all float literals with named globals. This fixed the 4 sdata2 mismatches but introduced 4 new ones (the int-to-float bias grHr_804DBC50 now also mismatches since its FPR changed from f3 to f4 due to reordering). Net result: 13 mismatches vs original 9 — worse.
- **Likely fix:** Need a source expression that simultaneously produces named-global sdata2 loads for the 4 float constants AND keeps the correct FPR assignment for grHr_804DBC50 (int-to-float bias). Might require also declaring grHr_804DBC50 as extern f64 AND using it explicitly. Permuter with sdata2-aware scoring would be needed.

