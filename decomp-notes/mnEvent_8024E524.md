---
function: mnEvent_8024E524
tu: src/melee/mn/mnevent.c
headline: frame-size + regalloc
tags: [frame-size, regalloc, stack-offset, sdata2-float]
---
## mnEvent_8024E524 (`src/melee/mn/mnevent.c`) — frame-size + regalloc

- **Tags:** `frame-size`, `regalloc`, `stack-offset`, `sdata2-float`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Frame is 0x68 in base vs 0x60 in target. All 4 address-taken HSD_JObj* locals (sp1C/sp20/sp24/sp28) land 0x10 bytes too high (e.g. sp20 at 0x30 vs target 0x20), and stmw r26 is at 0x40 vs target 0x38. Both attempts preserve the same 6 callee-saved regs (r26-r31) and 2 FPRs (f30-f31). The 8-byte frame excess is likely caused by the compiler allocating a larger param-save area or treating named f32 ay/by locals as needing stack slots. Register swap r26<->r27 for jobj/event_idx is also present but is a consequence of the frame mismatch. sdata2-float false positives: 0.0f constant generates @220@sda21 instead of mnEvent_804DC170@sda21, and assert strings generate @197/@198 instead of mnEvent_804D5030/5038 SDA refs.
- **Tried:** Attempt 1: Direct m2c translation with proc as named variable and arr/base in original order. Attempt 2: Removed named proc variable (used inline ->flags_3), swapped arr/base declaration order to match register load order in prologue. Neither fixed the 8-byte frame excess.
- **Likely fix:** Try declaring locals in a specific order that reduces the compiler's local variable area. The 8 extra bytes may be from the f32 ay/by locals taking stack space - try removing them and using HSD_JObjGetTranslationY inline. Or the compiler may need a specific declaration order of the address-taken HSD_JObj* locals. Also verify whether omitting first_event as a named variable (inlining data->first_event in the loop) helps. The sdata2-float mismatches are false positives (post-link bytes match).

