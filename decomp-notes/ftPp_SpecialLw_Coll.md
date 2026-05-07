---
function: ftPp_SpecialLw_Coll
tu: src/melee/ft/chara/ftPopo/ftPp_SpecialS.c
headline: permuter-false-positive + sdata2-float
tags: [permuter-false-positive, sdata2-float, sdata2-named-floats]
---
## ftPp_SpecialLw_Coll (`src/melee/ft/chara/ftPopo/ftPp_SpecialS.c`) — permuter-false-positive + sdata2-float

- **Tags:** `permuter-false-positive`, `sdata2-float`, `sdata2-named-floats`
- **Best fuzzy:** 99.8814%
- **Diagnosis:** 99.66% match (4 mismatches). All 4 remaining diffs are sdata2 float symbol mismatches: target uses named globals ftPp_Init_804D9890@sda21 (0.0f, 3x) and ftPp_Init_804D9894@sda21 (1.0f, 1x) but base emits anonymous @212@sda21 and @306@sda21. Post-link bytes are identical. Permuter scorer treats as equivalent so running permuter would return 'already 100%'.
- **Tried:** 1) Original source (3-register r29/r30/r31 allocation): 94.2%, 15 mismatches. 2) Moved fp declaration out of if-block and used GET_FIGHTER(gobj) before Land inline, then fp=GET_FIGHTER(gobj) after. Added PAD_STACK(8) for correct frame size. Result: 99.66%, 4 mismatches. All remaining diffs are sdata2 named-float reloc symbols.
- **Likely fix:** The named globals ftPp_Init_804D9890 and ftPp_Init_804D9894 are static float globals in ftPp_Init.c (at BSS or sdata2 region) that hold 0.0f and 1.0f respectively. If declared and exposed via header, referencing them directly in the C source would produce exact symbol name matches. Alternatively this is a tooling gap: report.json fuzzy matching does not treat @N@sda21 and named@sda21 as equivalent.

