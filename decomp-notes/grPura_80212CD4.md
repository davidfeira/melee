---
function: grPura_80212CD4
tu: src/melee/gr/grpura.c
headline: regalloc + frame-size
tags: [regalloc, frame-size, mwcc-loop-opt, struct-typing]
---
## grPura_80212CD4 (`src/melee/gr/grpura.c`) — regalloc + frame-size

- **Tags:** `regalloc`, `frame-size`, `mwcc-loop-opt`, `struct-typing`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Structure of init loop and main loop appears semantically correct (parallel arrays jobjs[25] at gp+0xC4 and CmSubject*[25] at gp+0x128; init via 3x unrolled-by-8 + 1 cleanup; main loop walks linked list of HSD_JObj children-of-children and allocates CmSubject per node, copying flags/bounds). Best 70% with simple form. Target uses only 4 saved nonvolatile regs (r28-r31) and 0x40 stack frame; my source produces stmw r27 (5 saved regs) and 0x48 frame, indicating one extra live variable across the calls. Suspect the cleanup loop and main loop should share counter (m2c showed var_r7 reused), or pointer-walk hsd_obj differently to drop one variable.
- **Tried:** (1) Simple jobjs[i]=NULL/subs[i]=NULL loop + idiomatic main loop -> 70% match, structure matches but reg pressure off. (2) Manually unrolled init loop with 8 stores per iter and pointer-walk in main loop -> 50%, made worse.
- **Likely fix:** Source likely uses single counter shared across init and main loop phases (m2c hint: var_r7 used in both phases). Init may need to be 3x do-while with single advancing pointer (single base reg p that walks gp+0,gp+0x20,gp+0x40 with stores at fixed offsets +0xC4..+0xE0,+0x128..+0x144). Main loop's two parallel pointers (r30, r31) both starting at gp suggest source uses one indexed and one pointer-incremented form. May benefit from permuter once base structure right.

