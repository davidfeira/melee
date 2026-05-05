---
function: HSD_CObjSetUpVector
tu: src/sysdolphin/baselib/cobj.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, stack-offset, float-literal]
---
## HSD_CObjSetUpVector (`src/sysdolphin/baselib/cobj.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `stack-offset`, `float-literal`
- **Best fuzzy:** 99.8014%
- **Diagnosis:** 44 mismatches at 99.23% strict / 99.80% fuzzy. Decomposes as: (a) 16 sda21 named-vs-anonymous float literal mismatches (target uses HSD_CObj_804DE478/498@sda21 — file-scope named statics shared across cobj.c TU; base emits @243/@451@sda21 anonymous pool). Same post-link bytes; permuter false-positive class. (b) 20 stack-offset mismatches with uniform 4-byte shift (target=0x40,0x3c,0x38,0x50,0x8c; base=0x3c,0x38,0x34,0x4c,0x88). Frame layout has a 4-byte missing pad below Vec3 v local. (c) 8 'real' addi r29,r30,0xcc + lfs/lwz at r29+0/4/8 — actually identical bytes, classifier counts the named-vs-anon symbol surface twice. Source already minimal: Vec3 v + early-return + flags-branch. No source-shape variants warranted: the named float globals are TU-wide (siblings HSD_CObjGetViewingMtxPtr / roll2upvec already logged with same blocker).
- **Tried:** prep+diff inspection only; no source edits — same blocker class as 3 logged sibling cobj.c functions (HSD_CObjGetViewingMtxPtr/HSD_CObjGetInvViewingMtxPtr frame-size, roll2upvec tu-wide-data). Compact-brief recommended log-stuck-immediately.
- **Likely fix:** TU-wide refactor: declare named static const f32 at file-scope in cobj.c for the constants behind HSD_CObj_804DE478 and HSD_CObj_804DE498 (likely 0.0f / 1.0f / similar — verify by reading lbl_804DE478 + 0x498 in sysdolphin/baselib/cobj.s sdata2). Once the named symbols are introduced, mwcc may also stop reserving the 4-byte pad slot, fixing the stack-offset class as a side-effect (same pattern as ftCo_800AC5A0 tu-wide-data note). Coordinate change across all sibling cobj.c functions sharing these literals. Permuter cannot help (sda21 reloc-symbol mismatches are permuter false-positives per CLAUDE.md).
