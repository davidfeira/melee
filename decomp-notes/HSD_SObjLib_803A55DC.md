---
function: HSD_SObjLib_803A55DC
tu: src/sysdolphin/baselib/sobjlib.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, float-literal, frame-size]
---
## HSD_SObjLib_803A55DC (`src/sysdolphin/baselib/sobjlib.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `float-literal`, `frame-size`
- **Best fuzzy:** 99.8378%
- **Diagnosis:** 99.84% fuzzy. 21 mismatches break into two classes, both NOT permuter-fixable: (1) sdata2 float-literal naming: target loads f30 from named HSD_SObjLib_804DEA98 (=2.0f) and f1/f2 from named HSD_SObjLib_804DEA78/EAA0 (4330... u16->float biases), but base emits anonymous @100/@102/@104 because this TU's named sdata2 globals are not defined in source. The TU's sdata2 range 0x804DEA70-0x804DEAA8 (0x38 bytes, 11 globals) is currently empty in source — only 0x18 of anonymous literals. (2) Frame size +4: base frame is 0x94 vs target 0x90, shifting all local offsets by +4. Likely caused by an extra spill slot from anonymous-vs-named float pool layout. (3) Far value bug: source has far_val=0.5F but EA98 holds 2.0f — confirmed via target sdata2 .float 2.
- **Tried:** Reordered locals so Scissor viewport/scissor are declared before Vec3 eye/interest — this normalized the stack-offset diff from a region-swap into a uniform +4 shift, suggesting the new ordering matches target. Did NOT change match% (still 99.84% fuzzy) since the underlying cause is the missing TU-wide sdata2 globals.
- **Likely fix:** TU-wide change: define HSD_SObjLib_804DEA70 (0.0f), EA74 (1.0f), EA78 (4330000000000000 double), EA80/EA84/EA88/EA8C/EA90 (4-byte data — see asm), EA94 (0.5f), EA98 (2.0f), EAA0 (4330000080000000 double) as static const file-scope sdata2 globals in sobjlib.c, matching the target sdata2 layout from build-linux/GALE01/asm/sysdolphin/baselib/sobjlib.s lines 1457-1515. Then change far_val=0.5F to far_val=2.0F (or reference HSD_SObjLib_804DEA98 directly). This will require coordinated edits across all sobjlib.c functions that currently use anonymous float literals. Frame +4 should resolve once the float pool is correctly named.
