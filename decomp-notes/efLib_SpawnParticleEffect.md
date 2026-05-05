---
function: efLib_SpawnParticleEffect
tu: src/melee/ef/eflib.c
headline: mwcc-aliasing + header-prototype
tags: [mwcc-aliasing, header-prototype, upstream-regression]
---
## efLib_SpawnParticleEffect (`src/melee/ef/eflib.c`) — mwcc-aliasing + header-prototype

- **Tags:** `mwcc-aliasing`, `header-prototype`, `upstream-regression`
- **Best fuzzy:** 99.8384%
- **Diagnosis:** Single-instruction near-miss: base emits 'extsb r3,r3' before final hsd_8039EFAC call; target has no extsb. Cause: another agent changed hsd_8039EFAC prototype in src/sysdolphin/baselib/particle.h from 's32 linkNo' to 's8 linkNo' (uncommitted, in working tree). Original target was compiled with s32 linkNo prototype, so caller passed chk full-word with no extsb. With s8 in the header now, mwcc emits extsb on the fall-through merge path (chk = 0 default vs chk = 1 from cases 0xFC/0xFF/0xF7/0x7918). Other EFAC call sites in this TU don't show extsb because their chk is a known-byte expression (e.g. 'srwi r0,r0,31' produces a 0/1 already).
- **Tried:** (1) Inlined the chk=1 cases into per-case calls with literal 1 -> 35 mismatches (structurally wrong, reverted). (2) Added (s32) cast on EFAC arg -> identical 1 mismatch (cast no-ops because callee param is s8). Hit 2-variant cap.
- **Likely fix:** Revert the particle.h prototype change for hsd_8039EFAC back to 's32 linkNo' (matches original target compile). The s8 change is what introduced the regression - it likely fixed a different function elsewhere but broke this one. Mama Claude needs to decide: keep s8 (and accept this near-miss) or revert and find another fix for whatever needed s8.
