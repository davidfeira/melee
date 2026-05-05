---
function: ftKb_SpecialNPe_8010C06C
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c
headline: tu-wide-data + data-symbols-missing
tags: [tu-wide-data, data-symbols-missing, permuter-false-positive]
---
## ftKb_SpecialNPe_8010C06C (`src/melee/ft/chara/ftKirby/ftKb_SpecialNYs.c`) — tu-wide-data + data-symbols-missing

- **Tags:** `tu-wide-data`, `data-symbols-missing`, `permuter-false-positive`
- **Best fuzzy:** 99.8182%
- **Diagnosis:** Sibling regalloc-pattern fix (((Fighter*) gobj->user_data)->... in if-else branches) RESOLVED 2 of 4 mismatches (r3 vs r31 on 0x2238 loads). Now at 99.8182% with 2 remaining mismatches: lfs f2,ftKb_Init_804D9574@sda21 vs @216@sda21 and lfs f3,ftKb_Init_804D9570@sda21 vs @207@sda21.
- **Tried:** Applied sibling 8010BF90 pattern (commit 238b6b1f1): replaced cached fp with direct ((Fighter*) gobj->user_data)-> access for cmd_vars[0] and fv.kb.hat.kind reads in if-else. Confirmed regalloc half of mismatch fixed; remaining 2 mismatches are float-literal vs named-global symbols (1.0F/0.0F should be ftKb_Init_804D9574/_9570). Sibling-pattern subagent attempt: regalloc fix landed in working tree but NOT yet committed (cant commit-match since not 100%); fix needs to ship together with the broader header/data def work.
- **Likely fix:** Out-of-scope header/data work as previously diagnosed: declare extern f32 ftKb_Init_804D9574 in ftKb_Init.static.h, define f32 ftKb_Init_804D9574=1.0f and ftKb_Init_804D9570=0.0f in appropriate Kirby TU sdata2, then use the named globals instead of literals here. Permuter cannot resolve since report.json fuzzy treats sdata2 symbol names as semantically distinct. Recommend mama Claude land the regalloc fix (already in working tree) + header/data fix in same commit.
