---
function: grYorster_80202428
tu: src/melee/gr/gryorster.c
headline: r30-r31-swap + sdata2-anonymous-floats
tags: [r30-r31-swap, sdata2-anonymous-floats, sdata2-named-global, regalloc]
---
## grYorster_80202428 (`src/melee/gr/gryorster.c`) — r30-r31-swap + sdata2-anonymous-floats

- **Tags:** `r30-r31-swap`, `sdata2-anonymous-floats`, `sdata2-named-global`, `regalloc`
- **Best fuzzy:** 99.4%
- **Diagnosis:** Two structural blockers: (1) r30/r31 swap throughout — target binds r31<-gp(r4), r30<-fighter_gobj(r6); our build reverses this. Permuter ran 13 iterations, no fix. (2) lfd f1, grYt_804DB700@sda21 vs @216@sda21 — target references the named sdata2 double, our build generates an anonymous literal. Root cause identified: mwcc does NOT coalesce compiler-generated int-to-float anonymous f64 literals (0x4330000080000000) with user-declared 'const f64 grYt_804DB700' globals — they coexist as separate sdata2 entries even with identical values. Attempted: (a) const f64 grYt_804DB700 declaration only — adds named entry at offset 16 but anonymous @230 still appears at offset 40; (b) removed grlib.h (which injects _half/_three doubles via MSL sqrtf inline through grlib.h -> baselib/mtx.h -> MSL/math_ppc.h chain) + declared ALL 8 named sdata2 constants (grYt_804DB6F0 thru grYt_804DB714) — sdata2 first 40 bytes now match target exactly, but anonymous duplicates appear at offsets 40-79; code-level float literals (0.0f, 1.0f, etc.) and int-to-float bias do NOT coalesce with declared named consts.
- **Tried:** (a) const f64 grYt_804DB700 = 4503601774854144.0 at file scope — creates correct named entry at sdata2+16 but anonymous @230 (same value) appears at sdata2+40. (b) Removed grlib.h include (prevents MSL sqrtf _half/_three from polluting sdata2) + declared all 8 named sdata2 consts — first 40 bytes of sdata2 now match target layout perfectly, but 40 anonymous duplicate bytes appear afterwards; net result unchanged at 99.4%/7 mismatches.
- **Likely fix:** The anonymous float/double literals in code must be REPLACED by explicit named constant references (e.g., write grYt_804DB6F4 instead of 1.0f) in grYorster_802022A4, grYorster_8020266C, grYorster_802024F0 — same pattern used in grpura.c (grPu_804DBA58 etc used directly in code). This requires decompiling those neighbor functions with named constants instead of literals. grlib.h removal is also required to avoid _half/_three injection. r30/r31 swap may resolve naturally once sdata2 layout is fixed.

