---
function: grIceMt_801F686C
tu: src/melee/gr/gricemt.c
headline: permuter-queued + data-anchor
tags: [permuter-queued, data-anchor, string-pool, cross-function-rodata]
---
## grIceMt_801F686C (`src/melee/gr/gricemt.c`) — permuter-queued + data-anchor

- **Tags:** `permuter-queued`, `data-anchor`, `string-pool`, `cross-function-rodata`
- **Best fuzzy:** 94.9845%
- **Diagnosis:** 94.52% match, 124 mismatches dominated by base-register pooling. Target asm uses ONE base reg (r31=grIm_803E4068) and accesses both the IceMtRowData[6] table AND the assert string literals (grIm_803E46F8) via offsets +0x690/+0x69c — i.e., mwcc folded the second symbol's @ha load into the first because final layout places them at known relative offsets in the same data section. Base emits TWO separate base reg loads (r30=...data.0 for strings, r31=grIm_803E4068 for table), bumping live-reg count and stack frame from 0x38 to 0x48 (stmw r26 vs stmw r27) and propagating a register-allocation shift downstream (r28 vs r30 for field30/29/28 storage; r29 vs r27 for row_idx). Root cause: grIm_803E4544 (s16[218], 0x1B4 bytes between grIm_803E40B0 and grIm_803E46F8) is declared extern but should be defined here; without it (and likely some other static const data anchoring the assert strings near grIm_803E4068), mwcc cannot prove the relative offset. Caching grIm_803E4068 in a local pointer (attempt 1) had no effect — pooling is data-layout driven, not source-shape. Real fix requires defining grIm_803E4544 and any other gricemt.c-owned data in the right order so the assert strings land at fixed offset from grIm_803E4068. Tagged permuter-queued per offline override; secondary tags reflect the structural data anchoring blocker.

