---
function: DevText_Create
tu: src/melee/if/textlib.c
headline: cross-TU refactor
tags: [cross-tu-globals]
---
## DevText_Create (`src/melee/if/textlib.c`) — cross-TU refactor

- **Tags:** `cross-tu-globals`
- **Best fuzzy:** 99.98% (Opus subagent — escalated, no commit)
- **Diagnosis:** 17 mismatches dominated by symbol relocations pointing to the wrong TU. Our build references `white`/`red`/`green`/`blue`/`devtext_drawlist`/`devtext_poolhead` (currently in `textlib.c`) while target wants `un_804DDC8C/90/94/98` and `un_804D6E18/38` plus `@163`/`@186`-`@190` literals. Plus a 1-byte PAD_STACK offset.
- **Root cause:** `config/GALE01/splits.txt:3982` shows `melee/if/textlib.c` has only `.text` + `.bss`. The `sdata2` range `0x804DDBA8..DCC8` (where white/red/green/blue live in target at DC8C-DC98 + floats at DC9C/DCA0) belongs to `melee/if/if_2FC93.c` (splits.txt:3949). OSReport/__assert string args and the drawlist/poolhead globals also belong there.
- **Likely fix:** move `GXColor white/red/green/blue` (textlib.c lines 55-58) plus `devtext_drawlist` and `devtext_poolhead` into `if_2FC93.c`, change to `extern` in textlib.c. Cross-TU edit — out of scope for single-function subagent.
