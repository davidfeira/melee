---
function: itLinkboomerang_UnkMotion3_Anim
tu: src/melee/it/items/itlinkboomerang.c
headline: permuter-false-positive + data-symbols-missing
tags: [permuter-false-positive, data-symbols-missing, regalloc]
---
## itLinkboomerang_UnkMotion3_Anim (`src/melee/it/items/itlinkboomerang.c`) — permuter-false-positive + data-symbols-missing

- **Tags:** `permuter-false-positive`, `data-symbols-missing`, `regalloc`
- **Best fuzzy:** 99.8684%
- **Diagnosis:** 99.74% strict / 99.87% fuzzy with 4 mismatches on 76-instr function. 2 mismatches are reloc-symbol false-positives: target loads HSD_ASSERT(682) message string via named global it_803F696C@ha+@l (declared in symbols.txt as .data:0x803F696C size 0x25 scope:global data:string — the stringified condition '!(jobj->flags & JOBJ_USE_QUATERNION)' from HSD_JObjSetRotationZ inline assert), base emits anonymous @258@ha+@l string literal at the same final address. Post-link bytes match but report.json strict counts symbol mismatch. The other 2 mismatches are pure register-choice noise: target loads rot_z directly into callee-saved f31 ('lfs f31, 0x24(r31); fadds f31, f31, f0'), base loads to scratch f1 then writes f31 ('lfs f1, 0x24(r31); fadds f31, f1, f0'). The fadds result lands in f31 in both. mwcc's choice of source register (f31 vs f1) for the rot_z load is internal — likely driven by whether the value needs to survive a potential __assert call (asserts on a non-taken branch but mwcc may still pessimize). TU has 3 logged stuck siblings — same family.
- **Tried:** V1: inline HSD_JObjGetRotationZ(child) directly into HSD_JObjSetRotationZ call (drop rot_z local) — regressed to 99.58%/5 mismatches; mwcc reordered the loads so 0x24(r31) and 0xf88(r30) swapped order. Reverted.
- **Likely fix:** Two-part: (a) Resolve the it_803F696C named-string false-positive by ensuring the HSD_ASSERT's stringified message is emitted as the named .data global rather than an anonymous @258 — likely requires a TU-wide string table (extern char it_803F696C[]; or splits.txt change). Same family as 3 sibling itlinkboomerang functions logged. (b) The f31/f1 register choice on rot_z load is permuter-territory but not worth dispatching alone — only 2 instructions, the false-positive bound dominates. If the named-string fix lands TU-wide, the 2 register mismatches may resolve via cascading literal-pool layout changes too. Beyond single-function scope; mama Claude or TU-wide refactor required.
