---
function: un_802FF7DC
tu: src/melee/if/soundtest.c
headline: tu-wide-data-anchor
tags: [tu-data-osreport, cross-tu-globals, paired-siblings]
---
## un_802FF7DC (`src/melee/if/soundtest.c`) — tu-wide-data-anchor

- **Tags:** `tu-data-osreport`, `cross-tu-globals`, `paired-siblings`
- **Best fuzzy:** 72.7619%
- **Diagnosis:** 42-instr LoadSymbols-style init. Target uses ONE base anchor `un_803F9F28` (data:string, size 0x10, at the start of soundtest.c .data) and addresses every other static via a fixed offset from it: `+0x1DC`="SmSt.dat", `+0x1E8`="smSoundTestLoadData", `+0xA8`=un_803F9FD0, `+0xB4`=un_803F9FDC, `+0x148`=un_803FA070, `+0x168`=un_803FA090, `+0x174`=un_803FA09C, `+0x188`=un_803FA0B0. Base emits separate `@ha/@l` pairs for "SmSt.dat"/"smSoundTestLoadData" string literals (rodata pool) and separate `@sda21`/`@ha+@l` for each global. Same TU-wide BSS/.data anchor blocker called out in CLAUDE.md and documented for sibling un_80300AF4. Source code itself (lbArchive_LoadSymbols call + 6 assignments from un_804D6DA8[0..5]) is semantically correct; the only divergence is the data-pool anchor strategy mwcc picks.
- **Tried:** Diff inspection only; no source-shape attempts (per Permuter Boundary, false diffs from equivalent BSS/global base symbols should not be permuted; per CLAUDE.md "Verify whether the source really needs changing first"). Permuter cannot bridge anchor-symbol divergence per prior soundtest/it_2725/mp/lbmthp notes.
- **Likely fix:** TU-wide refactor of soundtest.c .data layout. The strings "SmSt.dat" and "smSoundTestLoadData" must live as .data members at offsets +0x1DC/+0x1E8 from `un_803F9F28`, and all the un_803F9FXX/un_803FAXXX statics need to become fields of a single struct rooted at `un_803F9F28` (described as data:string size 0x10 in symbols.txt). This affects every other function in the TU (un_802FF88C, un_802FFB58, un_802FFBAC, …) so it's a multi-function cross-cutting refactor, beyond single-function scope. Pairs with un_80300AF4/un_80300B58 (same TU, same pattern) — one structural fix likely lifts all three simultaneously.
