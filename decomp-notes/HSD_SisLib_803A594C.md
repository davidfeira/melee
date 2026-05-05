---
function: HSD_SisLib_803A594C
tu: src/sysdolphin/baselib/sislib.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## HSD_SisLib_803A594C (`src/sysdolphin/baselib/sislib.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 99.8214%
- **Diagnosis:** Single mismatch at offset 528: target wants 'add r5, r0, r5' (free_cur->size + addi_result), base emits 'add r5, r5, r0'. r0 holds free_cur->size (loaded as 'lwz r0, 0x8(r4)' at offset 516), r5 is the result of 'addi r5, r3, 0xc' where r3=alloc_cur->size. Source is: new_size = alloc_cur->size + 0xC; old_next = free_cur->data_0; new_size += free_cur->size. Permuter already plateaued at score=10 (~666min of cluster runtime; output-10-1 added intermediate decls but didn't reach 0).
- **Tried:** 1) new_size = free_cur->size + new_size (after addi)  2) Single-expression: new_size = free_cur->size + (alloc_cur->size + 0xC). BOTH variants caused MWCC to hoist the lwz of free_cur->size and rearrange registers, yielding 6+ mismatches around offsets 512-560 (lwz reordering, addi r5,r5,0xc instead of addi r5,r3,0xc, store r4 vs r3 to alloc_cur->data_0). The 'r5 += free_cur->size' form via compound-assign is the only known starting point that keeps the structure — only the final add operand order is wrong.
- **Likely fix:** Pure commutative-add register-order issue. Source change cannot reach it without breaking surrounding regalloc. Best path: more permuter wall-clock (current plateau is non-trivial; the score=10 candidate adds intermediate vars that don't survive to 0), OR accept as a known false-positive class if it's actually equivalent post-link. Not recommended for further manual subagent attempts — every structural rewrite tested loses ground.
