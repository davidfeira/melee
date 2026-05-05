---
function: HSD_CObjGetViewingMtxPtr
paired_with: [HSD_CObjGetInvViewingMtxPtr]
tu: src/sysdolphin/baselib/cobj.c
headline: paired frame-size
tags: [stack-offset, frame-size, paired-siblings]
---
## HSD_CObjGetViewingMtxPtr + HSD_CObjGetInvViewingMtxPtr (`src/sysdolphin/baselib/cobj.c`) — paired frame-size

- **Tags:** `stack-offset`, `frame-size`, `paired-siblings`
- **Best fuzzy:** 99.89% (Opus subagent — escalated, no commit)
- **Diagnosis:** Frame size delta — target wants `0x60`, base produces `0x48` (24 bytes short). All 11 mismatches are stwu / r31-save / Vec3-offsets shifted by `0x18`. Instruction count + opcodes already match — mwcc inlines `HSD_CObjSetupViewingMtx` correctly, just under-reserves stack by 24 bytes.
- **Tried:** manual inline of SetupViewingMtx body (regressed — mwcc also inlined `HSD_CObjGetUpVector`); 2 unused `Vec3 dummy` locals (frame grew to 0x60 but real Vec3 live locals stayed at low offsets, dummies took the high slots — 6 mismatches remained). Both reverted.
- **Likely fix:** an originally-referenced "unused" local that escapes DCE, or `FORCE_PAD_STACK_*` macro variant.
- **Sibling:** `HSD_CObjGetInvViewingMtxPtr` has identical 0x48-vs-0x60 frame diff — same fix should apply.
