---
function: grFourside_801F3CC8
tu: src/melee/gr/grfourside.c
headline: permuter-territory + frame-size
tags: [permuter-territory, frame-size, r30-r31-swap, literal-pool, regalloc]
---
## grFourside_801F3CC8 (`src/melee/gr/grfourside.c`) — permuter-territory + frame-size

- **Tags:** `permuter-territory`, `frame-size`, `r30-r31-swap`, `literal-pool`, `regalloc`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 91.3% match, 32 mismatches. Structural state machine matched (4-case switch on fourside2.x0). Three remaining classes of mismatch: (1) stack frame 0x40 vs 0x30 — Vec3 sp24 placed at 0x24 in target vs 0x10/0x14 in base, suggesting target reserves more stack space (maybe extra padding/scratch), (2) r29/r30 swap — target r30=gobj/r29=jobj, base r29=gobj/r30=jobj, just regalloc preference (3) MWCC emits a 'bool var = (x1==2 || x0==0); if (var==0) work' temp pattern in cases 0 and 2 instead of direct ||-short-circuit. Adds 5 instructions per occurrence (li r0,0; b; li r0,1; cmpwi; bne). (4) float literal grFs_804DB51C@sda21 (50.0f) is in named sdata2 pool, base emits @357@sda21 — literal pool dedup didn't share the existing slot. Tried: a+b operand reorder (50.0f+top_offset), no effect on pool slot.
- **Tried:** Two source-shape attempts. (1) initial switch with direct || in if conditions yielded 81%; (2) inverted if-else for cases 0/2 (target uses bgt to skip work block, fall-through is work) yielded 91.3%. Float operand order reorder for the Stage_GetCamBoundsTopOffset+50 expression had no effect.
- **Likely fix:** Permuter run: regalloc swap and frame size are exact permuter territory. The OR-temp pattern may need explicit source bool temp: 'bool blocked = (other_gp->fourside2.x1 == 2) || (other_gp->fourside2.x0 == 0); if (!blocked) { work }' — or possibly using int temp with explicit assignment in if/else. The float pool issue may resolve once frame/regalloc match, or may be a known sdata2-anonymous-floats class needing manual constant declaration.

