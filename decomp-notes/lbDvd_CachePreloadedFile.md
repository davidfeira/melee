---
function: lbDvd_CachePreloadedFile
tu: src/melee/lb/lbdvd.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## lbDvd_CachePreloadedFile (`src/melee/lb/lbdvd.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 99.6241%
- **Diagnosis:** 8 mismatches all r27<->r30 swap. Target: r27=preloadEntry pointer (set once outside loop via 'addi r27, r31, 0x0' = base of preloadCache.entries), r30=loop counter i. Base swaps these (r30=preloadEntry, r27=i). Function declares: int heap; s32 i; PreloadEntry* preloadEntry; PreloadEntry* entry. The preloadEntry/entry aliasing (entry = &preloadCache.entries[index]; preloadEntry = entry) survives the loop and is reused after. mwcc puts the loop counter in lower-numbered saved reg (r27) when it should be in r30.
- **Tried:** V1: moved entry/preloadEntry decls before i (regressed to 32 mismatches at 98.6%, reverted). V2: moved s32 i to last decl position (regressed to 27 mismatches at 98.9%, reverted). Neither decl reorder flipped the saved-reg assignment in the desired direction.
- **Likely fix:** Permuter cluster - pure regalloc r27<->r30 swap. Try perms that introduce extra temp local for the loop entry pointer (entry=&preloadCache.entries[i]) so it gets a different reg than preloadEntry, or fold the preloadEntry alias away to change live ranges.
