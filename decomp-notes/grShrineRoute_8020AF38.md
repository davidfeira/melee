---
function: grShrineRoute_8020AF38
tu: src/melee/gr/grshrineroute.c
headline: regalloc + permuter-blocked
tags: [regalloc, permuter-blocked, varargs-cr1eq]
---
## grShrineRoute_8020AF38 (`src/melee/gr/grshrineroute.c`) — regalloc + permuter-blocked

- **Tags:** `regalloc`, `permuter-blocked`, `varargs-cr1eq`
- **Best fuzzy:** 77.0517%
- **Diagnosis:** Best 77.05% match with 31 mismatches. Target uses 6 callee-saved regs (r26-r31), base uses 4 (r28-r31). Stack frame -0x38 vs base -0x30. After adding 'float unused1;' local, scale slot moved from 0x14 to 0x18 (matching target) and saved 4 bytes of frame. Remaining diff: target keeps ix*4 (r31), gp (r30), pgobj (r28), gobj (r26), arg1 (r27) ALL callee-saved AND derives &symbols[ix] in r29 inside the if-branch via 'addi r29, r4, 0x108'. Base computes &symbols[ix] once in r31 outside the branch and reuses r30 for pgobj after ix dies. Pure register-allocation territory.
- **Tried:** (1) HSD_GObj** sym_p alias rewrite using *sym_p three times - dropped to 72.22%; (2) reorder Ground* gp / s32 ix declarations - no change; (3) float unused1 added before ix decl - +0.08% (76.97% -> 77.05%), kept (matches similar functions in TU like grShrineRoute_8020AE08). PERMUTER BLOCKED: vendor/decomp-permuter/import.py fails to assemble target.s with 'unsupported relocation against cr1eq' from the 'crclr cr1eq' emitted for the varargs efSync_Spawn call - cluster permuter cannot be dispatched.
- **Likely fix:** Two paths: (a) tooling fix - patch decomp-permuter import.py / target.s post-processing to strip or rewrite the 'crclr cr1eq' reloc so binutils-as accepts it, then permuter can attempt regalloc shuffling locally/cluster; (b) source-level - find a shape that forces mwcc to keep both gp AND ix*4 separately as callee-saved without folding them into an &symbols[ix] alias. Possibly use index arithmetic that touches symbols[ix] through a different path each time, or split the function so the 4-bytes-of-extra-locals encourages 6-reg allocation. Current structure already mirrors the matched grKongo_801D5340/grOldKongo_8020F52C dispatch functions but those have different control flow.
