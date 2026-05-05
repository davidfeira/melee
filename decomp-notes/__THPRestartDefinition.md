---
function: __THPRestartDefinition
tu: <unknown source>
headline: extern-dolphin
tags: [extern-dolphin]
---
## __THPRestartDefinition (`<unknown source>`) — extern-dolphin

- **Tags:** `extern-dolphin`
- **Best fuzzy:** 99.7647%
- **Diagnosis:** Function lives in extern/dolphin/src/dolphin/thp/THPDec.c, outside swarm scope (src/melee/, src/sysdolphin/). Currently 99.7647% fuzzy.
- **Tried:** No attempts; out of scope per CLAUDE.md hard-stop rule restricting subagent edits to src/melee/ and src/sysdolphin/.
- **Likely fix:** Mama Claude or extern/dolphin maintainer must handle. Subagent dispatch to extern-dolphin functions should be filtered out at the picker/triage layer.
