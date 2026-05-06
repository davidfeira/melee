---
function: grPura_80212EF4
tu: src/melee/gr/grpura.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc]
---
## grPura_80212EF4 (`src/melee/gr/grpura.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`
- **Best fuzzy:** 1.96078%
- **Diagnosis:** 89.80% (26 instr off): two source-shape attempts converged on jobjs[i]/structs[i] indexing through (T**)((s8*)gp+0xC4) and gp+0x128 casts, giving a clean for-loop over 25 entries with grPura_unk128 holding x8 (flag) and x10 (Vec3). Remaining diffs are: (a) stack frame 0x30 vs target 0x28 — target packs Vec3 at sp+0xC, my base at sp+0x10, +8 wasted bytes; (b) target maintains TWO running pointers r30 and r31, both initialized to gp+slwi(i,2)/gp+0 and both incremented by 4 each iter — r30 used ONLY for the JObj load 'lwz r3, 0xc4(r30)' while r31 is used for both the C4 NULL test and the 0x128 NULL test/load; my single-base version uses r31 alone, so one redundant pointer stream is missing. Tried a second shape with explicit 'HSD_JObj** p = &jobjs[i]; p++; i++;' — regressed to 72% (compiler used stmw r27 with a 0x38 stack). Pattern looks like permuter-friendly territory: needs either a structural source change to introduce the dual-pointer stride that mwcc canonicalizes, or accept as the same 'extra mov via r0 / dual-pointer' compiler-quirk class noted in the sibling grPura_80212FC0/80213030 entries (same TU, same iterate-by-4-bytes-into-Ground pattern).

