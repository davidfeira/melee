---
function: ifMagnify_802FC3C0
tu: src/melee/if/ifmagnify.c
headline: permuter-queued + permuter-territory
tags: [permuter-queued, permuter-territory, regalloc, frame-size, instruction-scheduling]
---
## ifMagnify_802FC3C0 (`src/melee/if/ifmagnify.c`) — permuter-queued + permuter-territory

- **Tags:** `permuter-queued`, `permuter-territory`, `regalloc`, `frame-size`, `instruction-scheduling`
- **Best fuzzy:** 72.14%
- **Diagnosis:** Source-shape complete and semantically correct (84.57%, 84 mismatches). Remaining diff is register renumbering (r26..r31 vs r27..r31 — one extra callee-saved local), stack frame off by 8 (0x38 vs 0x30), sp10 stack slot at sp+0x18 vs sp+0x10, and struct-copy store scheduling. All classic permuter territory. Target uses 5 callee-saved regs (r27..r31): slot, jobj_root, gobj, &player[slot].gobj, base. Our base uses 6, with one extra long-lived value across both branches of the if/else (likely the slot offset or one of the dst/src/idesc temps). Permuter offline per dispatcher override; queued for next run.
- **Tried:** (1) initial draft with HSD_TObj* tobj field type yielded 68% — wrong dobj chain. (2) Fixed: sp10's u.dobj has imagedesc on dobj->next->mobj->tobj, while tobj field's u.dobj has mat on dobj->mobj->mat (no ->next). Switched to opaque (u8*)entry pointer for player[slot] to match target's r30 = base+slot*0x10+0x14 caching. Now 84.57%.
- **Likely fix:** Permuter should be able to drop one callee-saved local and reschedule struct-copy stores. The slot_offset *0x18 expression is computed twice (once for slot*0x18, once for (slot-1)*0x18) — try expressing as (slot-1)*0x18+0x18 to reuse intermediate. Also try ordering the dst struct-copy as image_ptr first, or splitting into HSD_ImageDesc field assignments instead of *dst = *src. The HSD_Joint*** triple-pointer may also be reducible if ifMagnify struct's joint field type is wrong.

