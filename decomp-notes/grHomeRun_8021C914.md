---
function: grHomeRun_8021C914
tu: src/melee/gr/grhomerun.c
headline: permuter-false-positive + string-pool
tags: [permuter-false-positive, string-pool, reloc-symbol-false-positive, sda21]
---
## grHomeRun_8021C914 (`src/melee/gr/grhomerun.c`) — permuter-false-positive + string-pool

- **Tags:** `permuter-false-positive`, `string-pool`, `reloc-symbol-false-positive`, `sda21`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 99.29% match (18 mismatches). Source is structurally correct: simple wrapper that calls grAnime_801C8138 then HSD_JObjSetScale{X,Y,Z}(jobj, grHr_804D6AE4 * HSD_JObjGetScale*(jobj)). All 18 mismatches are sda21 string-pool anchor differences: target uses named symbols grHr_804D49A8 ("jobj.h") and grHr_804D49B0 ("jobj") while base produces anonymous @228@sda21/@229@sda21 from inline HSD_ASSERT/HSD_ASSERTMSG expansion via jobj.h. The string bytes are identical — post-link binary is byte-equivalent. Classic permuter-false-positive (string-pool / sda21 reloc class).
- **Tried:** Single-attempt structural decomp matches asm semantically; m2c-derived form using inline HSD_JObj setters/getters mirrors grHomeRun_8021CB20 (matched sibling).
- **Likely fix:** Either (a) accept as-is via fuzzy report.json (strings dedupe at link time so output is identical), or (b) introduce a same-TU reference to "jobj.h"/"jobj" string literals that earlier in the TU forces them into named slots matching target. Likely no source-level fix can rename anonymous @N pool labels without already having a named producer earlier in the TU. Worth checking whether a sibling function in this TU (grHomeRun_8021CB20 etc.) when matched would push these strings into the pool first.

