---
function: grInishie1_801FC664
tu: src/melee/gr/grinishie1.c
headline: sdata2-named-floats + sdata2-float
tags: [sdata2-named-floats, sdata2-float, permuter-false-positive, frame-size, regalloc, paired-siblings]
---
## grInishie1_801FC664 (`src/melee/gr/grinishie1.c`) — sdata2-named-floats + sdata2-float

- **Tags:** `sdata2-named-floats`, `sdata2-float`, `permuter-false-positive`, `frame-size`, `regalloc`, `paired-siblings`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 95.82% match (34 mismatches). Source-shape is correct (state machine on xEE with cases 0/1/2/3 dispatching to FC110, main body, finalizer, FC4A0). Three blocker classes: (1) sdata2 named-float false-positive — target uses named symbols grI1_804DB604 (-30.0f) and grI1_804DB5C8 (0.0f) at 4 sites; base emits anonymous @N@sda21. Same class as sibling 801FC4A0 (already logged 99.82%). (2) Stack frame is 0x40 in base vs 0x50 in target — target has extra 16 bytes. Vec3 locals reordered: target sp18@0x18, sp24@0x24 (declared order); base sp24@0xc, sp18@0x1c (reversed) plus fctiwz scratch at 0x28 vs target 0x38. (3) Spurious xoris/lfd/stw/lis/stw/lfd/fsubs u32->f64 conversion sequence in base around -30.0f load that target lacks — origin unclear, possibly mwcc choosing different conversion path for (s16)f32 cast of unk4C. (4) Register allocation: case 2 second jobj lookup uses r30 in target but base reuses r31 (no longer needs gp).
- **Tried:** Manual attempt 1: Used &gp->gv.inishie1 as vars pointer — produced extra addi r31,r4,0xc4 and offsets relative to vars (0x30 for xF4 etc). 95.20%. Manual attempt 2: Switched to gp->gv.inishie1.X direct member access — eliminated addi indirection, all member offsets now match target (0xee, 0xf4, 0x100, 0x104). Improved to 95.82%. Reused HSD_JObjAddTranslationY/HSD_JObjSetTranslateY inlines from jobj.h — these expand correctly with USER_DEF_MTX (0x800000) / MTX_DIRTY (0x40) / MTX_INDEP_SRT (0x02000000) flag pattern matching target. (s16) cast of f32 grI1_804D69F8->unk4C produces fctiwz/stfd/lwz/sth as expected.
- **Likely fix:** Same blocker class as sibling 801FC4A0: sdata2 named-float pool requires TU-wide named extern decls for grI1_804DB604=-30.0f and grI1_804DB5C8=0.0f to force mwcc to use named symbols. Combined with permuter-false-positive: the linker bytes match for sdata2 pool entries, so permuter scorer sees instant 100% but report.json fuzzy treats the @N vs named symbol mismatch as non-equivalent. Frame size and u32-conversion noise need separate investigation — possibly upstream is built with slightly different inline expansion of the grInishie1_stuff struct unk4C field type (s32 vs f32?). DO NOT dispatch permuter — same false-positive class as sibling.

