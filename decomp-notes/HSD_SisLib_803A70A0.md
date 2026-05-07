---
function: HSD_SisLib_803A70A0
tu: src/sysdolphin/baselib/sislib.c
headline: frame-size + stack-offset
tags: [frame-size, stack-offset, regalloc, varargs-cr1eq]
---
## HSD_SisLib_803A70A0 (`src/sysdolphin/baselib/sislib.c`) — frame-size + stack-offset

- **Tags:** `frame-size`, `stack-offset`, `regalloc`, `varargs-cr1eq`
- **Best fuzzy:** 75.2058%
- **Diagnosis:** Stack frame is 8 bytes too small (0x1a8 vs 0x1b0). Root cause: va_list is placed at sp+0x74 in our code vs sp+0x80 in target. All local variable offsets are shifted by -12 bytes (va_list, sp8C, sp90, sp110). The 12-byte gap at sp+0x68..0x7F in the target (between float arg saves and va_list) suggests CW places the va_list at a 32-byte-aligned address (0x80=128=4*32) in the local variable area for this function ABI. Also, var_r28 (encoded length from HSD_SisLib_803A67EC) lands in r31 in our code but r28 in the target, because the target allocator pre-reserves r31 for data_start (alloc->data_1) which needs to survive across two function calls. Our code puts data_start in r4 (volatile) instead.
- **Tried:** Attempt 1: wrote full function with separate data_start variable, got 75.21% (167 mismatches). Attempt 2: inlined new_req expression to avoid extra variable, fixed field access order (data_0 before data_1), got 75.54% (167 mismatches). Swapped array declaration order - no effect on frame size. The sp offset shift (-12) persists across all attempts. The register allocation mismatch (r28 vs r31 for var_r28) also persists.
- **Likely fix:** The frame size issue likely requires additional stack variable declarations to push va_list from sp+0x74 to sp+0x80. Adding 3 x s32 variables (12 bytes total) somewhere before va_list in the local area might fix this. The regalloc issue may resolve automatically once frame size is correct. Alternatively, try declaring a 12-byte struct or padding array at the function top. The varargs-cr1eq tag applies because the cr1 check (bne cr1) for float arg presence is part of the function ABI.

