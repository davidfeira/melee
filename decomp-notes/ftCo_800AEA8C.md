---
function: ftCo_800AEA8C
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, frame-size, bitfield-reuse]
---
## ftCo_800AEA8C (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `frame-size`, `bitfield-reuse`
- **Best fuzzy:** 51.9346%
- **Diagnosis:** 153-instr Fighter AI tick. Two manual source-shape attempts plateau ~51% with 112 mismatches. Target uses saved regs r28/r29 to hold constants 1/0 across many calls (rlwimi sources for 8 bitfield writes + var_r28 'targetable' flag + reuse as 'hit' var); base materializes constants inline (li r4,1; li r5,0) because mwcc -O4,p sees lifetimes as too short to promote. Same regalloc/frame-size class as already-logged ftCo_800B2AFC in same TU. Switch over item->kind ({8,9,0x12} match else var_r28=0) compiles to wrong branch shape with if/else-if (mwcc emits 'beq common' instead of target's 'bne next; b common' per arm). Stack frame 0x58 vs 0x68 (Vec3 sp28/sp34 + sp40 + sp44 merging into smaller slots). x44/x50 stored via fp+0x1ACC/fp+0x1AD8 in target but via data->x44/data->x50 (r31) in base.
- **Tried:** Attempt1: switch+goto block_check_held with int targetable, separate Vec3/sp40/sp44 locals, &data accessor. 51.80% / 115 mismatches. Attempt2: explicit s32 var_r28/var_r29/ret locals (matching m2c hint), if-else-if chain over kind, fp->x1A88.x44 / fp->x1A88.x50 fp-relative, mpCheckFloor stack arg as NULL, removed unused sp8. 51.12% / 112 mismatches. Bit-twiddle order matches target rlwimi shifts (xF8_b0=false; xF9_b2=true; xF9_b4=true; xF9_b3=false; xF9_b5=true; xF9_b6=true; xF9_b7=true; xF9_b1=false). inlineI1 helper used (matches sibling ftCo_800AE7AC pattern). Forward decl in ftCo_0A01.h updated UNK_RET/UNK_PARAMS -> void/Fighter*.
- **Likely fix:** Permuter (when online) for register-allocation rolling; may bridge regalloc churn but unlikely to flip stack frame size or saved-reg count alone. Manual re-attempt could try: (a) tying var_r28/var_r29 to the bit-clear writes by assigning bool fields from the int (forcing mwcc to keep them resident), (b) keeping a single block-scoped int in mpCheckFloor branch named the same as outer flag so liveness extends across calls, (c) writing the if-else-if as 3-way OR ((kind==8)||(kind==9)||(kind==0x12)) and inverting the early-exit so each cmpwi has its own bne+b pair like target. Same TU has logged ftCo_800B2AFC with identical regalloc/frame-size plateau ~50%.

