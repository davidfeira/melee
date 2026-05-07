---
function: hsd_803B5EA0
tu: src/sysdolphin/baselib/hsd_3B34.c
headline: header-prototype + regalloc
tags: [header-prototype, regalloc, mwcc-loop-opt]
---
## hsd_803B5EA0 (`src/sysdolphin/baselib/hsd_3B34.c`) — header-prototype + regalloc

- **Tags:** `header-prototype`, `regalloc`, `mwcc-loop-opt`
- **Best fuzzy:** (unknown)
- **Diagnosis:** hsd_803B5D70 returns u8 but target asm uses mr./cmpwi (s32 patterns), not clrlwi/cmplwi; also the inline memory access pattern (s32*)(base + x*4 + 0x718) generates addi+stwx but target wants slwi+add+stw-with-offset; inner loop uses subic. counter pattern vs target mtctr/bdnz; 152/197 mismatches at 59%
- **Tried:** Attempt 1: m2c-based rewrite using arr718/arr818 pointer variables (55.9%). Attempt 2: direct cast *(s32*)(base+x*4+0x718) pattern with u8* base variable (59.2%). Both attempts produce wrong zero-extension pattern for hsd_803B5D70 return and wrong memory-access codegen.
- **Likely fix:** Change hsd_803B5D70 return type from u8 to s32 (in header or with static redecl); find the C pattern that generates slwi r0,x,2; add r4,r30,r0; stw val,0x718(r4) - may need struct with explicit u32 field at 0x718 offset; for the inner loop counter pattern use a separate count variable not a pointer so compiler emits subic. not bdnz

