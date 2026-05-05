---
function: grCastle_801CF308
tu: src/melee/gr/grcastle.c
headline: permuter-false-positive + sdata-symbols-missing
tags: [permuter-false-positive, sdata-symbols-missing, regalloc]
---
## grCastle_801CF308 (`src/melee/gr/grcastle.c`) — permuter-false-positive + sdata-symbols-missing

- **Tags:** `permuter-false-positive`, `sdata-symbols-missing`, `regalloc`
- **Best fuzzy:** 99.5055%
- **Diagnosis:** 99.21% strict, 24 mismatches: 16 reloc-name false positives (sdata2 float refs grCs_804DAE30/48/1C/50/54/58 + sdata string refs grCs_804D45D0/D8), 7 regalloc spread (var_r6 lives in r5 in base vs r6 in target; gp lives in r31 in base, in r5+r31 in target via extra mr), and 1 truly extra 'mr r31, r5' instr at offset 8192 (gp loaded into r5 first then moved to r31, base loads gp directly into r31). The named sdata symbols exist in symbols.txt but base.c references them as inline literals (0.0f, 1.0f, -1.0f, 4.0f, 2.0 double, string '%d' etc) which mwcc deduplicates to anonymous @N@sda21. To match the named refs would require introducing extern-named globals shared across TU — extern/data-symbols convention work, not in-function source reshape.
- **Tried:** reviewed source structure (switch on gp->gv.castle5.xC4 with cases 1/2/3/4/5, sets var_r6=1, then post-switch if(var_r6) block calls lb_8000B1CC + HSD_JObjSetTranslate + HSD_JObjGetRotation + HSD_JObjSetRotation). Single mr r31, r5 cannot be cured by source reshape since base already does the cleaner thing — would need permuter regalloc shuffling, but permuter scorer treats the 16 false-positive sdata mismatches as equivalent post-link bytes, so it would report 'matched' while report.json fuzzy still ~99.5% — classic permuter-false-positive class.
- **Likely fix:** introduce named sdata2 float/double externs (grCs_804DAE30 = 1.0 double-anchored, etc) and a named string global for grCs_804D45D0/D8, all referenced from this TU. This is extern/.h convention work spanning the file (or possibly cross-TU). Without those names matching, report.json will keep flagging the 16 reloc symbol diffs even if the permuter says matched.
