---
function: ftCo_800AC5A0
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: tu-wide-data + frame-size
tags: [tu-wide-data, frame-size, permuter-false-positive]
---
## ftCo_800AC5A0 (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — tu-wide-data + frame-size

- **Tags:** `tu-wide-data`, `frame-size`, `permuter-false-positive`
- **Best fuzzy:** 96.2979%
- **Diagnosis:** 99.56% match with 26 mismatches: 4 stack store/load offsets (frame is 0x38 in base vs 0x30 in target -> 8-byte ghost slot at 0x10..0x17 between volatile y at 0xC and first stfd) + ~12 sda21 anonymous-vs-named float literal mismatches (target uses ftCo_804D87D8/8808/8830/8870/8874/888C/88C0 from sdata2 named statics shared across the entire ftCo_0A01.s TU; our compile emits anonymous @230/@293/@331/@419/@420/@437/@511 inline). Frame-size diff is consequence of unused 8-byte spill slot that mwcc reserves; tried (1) removing 'bool var_r0' intermediate (broke control flow, dropped to 95.97% with 32 mismatches incl extra DIFF_DELETE), (2) hoisting all locals to function top (no change, still 99.56% same 26 mismatches). The named float symbols in target (size 0x4 floats: 0.0f, 1.0f, 0.00001f, -0.00001f, 127.0f and size 0x8 doubles: 0.5, 3.0) are file-scope statics shared across ALL functions in ftCo_0A01.s.
- **Tried:** removed bool var_r0 intermediate; hoisted all locals to function top
- **Likely fix:** TU-wide refactor: declare named static const f32/f64 at file-scope (or in shared header) for 0.0f, 1.0f, 0.00001f, -0.00001f, 127.0f, 0.5, 3.0 -> these symbols are heavily used across many functions in ftCo_0A01.c so must be coordinated change across the whole TU. Frame-size 8-byte gap likely resolves once the inline literal references are replaced by named-symbol references (mwcc may stop reserving the unused spill slot). Permuter cannot help (sda21 reloc-symbol mismatches are permuter false-positives per CLAUDE.md).
