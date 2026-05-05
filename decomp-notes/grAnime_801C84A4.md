---
function: grAnime_801C84A4
tu: src/melee/gr/granime.c
headline: regalloc + permuter-blocked (varargs-cr1eq)
tags: [regalloc, permuter-blocked, varargs-cr1eq]
---
## grAnime_801C84A4 (`src/melee/gr/granime.c`) — regalloc + permuter-blocked (varargs-cr1eq)

- **Tags:** `regalloc`, `permuter-blocked`, `varargs-cr1eq`
- **Best fuzzy:** 97.92% (3 strict mismatches, 53-instr function)
- **Diagnosis:** Pure register-allocation diff. Source structure mirrors matched sibling `grAnime_801C8318` (same TU) plus an `HSD_AObjGetFlags(result) & 0x04000000` post-check — same shape as already-matched `grAnime_801C83D0`. The 3 remaining mismatches form a single regalloc pattern around the join point feeding `HSD_AObjGetFlags`:
  - target: `li r0, 0x0` / `lwz r0, 0x14(r1)` / `mr r3, r0` / `bl HSD_AObjGetFlags`
  - base: `li r3, 0x0` / `lwz r3, 0x14(r1)` (no extra `mr`)
  Target keeps the result variable in r0 across both predecessor blocks of the join, base uses r3 directly. Stack frame, prologue, epilogue, body, and `__setjmp`/`HSD_ForeachAnim` call sequence all match perfectly. The local declaration list (`enum mask=0; HSD_JObj* jobj; u8 _[8]; HSD_AObj* sp14=NULL; HSD_AObj* result;`) is necessary to keep frame at 0x30 — removing the `u8 _[8]` padding drops the stack to 0x28 and explodes mismatch count.
- **Tried:** (1) Eliminate the `result` intermediate and use `sp14` directly in both branches — broke 13 mismatches because frame shrinks without padding; (2) Inline ternary `jobj == NULL ? NULL : sp14` directly into HSD_AObjGetFlags arg — dropped to 86.5% (10 mismatches), changed control-flow shape.
- **Permuter blocker:** `vendor/decomp-permuter/import.py` exits 1 with `Error: unsupported relocation against cr1eq` at line 78 of target.s. The variadic `HSD_ForeachAnim` call emits `crclr cr1eq` which binutils rejects as a relocation. Same blocker family as `grFlatzone_80216F48`, `grShrineRoute_8020AF38`, `fn_801652D8`, `un_80308354` — affects every PowerPC variadic-call near-miss.
- **Likely fix:** (a) tooling fix — patch decomp-permuter `import.py` to translate `crclr cr1eq` → `crclr 6` or strip the line before assembly, then dispatch a cluster permuter (3-instruction regalloc-pure noise; should land in low iterations); (b) source-shape — find a way to coax mwcc into preferring r3 directly across the early-return + fall-through join. Sibling `grAnime_801C83D0` matched with `result = grAnime_801C8318(gobj, arg1, arg2)` extracted as a separate call, but here the early-NULL exit needs to be expressed without the intermediate var.
