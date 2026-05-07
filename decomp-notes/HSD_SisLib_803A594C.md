---
function: HSD_SisLib_803A594C
tu: src/sysdolphin/baselib/sislib.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## HSD_SisLib_803A594C (`src/sysdolphin/baselib/sislib.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 92.5714%
- **Diagnosis:** Single commutative-add operand order mismatch: target 'add r5, r0, r5' vs base 'add r5, r5, r0'. r0=free_cur->size, r5=alloc_cur->size+0xC. Every manual structural rewrite (reordering old_next/new_size, splitting new_size into two statements, hoisting alloc_prev check before size computation) either stays at 7 mismatches or introduces 14+ new mismatches. The upstream form (free_cur->size + (alloc_cur->size + 0xC)) is closest but still yields wrong add operand order. Prior permuter ran 666+min at cluster scale and plateaued at score=10 without resolution.
- **Tried:** 1) new_size = alloc_cur->size + 0xC; old_next = free_cur->data_0; new_size = free_cur->size + new_size — same 7 mismatches (attempt 1). 2) hoisting alloc_prev check to top of if-block + temp_size intermediate — 14 mismatches, breaks condition reg loads at offsets 492-500 (attempt 2, exhausted 2-attempt cap).
- **Likely fix:** Commutative-add operand order cannot be forced manually without breaking surrounding regalloc. Requires permuter breakthrough (resume from score=10 candidate with output-10-1 intermediate decl approach) or accept as structurally blocked.

