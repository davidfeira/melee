---
function: ftCo_CapturePulledHi_Phys
tu: src/melee/ft/chara/ftCommon/ftCo_Attack100.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, frame-size]
---
## ftCo_CapturePulledHi_Phys (`src/melee/ft/chara/ftCommon/ftCo_Attack100.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 98.14%, 11 mismatches all FPR allocation. Frame layout matched (PAD_STACK(0x4) + 3 Vec3: tmp/sp2C/sp20, stwu -0x50, sp20@0x20, sp2C@0x2C). Target uses f5/f3/f1 for diffs and f0/f2 for cur_pos load/add chain interleaved with diff loads; base allocates f0/f2/f3 for diffs sequentially. Pure scheduler/regalloc problem, no structural change available.
- **Tried:** variant1 PAD_STACK(0x4)+3Vec3 tmp pattern=98.14% (matches prior best); variant2 inline expression no-tmp=77.67% (frame collapsed to 0x48, structural regression). Body now committed in TU; partial improvement (0% -> 98.14%) preserved.
- **Likely fix:** Permuter cluster (currently offline). Source is structurally optimal; only register/scheduling permutations remain.

