---
function: un_802FFF2C
tu: src/melee/if/soundtest.c
headline: bss-anchor + permuter-false-positive
tags: [bss-anchor, permuter-false-positive, mwcc-loop-opt, struct-typing]
---
## un_802FFF2C (`src/melee/if/soundtest.c`) — bss-anchor + permuter-false-positive

- **Tags:** `bss-anchor`, `permuter-false-positive`, `mwcc-loop-opt`, `struct-typing`
- **Best fuzzy:** 95.1105%
- **Diagnosis:** 93.97% match (82 instr) with two distinct issues. (1) BSS-anchor false positive: lis/addi reference '...bss.0@ha/@l' instead of 'un_803FA128@ha/@l' but post-link bytes are identical (~12 instructions). (2) Loop unrolling mismatch: target uses do{..r5+=8; r6+=0x48;}while(--ctr) with ctr=2, induction r5=&un_803FA128+0x130 and r6=arg0; my for(i=0;i<2;i++){[i*2+0];[i*2+1];} is completely unrolled by MWCC into 4 absolute r31-relative loads per field (~70 instructions of register/offset shuffle). Also r6 vs r3 register choice in the unrolled output.
- **Tried:** (a) flat for(i=0;i<2;i++) with explicit [i*2+0]/[i*2+1] indexing -> 93.97% (compiler fully unrolls). (b) byte-pointer arith via (s32*)((u8*)src+N) casts -> 90.7% (added register pressure forced r28/stmw save). (c) do{..}while(--i) with i=2 and j=(2-i)*2 -> 86.2% (extra arith hurts). The struct un_803FA128 was redefined with named arrays c_kind[4], slot_type[4], color[4], sub_color[4], team[4], x12_arr[4], x18_arr[4], x1C_arr[4], x20_arr[4], xE_arr[4], cpu_level_arr[4], rumble_arr[4] plus scalar fields x138, x13C, x1F8, x1FC, x200, x204, x208, x21C.
- **Likely fix:** The original C very likely uses a pointer-walking loop with src incremented by 8 bytes per iteration, e.g. via a local struct pointer that aliases an internal section of un_803FA128. Need a struct shape where MWCC keeps the loop and emits r5+=8, r6+=0x48 induction. Possibly the source data is a separate global (not a sub-struct of un_803FA128) declared with stride 8 between pairs. Permuter cannot help: BSS-anchor false-positive will register as 100%, masking real structural issue.

