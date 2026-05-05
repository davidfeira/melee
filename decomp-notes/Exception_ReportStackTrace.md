---
function: Exception_ReportStackTrace
tu: src/sysdolphin/baselib/particle.c
tags: [tu-data-osreport, data-symbols-missing]
---
## Exception_ReportStackTrace (`src/sysdolphin/baselib/particle.c`)

- **Tags:** `tu-data-osreport`, `data-symbols-missing`
- **Best fuzzy:** 99.94% (Opus subagent — escalated, no commit)
- **Diagnosis:** 5 ARG_MISMATCH on the OSReport string-pool anchor. Target anchors via existing `lbl_8040AB00` with offsets `0x8CC/0x904/0x924`; base anchors via `...data.0` with offsets `0x5B4/0x5E0/0x600`. Function source is correct.
- **Likely fix:** merge surrounding data declarations + the OSReport format strings into one combined struct so mwcc anchors via `lbl_8040AB00`. Multi-symbol restructure, beyond single-function scope. Similar to gr/ TU-data pattern but with a different anchor symbol.
