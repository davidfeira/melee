---
function: Exception_ReportStackTrace
tu: src/sysdolphin/baselib/particle.c
headline: tu-data-osreport + data-symbols-missing
tags: [tu-data-osreport, data-symbols-missing, permuter-false-positive]
---
## Exception_ReportStackTrace (`src/sysdolphin/baselib/particle.c`) — tu-data-osreport + data-symbols-missing

- **Tags:** `tu-data-osreport`, `data-symbols-missing`, `permuter-false-positive`
- **Best fuzzy:** 99.9423%
- **Diagnosis:** 5 ARG_MISMATCH on OSReport string-pool anchor: target uses lbl_8040AB00+{0x8CC,0x904,0x924}, base uses ...data.0+{0x5B4,0x5E0,0x600}. Function source is semantically correct. Upstream already has this matched. The diff is purely a data-anchor layout issue.
- **Tried:** Reviewed prior diagnosis; confirmed upstream match state (doldecomp/melee already has it matched); re-ran diff — same 5 DIFF_ARG_MISMATCH, no regression from prior agent attempt. Permuter would be false-positive (post-link bytes match, report.json fuzzy does not).
- **Likely fix:** Merge surrounding OSReport format strings into one combined struct so mwcc anchors via lbl_8040AB00. Multi-symbol TU restructure required; beyond single-function scope. Pull upstream match instead.

