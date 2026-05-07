---
function: grHomeRun_8021C82C
tu: src/melee/gr/grhomerun.c
headline: data-anchor + tu-data-osreport
tags: [data-anchor, tu-data-osreport, string-pool]
---
## grHomeRun_8021C82C (`src/melee/gr/grhomerun.c`) — data-anchor + tu-data-osreport

- **Tags:** `data-anchor`, `tu-data-osreport`, `string-pool`
- **Best fuzzy:** 99.9655%
- **Diagnosis:** OSReport string literals for grHomeRun_8021C82C are stored in .data at offsets relative to grHr_803E8140 base. Target has strings at +0x110 and +0x134; our compiled base has them at +0xDC and +0x100 (0x34 bytes too early). The grHr_803E8140 array is 11 entries * 0x14 = 0xDC bytes in our TU. The target's layout implies additional data (0x34 bytes) between the array end and the OSReport format strings, likely from other in-progress functions in the TU that produce different .data content. The function code itself is identical to upstream/master.
- **Tried:** Confirmed function source matches upstream/master exactly. Checked data layout via dtk elf info: our .data has @179 at 0xDC (format string) and @180 at 0x100 (filename). Target needs them at 0x110 and 0x134. Diff shows DIFF_ARG_MISMATCH on the addi immediates in the OSReport branch.
- **Likely fix:** The .data layout will self-correct once all other functions in grhomerun.c that produce data are matched/completed, bringing the TU's .data section into alignment with the target. This is not fixable by editing grHomeRun_8021C82C alone — it's a whole-TU data ordering issue.

