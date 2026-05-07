---
function: gmCamera_801A30E4
tu: src/melee/gm/gmcamera.c
headline: regalloc + bss-anchor
tags: [regalloc, bss-anchor, upstream-regression]
---
## gmCamera_801A30E4 (`src/melee/gm/gmcamera.c`) — regalloc + bss-anchor

- **Tags:** `regalloc`, `bss-anchor`, `upstream-regression`
- **Best fuzzy:** 93.1148%
- **Diagnosis:** Upstream claims 100% match with identical source, but local build produces 93.1% (8 mismatches). Core issue: compiler reloads gmCamera_80479BC8 via lis/addi in the else branch and post-if/else code instead of keeping r29=&gmCamera_80479BC8 alive. Target caches r29=&base, r31=&xC, r28=&x8 and overwrites r29=1 only in the loop; base reloads the BSS address twice. Source code is byte-for-byte identical to upstream/master which reports state=matched.
- **Tried:** 1) Added gmCameraUnkStruct* gcus = &gmCamera_80479BC8.gcus local pointer — made things worse (82.9%, 24 mismatches, wrong register allocation, r28-r31 used instead of r27-r31). 2) Restructured pragma dont_inline block from wrapping gmCamera_801A253C+gmCamera_801A25C8+gmCamera_801A2640 to only wrapping gmCamera_801A2650 (matching upstream) — no change (still 93.1%). Header and data context (gmCamera_803DA630, static.h) already match upstream.
- **Likely fix:** Unknown. Source and context are identical to upstream. Possible cause: subtle CodeWarrior optimizer difference, cross-function register pressure from TU-wide function inlining analysis, or upstream accepted a near-miss. Try: (1) static.h change adding initialization to gmCamera_803DA758, (2) checking if a new CodeWarrior build produces different output, (3) accepting upstream may have been wrong about 100% match.

