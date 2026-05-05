---
function: lbHeap_80015F3C
tu: src/melee/lb/lbheap.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, permuter-territory]
---
## lbHeap_80015F3C (`src/melee/lb/lbheap.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `permuter-territory`
- **Best fuzzy:** 96.2941%
- **Diagnosis:** 84-mismatch regalloc shift across unrolled init loop. Target frame -0x18 with r29-r31 saved; base frame -0x20 (8 extra stack bytes) same regs saved. Target uses r6/r5/r4 for li(-1)/li(0)/li(1) and threads array address through 'lis r3; addi r0, r3, @l; ...; mr r3, r0' (curious deferred register move). Base uses r4/r3/r0 for li's and addi @l directly into r5. 74/84 are pure regalloc shifts in the unrolled 6x7 store sequence; 1 is the extra 'mr r3, r0' instruction; remaining are stack-offset shifts from the 8-byte frame difference. Source semantics correct (heap_array init + size/type/start computation from lbHeap_803BA380 table).
- **Tried:** V1: split shared 'i' variable into separate 'j' for the init loop (no change, same 84 mismatches). V2: removed prev_idx local, inlined lbHeap_803BA380[i].prev_idx (regressed to 85 mismatches at 95.85%, reverted). Both variants left frame size and the mr r3, r0 quirk untouched.
- **Likely fix:** Permuter (regalloc + scheduling territory). The mr r3, r0 deferred-move pattern suggests a specific liveness/scheduling state mwcc reaches through some interaction of locals; not reproducible by hand. Frame size +8 in base implies an extra spill slot mwcc didn't need in target.
