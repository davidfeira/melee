---
function: itPikachuthunder_UnkMotion2_Anim
tu: src/melee/it/items/itpikachuthunder.c
headline: cross-tu-globals + tu-data-osreport
tags: [cross-tu-globals, tu-data-osreport, permuter-false-positive]
---
## itPikachuthunder_UnkMotion2_Anim (`src/melee/it/items/itpikachuthunder.c`) — cross-tu-globals + tu-data-osreport

- **Tags:** `cross-tu-globals`, `tu-data-osreport`, `permuter-false-positive`
- **Best fuzzy:** 99.4298%
- **Diagnosis:** 99.43% fuzzy / 99.30% strict, 11 mismatches at addresses 1500-1652 in the inlined itPikachuthunder_UnkMotion2_UpdateScale body. Target binary anchors float/double constants via named sdata2 symbols it_804DCFA0 (1.0f), it_804DCFA4 (10000.0f), it_804DCFA8 (double 4.503e15 bias for fctiwz), it_804DCFB0 (0.01f). Base mwcc generates anonymous compiler-pool literals @181/@283/@284/@289 instead. Symbols exist in config/GALE01/symbols.txt:33196-33199 but are not declared in src/melee/it/items/itpikachuthunder.c. Function source is structurally correct (the small _Anim body reaches 100%; all mismatches are inside the inlined UpdateScale + ScaleCall + pika_scale calls which use literal 1.0f / 10000.0f / 0.01f). Same family as it_80274DAC, mpGetSpeed, fn_801803FC, lbColl_800077A0 reloc-symbol false-positives.
- **Tried:** Manual diff inspection only. No source-shape attempts; per Permuter Boundary, permuter is contraindicated for sdata2-anchor false positives (the target uses named it_* anchors, base uses anonymous @N entries, post-link bytes match but objdiff strict/report.json fuzzy flags the symbol-name divergence). Compact-brief recommended match-attempt but the brief misclassified 8 of 11 mismatches as 'real' when they are actually all reloc-symbol false-positives.
- **Likely fix:** TU-wide multi-symbol refactor in itpikachuthunder.c: declare static const float it_804DCFA0=1.0f; it_804DCFA4=10000.0f; static const double it_804DCFA8=4503599627370496.0; static const float it_804DCFB0=0.01f; (or equivalent extern decls if the symbols are defined in a sibling TU per splits.txt). Then replace the literal 1.0f / 10000.0f / 0.01f references inside pika_scale and itPikachuthunder_UnkMotion2_UpdateScale with the named symbols. Need to verify sdata2 ordering — surrounding symbols include it_804DCF98 (already used for 0.0f compare), it_804DCF9C, it_804DCFC0/C4 (used elsewhere in TU). May also need to add the corresponding sda21 string-pool/__assert anchors. Multi-symbol cross-function refactor — beyond single-function subagent scope.
