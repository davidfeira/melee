---
function: grFlatzone_80216F48
tu: src/melee/gr/grflatzone.c
headline: regalloc + permuter-blocked
tags: [regalloc, permuter-blocked]
---
## grFlatzone_80216F48 (`src/melee/gr/grflatzone.c`) — regalloc + permuter-blocked

- **Tags:** `regalloc`, `permuter-blocked`
- **Best fuzzy:** 99.14% (12 strict mismatches, 58-instr function)
- **Diagnosis:** Pure r29/r30 register-allocation swap on the two main locals (`callbacks = &grFz_803E7940[gobj_id]` and `gobj = Ground_GetStageGObj(gobj_id)`). Target wants `callbacks→r29`, `gobj→r30`; base produces the opposite. r28 (saved arg0) and r31 (base array address) match. All 12 mismatches are the same swap repeated across the function body. The OSReport branch also shows `addi r3, r31, 0xf4 / addi r4, r31, 0x118` listed as DIFF_ARG_MISMATCH but the immediates and registers are identical — it's a fuzzy false-positive on the rodata pool relocation symbol. Structure semantically correct; matches m2c output and matches the `Ground_SetupStageCallbacks(gobj, callbacks)` helper-style pattern used in cross-TU siblings (grTFox_80220C2C, grTLink_802219D0, grTLuigi_80221CB4).
- **Tried:**
  - Reordering local declarations (`HSD_GObj* gobj;` declared first, callbacks computed first) — no effect.
  - Extracting a static-inline helper `grFlatzone_80216F48_inline(gobj, callbacks)` — same 12 mismatches.
- **Permuter blocker:** `import.py` exits 1 with `Error: unsupported relocation against cr1eq` at line 91 of target.s. The OSReport variadic call emits `crclr cr1eq` which binutils 2.x rejects as a relocation. Same blocker family as `fn_801652D8` and `un_80308354` notes — affects every PowerPC variadic-call near-miss.
- **Likely fix:** Either (a) patch `vendor/decomp-permuter/import.py` to translate `crclr cr1eq` → `crclr 6` (or strip the line) before assembly, then re-dispatch to permuter (this is regalloc-pure noise, low iteration count expected to land); or (b) discover a source-shape trick that flips the r29/r30 priority — possibly by restructuring so callbacks is computed inside the `if (gobj != NULL)` block (changes liveness of the array index across the call).
- **Sibling family:** grFlatzone_80218260 matched via inline-vs-local-var trick (commit daa19291b). grFlatzone_802181B4 has its own cluster permuter active. F48 doesn't fit the inline-vs-local trick because both r29/r30 candidates already span the call boundary.
