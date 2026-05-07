---
function: mnEvent_8024D15C
tu: src/melee/mn/mnevent.c
headline: frame-size + regalloc
tags: [frame-size, regalloc, stack-offset, sdata2-float, varargs-cr1eq]
---
## mnEvent_8024D15C (`src/melee/mn/mnevent.c`) — frame-size + regalloc

- **Tags:** `frame-size`, `regalloc`, `stack-offset`, `sdata2-float`, `varargs-cr1eq`
- **Best fuzzy:** 57.6889%
- **Diagnosis:** Frame is 0x80 in base vs 0xC8 in target (0x48 excess). Target uses stmw r23 (9 callee-saved GP regs r23-r31) but base only uses stmw r24 (8 regs). Target has ~0x50 bytes of param save area (sp+0x08 to sp+0x57) which is 20 word slots — unusual and likely related to HSD_SisLib_803A6B98 varargs call with crset cr1eq (FP shadow mode). Base generates only 8 param slots (minimum). Unknown 8-byte gap at sp+0x74-0x7B between Vec3 pos2 and Vec3 pos not explained by named f32 variables (would cause f30 save), alignment, or double temp. The int-to-float double trick (xoris/stw/lis/stw/lfd/fsubs) appears at both the pos.y update and pos2.y update sites as expected. sdata2-float false positives: assert strings @197/@198@sda21 vs mnEvent_804D5030/5038@sda21. Same class of frame-size/stack-offset blocker as sibling mnEvent_8024E524 (which is stuck on identical issues). Both attempts scored below 75%.
- **Tried:** Attempt 1: Vec3 pos/pos2 + gobj_slot/text_slot/icon_slot as explicit pointer vars, y_a/y_b as named f32 temporaries — caused f30/f31 pair save, 73.76% match. Attempt 2: Reverted y_a/y_b to inline HSD_JObjGetTranslationY calls to avoid f30 save — 57.11% match (worse, extra store sequence appeared from HSD_JObjGetTranslation2 inline). Both blocked by frame-size mismatch and 9th callee-saved register.
- **Likely fix:** The 0x50 param save area is the root cause; it may require adding a call that consumes 20 register arg slots (e.g. a function with many float args that shadow GPR slots), or restructuring so MWCC expands the outgoing param area. The 9th callee-saved GP register (r23) might appear if a local variable lives across more function calls. The gap at sp+0x74-0x7B may resolve once the frame size is correct. Since sibling mnEvent_8024E524 has identical structural blocker, the fix for one likely fixes the other.

