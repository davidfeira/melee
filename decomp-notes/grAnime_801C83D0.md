---
function: grAnime_801C83D0
tu: src/melee/gr/granime.c
headline: frame-size + inlining
tags: [frame-size, inlining, regalloc]
---
## grAnime_801C83D0 (`src/melee/gr/granime.c`) — frame-size + inlining

- **Tags:** `frame-size`, `inlining`, `regalloc`
- **Best fuzzy:** 99.8302%
- **Diagnosis:** Thin wrapper calling grAnime_801C8318 compiles at 99.8% (9 mismatches, all stack-frame offsets). CodeWarrior inlines grAnime_801C8318 and produces correct register allocation (r31=jobj, r30=mask, r29=arg2) but a 0x28 frame. Target requires 0x30 (8 bytes larger). Expanding to full inline body changes register allocation (r31=mask, r30=jobj) but still gives 0x28 frame and adds 3 more mismatches in the NULL-path handling. u8 _[8] padding approach in the thin wrapper (to grow frame by 8) was blocked by attempt cap before compile.
- **Tried:** 1) Thin wrapper calling grAnime_801C8318 - 9 mismatches (frame offsets only). 2) Full inline expansion with mask first then jobj - 12 mismatches (frame + NULL-path control flow). 3) u8 _[8] in thin wrapper - not tested (hit attempt cap).
- **Likely fix:** Try u8 _[8] in the thin wrapper - should grow frame from 0x28 to 0x30 while preserving the correct register allocation from the inlined grAnime_801C8318. Reset attempts first with: python tools/permute.py reset-attempts grAnime_801C83D0. NOTE: upstream already marks this as matched - check if their full TU context (they have grAnime_801C752C and grAnime_801C7C1C as stubs which we have implemented) is affecting codegen.

