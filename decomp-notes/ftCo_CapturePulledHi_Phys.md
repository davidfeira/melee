---
function: ftCo_CapturePulledHi_Phys
tu: src/melee/ft/chara/ftCommon/ftCo_Attack100.c
headline: regalloc + frame-size
tags: [regalloc, frame-size]
---
## ftCo_CapturePulledHi_Phys (`src/melee/ft/chara/ftCommon/ftCo_Attack100.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`
- **Best fuzzy:** 97.9535%
- **Diagnosis:** Frame layout solved with PAD_STACK(0x4) + 3 Vec3 locals (tmp, sp2C, sp20). Stack offsets now match target (sp20@0x20, sp2C@0x2C, tmp@0x38). Remaining 11 mismatches are all register allocation: target uses f5/f3/f1 for diffs and f0/f2 for cur_pos chain; base uses f0/f2/f3 for diffs. Permuter territory; cluster permuter dispatched at 98.14%.
- **Tried:** variant1 PAD_STACK(0x8)+3Vec3=97.95%(off-by-4-stack); variant2 no-tmp PAD_STACK(0x18)=77%(wrong frame); variant3 PAD_STACK(0x4)+3Vec3=98.14%(stack matched); variant4 f32 dx/dy/dz=97.95%
- **Likely fix:** Cluster permuter dispatched at 98.14% with stack offsets correct. Pure register allocation diff.
