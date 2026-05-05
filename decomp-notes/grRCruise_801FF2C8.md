---
function: grRCruise_801FF2C8
tu: src/melee/gr/grrcruise.c
headline: tu-data-osreport + cross-tu-globals
tags: [tu-data-osreport, cross-tu-globals]
---
## grRCruise_801FF2C8 (`src/melee/gr/grrcruise.c`) — tu-data-osreport + cross-tu-globals

- **Tags:** `tu-data-osreport`, `cross-tu-globals`
- **Best fuzzy:** 94.8814%
- **Diagnosis:** 94.9% with 5 mismatches centered on OSReport call. Target asm: r31 = grRc_803E4DA8 (a separate 0x8C-byte data symbol that lives at .data+0x0 in the TU, BEFORE the StageCallbacks array grRc_803E4E34 at .data+0x8C). Function uses r31 as base for OSReport args: addi r3,r31,0x158 (format string) and addi r4,r31,0x17c (__FILE__ 'grrcruise.c'). The format string '%s:%d: couldn t get gobj(id=%d)\n' is embedded INSIDE grRc_803E4ECC (a 0x58-byte struct at .data+0x124 containing func ptrs and the format string starting at struct-offset 0x34). __FILE__ lives at .data+0x17C as grRc_803E4F24. Current source defines only StageCallbacks grRc_803E4E34[7] and uses string literals via __FILE__/format string — mwcc places these in @stringbase relative to grRc_803E4E34 (r31+0x8C and r31+0xB0), not relative to a separate prefixed data block. Diff is purely data-layout-driven, not permuter territory (no regalloc/scheduling noise).
- **Tried:** Read the diff output and traced asm vs base. Inspected build-linux/GALE01/asm/melee/gr/grrcruise.s data section (lines 3196-3346). Did not attempt source rewrite — needs TU-wide data refactor outside subagent budget.
- **Likely fix:** Define grRc_803E4DA8 as a global 35-u32 array (with the exact values from grrcruise.s lines 3198-3232) BEFORE the StageCallbacks definition. Replace OSReport call to compute strings via offsets from grRc_803E4DA8 base, with the format string defined as a struct field inside a grRc_803E4ECC struct that contains func ptr table refs + the literal format string at offset 0x34. Touches at minimum 3 OSReport sites in the TU (grRCruise_801FF2C8 here, grRCruise_801FF924 at 801FF928, plus offset uses at 80201424 and 802015A0). Likely a TU-data audit task for mama Claude rather than a single-function subagent.
