---
function: gm_8019B8C4_OnEnter
tu: src/melee/gm/gmtou.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, data-symbols-missing]
---
## gm_8019B8C4_OnEnter (`src/melee/gm/gmtou.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `data-symbols-missing`
- **Best fuzzy:** 99.8769%
- **Diagnosis:** 99.876%% fuzzy / 99.108%% strict. All 10 mismatches are pure reloc-symbol class: target uses lbl_803DA0D0@ha+@l with offsets 0x190/0x1A8/0x1B4/0x1CC/0x1E4/0x1FC; base uses .data.0@ha+@l with offsets 0x0/0x18/0x24/0x3C/0x54/0x6C. Post-link bytes are identical (same final address); permuter scorer would treat these as equivalent but report.json strict doesn't. The 6 string literals (ScGamTour_scene_data, TmBox.dat, tournament_box2_array/box3_array/box4_array, SIS_TournamentData) live in .data immediately after struct lbl_803DA0D0 (size 0x184) and should be encoded as part of that aggregate symbol, not as separate string literals.
- **Tried:** Compared diff vs source. Confirmed struct lbl_803DA0D0_t size=0x184 in gm_18A5.static.h; strings used by gm_8019B8C4_OnEnter at offsets 0x190+ are clearly sequential continuation of the same data symbol.
- **Likely fix:** Extend struct lbl_803DA0D0_t in src/melee/gm/gm_18A5.static.h to include trailing string fields (or inline the strings into a wrapper aggregate so all references resolve via lbl_803DA0D0+offset). This is TU-wide and likely affects other gm_18A5 functions that index past 0x184. DO NOT dispatch permuter — scorer treats reloc-symbol mismatches as equivalent but report.json fuzzy does not.
