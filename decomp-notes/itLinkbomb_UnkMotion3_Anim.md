---
function: itLinkbomb_UnkMotion3_Anim
tu: src/melee/it/items/itlinkbomb.c
headline: regalloc + r30-r31-swap
tags: [regalloc, r30-r31-swap, permuter-territory, fuzzy-vs-strict]
---
## itLinkbomb_UnkMotion3_Anim (`src/melee/it/items/itlinkbomb.c`) — regalloc + r30-r31-swap

- **Tags:** `regalloc`, `r30-r31-swap`, `permuter-territory`, `fuzzy-vs-strict`
- **Best fuzzy:** 83.56%
- **Diagnosis:** 5 mismatches at 98.4%: article ptr uses r30 (callee-save) in base vs r4 (temp) in target; this shifts item-inside-if from r30 (target) to r31 (base); plus one addi-r3-r28-0 vs mr-r3-r28 for the second it_80272C6C call. Source shape matches upstream matched version exactly.
- **Tried:** (1) Removed Article* article variable, computed attrs via ip->xC4_article_data->x4_specialAttributes — reduced to 3 callee-saves, everything shifted by 1 register (worse). (2) Added ip-NULL dead check instead of article-NULL check — same 5 mismatches but ip now in r30 instead of article. (3) Moved dead checks before inline — eliminated early variable loads entirely (much worse). Source structure matches upstream matched version; all remaining diffs are register allocation.
- **Likely fix:** Permuter needed: force article to use volatile r4 instead of callee-save r30 (possibly via different variable ordering or dead-check placement), and fix addi vs mr for the it_80272C6C call in the second inline. Upstream has this as matched with identical source — may be a build-config or linker difference causing local 98.4% vs upstream 100%.

