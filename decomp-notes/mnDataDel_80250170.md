---
function: mnDataDel_80250170
tu: src/melee/mn/mndatadel.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, struct-split, tu-wide-data]
---
## mnDataDel_80250170 (`src/melee/mn/mndatadel.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `struct-split`, `tu-wide-data`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 69% match, 66 mismatches, semantically correct. TU-wide struct-split blocker: target asm splits mnDataDel_803EF870 into three .data symbols (0x30 + 0xC + 0x1DC, the last with format strings/index data) but current source has it as a single 0x70 .bss struct (used by sibling fns x3C/x40 fields). Function correctly accesses (u8*)&mnDataDel_803EF870 + 0xA0..0x1F0 to reach format strings inside what should be mnDataDel_803EF8AC (separate .data symbol). Required source-level rewrite to relayout TU-wide data: split mnDataDel_803EF870 into init'd .data + add mnDataDel_803EF8AC + add mnDataDel_804A0918/_804A0928 in .bss. Even with that, remaining 66 mismatches are pure register allocation: target uses 4 callee-saved regs (stmw r27 = stw r28-r31), mine uses 5; target keeps mnDataDel_804A0918@l in caller-saved r4, mine in callee-saved r28; target uses lbzu r0,mn_804A04F0@l(r3) post-update single instruction, mine uses lis+addi+lbz. All scheduling/regalloc differences. Permuter-friendly once data layout is fixed (or as-is, may match if scheduler permutes regs).

