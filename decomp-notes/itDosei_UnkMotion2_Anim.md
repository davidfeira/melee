---
function: itDosei_UnkMotion2_Anim
tu: src/melee/it/items/itdosei.c
headline: tu-wide-data + sdata2-named-floats
tags: [tu-wide-data, sdata2-named-floats, permuter-false-positive]
---
## itDosei_UnkMotion2_Anim (`src/melee/it/items/itdosei.c`) — tu-wide-data + sdata2-named-floats

- **Tags:** `tu-wide-data`, `sdata2-named-floats`, `permuter-false-positive`
- **Best fuzzy:** 99.8684%
- **Diagnosis:** Two mismatches: (1) 'lfs f0, it_804DC878@sda21' vs base 'lfs f0, @209@sda21' — base emits an unnamed sdata2 0.0f literal instead of using the named volatile-const it_804DC878. (2) 'fmuls f0, f2, f0' vs base 'fmuls f0, f0, f2' — operand swap caused by the same. Root cause is TU-wide: target itdosei.c has named sdata2 globals it_804DC870 (1.0f), it_804DC874 (0.5f), it_804DC878 (0.0f), it_804DC880 (M_PI_2 double), it_804DC888, it_804DC88C, it_804DC890 (M_PI double), it_804DC898, it_804DC8A0 (60.0f). Our source only declares it_804DC878. The inline itDosei_SetFacingAngle uses M_PI_2 macro (1.5707963267948966 double literal), which generates an unnamed @284 sdata2 entry, and the m=it_804DC878 parameter is loaded via a fresh @209 anonymous slot rather than the named symbol. mwcc seems to allocate new sdata2 slots for floats/doubles ahead of the volatile const symbol. Fix likely requires declaring all named globals in itdosei.c and rewriting itDosei_SetFacingAngle inline (and other affected sites) to reference it_804DC880 (M_PI_2) by name and to receive m via a path that survives constant folding. .sdata2 section is at 77.58% match (and .data at 95.1%) — this is the TU-wide data issue, not a single-function issue. Affects at least 11 functions in the TU. UnkMotion0_Anim has 5 same-class mismatches at 99.84%.
- **Tried:** prep+diff inspection, compared base vs target sdata2 layouts, compared matched UnkMotion0_Anim base vs target asm
- **Likely fix:** Declare all named it_804DC87x/it_804DC88x/it_804DC89x/it_804DC8A0 sdata2 globals in itdosei.c (extern or static const, ordering matters for sdata2 layout). Rewrite itDosei_SetFacingAngle and similar inlines to use these named globals instead of literals/M_PI_2. Cross-TU work, needs coordinated edit across 11+ functions and the data section.
