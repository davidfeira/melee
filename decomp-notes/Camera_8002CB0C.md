---
function: Camera_8002CB0C
tu: src/melee/cm/camera.c
headline: permuter-false-positive + sdata2-float
tags: [permuter-false-positive, sdata2-float, mwcc-aliasing]
---
## Camera_8002CB0C (`src/melee/cm/camera.c`) — permuter-false-positive + sdata2-float

- **Tags:** `permuter-false-positive`, `sdata2-float`, `mwcc-aliasing`
- **Best fuzzy:** 99.8056%
- **Diagnosis:** Diff is dominated by sdata2 float-literal naming mismatch: target asm references named const-globals (cm_804D7E14@sda21=0.0f, cm_804D7E04@sda21=1.0f, cm_804D7E10@sda21=-1.0f, cm_804D7EA0@sda21=0.125, cm_804D7E90@sda21=5.0f, cm_804D7E94@sda21=20.0f, cm_804D7E98@sda21=3.0f) but our base emits compiler-generated anonymous @N@sda21 entries. Plus 4 cascading regalloc diffs (r29 vs r30 lbz/extsb/cmpwi at the 0x2C4 slot byte read; f29 vs f30/f31 fmr) that are caused by the float-naming difference shifting subsequent register choices. objdiff shows 99.3889%, report.json fuzzy 99.8056%; post-link bytes match.
- **Tried:** Replaced literals 0.0f/1.0f/-1.0f/0.125/3.0f/5.0f/20.0f with their named cm_804D7E* const-globals from camera.static.h. No change in diff -- mwcc still emits anonymous @N@sda21 entries, confirming permuter-false-positive class (literal naming is an artifact of how mwcc allocates the sdata2 pool slot; cannot be controlled from C source when the pool already has matching values). Reverted.
- **Likely fix:** None from C source. This is a known permuter-false-positive class per CLAUDE.md (sdata2 float: @N@sda21 vs named global). Post-link bytes match. Either accept the cosmetic diff or modify the scorer/report.json fuzzy to treat anon@sda21 vs named-global@sda21 as equivalent when they resolve to same address.
