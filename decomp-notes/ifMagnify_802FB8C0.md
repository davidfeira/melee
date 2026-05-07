---
function: ifMagnify_802FB8C0
tu: src/melee/if/ifmagnify.c
headline: stack-offset + sdata2-named
tags: [stack-offset, sdata2-named, regalloc, r30-r31-swap]
---
## ifMagnify_802FB8C0 (`src/melee/if/ifmagnify.c`) — stack-offset + sdata2-named

- **Tags:** `stack-offset`, `sdata2-named`, `regalloc`, `r30-r31-swap`
- **Best fuzzy:** 94.2915%
- **Diagnosis:** Frame is 0x80 (correct with PAD_STACK(24)), but S32Vec2 sp40 lands at sp+0x48 instead of sp+0x40. Target has unused 8-byte gap at 0x48-0x4f; base puts S32Vec2 there instead. Additionally, int-to-float bias double uses anonymous @sda21 symbol instead of named ifMagnify_804DDB50@sda21 — static const double declaration didn't resolve this. Total: 73 mismatches, well above 15-mismatch permuter threshold.
- **Tried:** Attempt 1: basic m2c-based implementation. Attempt 2: Added PAD_STACK(24) to fix frame size (correct), added static const double ifMagnify_804DDB50 declaration for named bias symbol, fixed all type errors. Frame is now correct at 0x80 but S32Vec2 is 8 bytes too high in the stack layout. PAD_STACK(16) gives frame 0x78 (too small). No obvious way to shift S32Vec2 down 8 bytes without changing function semantics. r30/r31 swap and FPR swap are permuter territory but cannot be reached while structural blocker remains.
- **Likely fix:** Need to determine why the base allocates 8 extra bytes in the local variable area, placing S32Vec2 at 0x48 instead of 0x40. The target has an unused 8-byte gap at 0x48-0x4f that may be a compiler-allocated temp. Possible causes: (1) MWCC allocates an extra Vec2 temp for the (Vec2*)&sp30 cast; (2) variable declaration order creates unexpected alignment padding; (3) some other temp variable needs explicit declaration. For the sdata2 issue: the static const double declaration may need to be float const or placed in .static.h to take effect. After fixing stack layout, remaining regalloc (r30/r31 swap, f0/f2 FPR swap) is permuter territory.

