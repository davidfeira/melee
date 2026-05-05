---
function: grBigBlueRoute_8020DD64
tu: src/melee/gr/grbigblueroute.c
headline: regalloc + permuter-false-positive
tags: [regalloc, permuter-false-positive]
---
## grBigBlueRoute_8020DD64 (`src/melee/gr/grbigblueroute.c`) — regalloc + permuter-false-positive

- **Tags:** `regalloc`, `permuter-false-positive`
- **Best fuzzy:** 97.9825%
- **Diagnosis:** 17 mismatches all pure regalloc swap: target uses f0/f1 for compare/store of constants and lfs of v->\{x,y,z\}, base uses f3/f2. Pattern: lfs fX,0(r31); lfs fY,@sda21; fcmpo fX,fY; stfs fY,0(r31). Three repetitions for x/y/z fields. No structural difference; m2c-style early-return rewrite produced identical mismatch count. Permuter ran extensively (best score 75 across many outputs) but only made progress via semantically-broken transformations (replacing constants with variables) -- legitimate regalloc flip f0/f1 <-> f3/f2 isn't reachable from any source-shape change, since the if/else chain pattern forces mwcc into one canonical reg choice.
- **Tried:** if/else chain (current) and m2c early-return shape both emit identical 17-mismatch pure regalloc diff. Permuter outputs at score 75-115 all exploit illegitimate substitutions.
- **Likely fix:** Either (a) callers/inlining context affects mwcc's scratch register selection -- check if grBb caller uses f0/f1 first, forcing this fn to use f3/f2; or (b) accept that this needs upstream context (caller TU layout) to match, similar to other regalloc-only stuck cases.
