---
function: grHomeRun_8021C754
tu: src/melee/gr/grhomerun.c
headline: permuter-false-positive + bitfield-reuse
tags: [permuter-false-positive, bitfield-reuse, regalloc]
---
## grHomeRun_8021C754 (`src/melee/gr/grhomerun.c`) — permuter-false-positive + bitfield-reuse

- **Tags:** `permuter-false-positive`, `bitfield-reuse`, `regalloc`
- **Best fuzzy:** 97.6191%
- **Diagnosis:** Target reuses 'li r3, 0x1' loaded for the rlwimi (b5=1 bitfield store) as the immediate argument to grHomeRun_8021EDD4. Source 'stage_info.unk8C.b5 = true; grHomeRun_8021EDD4(1);' emits separate li for the call. Plateau 'output-100-*' all use '(stage_info.unk8C.b5 = 1)' as expression value, but mwcc compiles the assignment-expression by reading the bit BACK from memory (extrwi r3, r0, 1, 29) rather than reusing r3=1. So the permuter's local objdiff scorer reports 100, but real objdiff/report.json scores 97.6% with one extra DIFF_INSERT (extrwi r3, r0, 1, 29). All 6 output-100 candidates exhibit this false-positive pattern (assignment-expr/long long/(0,1) variants all generate the same extrwi).
- **Tried:** 1) grHomeRun_8021EDD4(stage_info.unk8C.b5 = true) -> 97.6% extra extrwi; 2) int tmp; tmp=1; stage_info.unk8C.b5=tmp; grHomeRun_8021EDD4(tmp); -> 96.9% (worse, regalloc shifted to r5); 3) unsigned int new_var; new_var = (stage_info.unk8C.b5 = 1); grHomeRun_8021EDD4(new_var); -> 97.6% same extrwi as variant 1, both with new_var-first and Vec3-first decl ordering
- **Likely fix:** mwcc may need a __asm__ or volatile trick to reuse r3, OR the original source might assign through a u8/bool temp differently. The 'b5' bitfield store via rlwimi inherently materializes 1 in r3 first; need source pattern that lets compiler keep r3 live across the stb. Possibly write through a local 'StageInfo*' alias variable where the compiler can see CSE between the bitfield store and the call argument. None of permuter's 100-score outputs actually match in real objdiff — false positive plateau.
