---
function: mn_8022DDA8_OnEnter
tu: src/melee/mn/mnmain.c
headline: stack-offset + float-literal
tags: [stack-offset, float-literal, tu-wide-data, permuter-false-positive]
---
## mn_8022DDA8_OnEnter (`src/melee/mn/mnmain.c`) — stack-offset + float-literal

- **Tags:** `stack-offset`, `float-literal`, `tu-wide-data`, `permuter-false-positive`
- **Best fuzzy:** 99.9987%
- **Tags:** `stack-offset`, `float-literal`, `tu-wide-data`, `permuter-false-positive`
- **Best fuzzy:** 99.9987% (strict 99.9920%) — Opus subagent, 2 mismatches.
- **Function size:** 0xBA8 (746 instructions). Heavily inlines `mn_8022DDA8_inline`, `mn_8022BCF8`, `mn_8022BE34`, `mn_8022BEDC`, `mn_80229B2C` (all auto-inlined with `-inline auto`).
- **Diagnosis:** 2 mismatches remain after Opus attempts.
  1. `addi r4, r1, 0x2a8` vs `addi r4, r1, 0x294` — Vec3 from inlined `mn_8022BE34` (passed to `HSD_CObjGetEyePosition`) lives at sp+0x294 in our build vs sp+0x2A8 in target. 0x14 byte stack-offset shift below Vec3.
  2. `lfs f1, mn_804DBDA8@sda21` vs `lfs f1, @267@sda21` — the `0.0F` literal passed to `HSD_JObjReqAnimAll` in inlined `mn_80229B2C` (line 811) uses target's named sdata2 global `mn_804DBDA8` but our build uses an anonymous sdata2 entry `@267`.
- **Tried (Opus, 2 attempts):**
  1. `u8 _[0x14] → _[0x28]` and `_[0x14] → removed`. Both broke 179 mismatches because frame size changed (0x440/0x468 instead of 0x450). The current `_[0x14]` is correct for frame size; it just lands ABOVE Vec3 instead of BELOW where target wants it.
  2. **WORKED:** `static char mn_804D4B78[8] = "MnMaAll";` at file scope, used in place of inline `"MnMaAll"`. Eliminated 1 of 3 mismatches. This is the named sdata global pattern — the target had a globally-named string literal at 0x804D4B78. Persisted in commit-pending source.
  3. (NOT counted as separate attempt) `static const f32 mn_804DBDA8 = 0.0f` — MWCC constant-folded back to literal pool, no effect. `static f32 mn_804DBDA8 = 0.0f` — went to .sbss not .sdata2. Reverted.
- **Likely fix (NOT viable from this function alone):**
  - **Stack-offset:** Permuter not directly usable — `permute.py permute` fails with `Error: unsupported relocation against cr1eq` during target.s assembly (mwcc -O4,p emitted condition-register relocations the permuter as-tooling can't handle). Manual stack rewrites can't move Vec3 down 0x14 bytes without breaking frame-size constraints.
  - **Float literal:** Needs TU-wide sdata2 layout work to define `mn_804DBDA8 = 0.0f` (and probably the surrounding `mn_804DBDA0`, `mn_804DBDA4`, `mn_804DBDAC`, `mn_804DBDB0`, etc. globals listed in symbols.txt at 0x804DBD90-0x804DBDE0). All are scope:global named float symbols originally declared at file scope in mnmain.c. Defining them shifts every other anonymous `@N` float reference in the TU and would break other functions.
- **Classification:** This is the **shared-string/named-sdata-global** false-positive class — same family as `it_802B56E4`, `lbColl_800077A0`. Single-function source-shape edits cannot redirect the literal pool naming.
- **Improved partial fix kept in tree:** `static char mn_804D4B78[8] = "MnMaAll";` at file scope (mnmain.c line 62), `lbArchive_LoadSymbols(mn_804D4B78, ...)` at OnEnter call site. Strict went from 99.9853% to 99.9920%. SHA still passes.
