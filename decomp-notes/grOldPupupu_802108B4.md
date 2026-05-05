---
function: grOldPupupu_802108B4
tu: src/melee/gr/groldpupupu.c
tags: [data-symbols-missing]
---
## grOldPupupu_802108B4 (`src/melee/gr/groldpupupu.c`)

- **Tags:** `data-symbols-missing`
- **Best fuzzy:** 92.65% (Haiku subagent attempted, reverted)
- **NOT a clean gr/ pattern instance** — strings need to be at frame-relative offsets `r31+0xf4` and `r31+0x118` (very different layout from other gr/ functions). Standard global symbol declarations produce addresses at `r31+0x0` or `r31+0x24`.
- **Blocker:** no `StageData` global to wrap (vs other gr/ files that have one to extend). Layout requires understanding how the linker places strings in `groldpupupu.o` specifically.
- **Likely fix:** non-trivial reverse-engineering of the data section.
