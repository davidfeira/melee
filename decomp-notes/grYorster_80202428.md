---
function: grYorster_80202428
tu: src/melee/gr/gryorster.c
headline: regalloc + float-literal
tags: [regalloc, float-literal, sdata2-named-global]
---
## grYorster_80202428 (`src/melee/gr/gryorster.c`) — regalloc + float-literal

- **Tags:** `regalloc`, `float-literal`, `sdata2-named-global`
- **Best fuzzy:** 99.4%
- **Diagnosis:** Two stable mismatches at 99.3%/99.4% fuzzy: (1) r30/r31 swap on saved args - target binds r31<-r4(gp), r30<-r6(fighter_gobj); our build does opposite. Permuter ran 13 iterations stuck at score=30 (no break). mwcc copy-props local-alias attempts so source-shape rewrites don't affect arg->callee-saved binding. (2) lfd uses 'grYt_804DB700@sda21' (named global, 0x4330000080000000 = int->double magic) in target but '@70@sda21' (anon literal pool) in our build. The named symbol must be declared in the TU's sdata2 to satisfy mwcc's literal-coalescing (used elsewhere in TU at 0x802025A0, 0x802025E0, 0x802026C8 in unmatched neighbor functions grYorster_802024F0/802026C8). Diff with --with-fuzzy reports 99.4%, so this is NOT a permuter false-positive (post-link bytes differ).
- **Tried:** (a) Local-alias 'Ground* gp2 = gp' to extend gp's lifetime - copy-propped away. (b) Local aliases for both gp and fighter_gobj - same, no effect. Permuter cluster ran 13 iterations from 11:38-13:01 all stuck at score=30 producing trivial dead-code transforms (if(!i){}, if(gp&&gp){}, etc) - the regalloc swap and named-literal mismatch are not in permuter's reach without TU-level decl changes.
- **Likely fix:** (1) Resolving named 'grYt_804DB700' likely requires declaring an extern f64 grYt_804DB700 = 0x4330000080000000 (or the equivalent magic-double) in sdata2 in this TU - or it might unblock once neighbor functions grYorster_802024F0 and grYorster_802026C8 (currently inline-asm /// stubs) are decompiled, since those also use grYt_804DB700 and may carry the named decl. (2) The r30/r31 swap might fall out naturally once the lfd issue is resolved (since the mismatched block is around the cast); or it may need other sister functions decompiled to fix register pressure across the TU. Recommend deferring this function until 802024F0/802026C8 are decompiled.
