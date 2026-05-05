---
function: it_802BA3BC
tu: src/melee/it/items/itsamusgrapple.c
headline: stack-offset + regalloc
tags: [stack-offset, regalloc]
---
## it_802BA3BC (`src/melee/it/items/itsamusgrapple.c`) — stack-offset + regalloc

- **Tags:** `stack-offset`, `regalloc`
- **Best fuzzy:** 99.5588%
- **Diagnosis:** 99.56% (19 mismatches): mwcc places dir at sp+0x2c instead of target's sp+0x28 (12-byte gap above saved_pos in our build, none in target). Plus link var lives in r26 vs target's r27 (regalloc swap with next_tail/clear-bit constant).
- **Tried:** (1) reduce _pad[8] to _pad[4] (no effect, alignment rounded back to 8); (2) remove _pad entirely (frame shrunk to 0x60, worse); (3) move _pad after dir (worse, 35 mm); (4) PAD_STACK(16)+remove dir_ptr+inline dir refs (frame became 0x70, much worse). Frame is correctly 0x68 only with original _pad[8] before dir.
- **Likely fix:** permuter dispatch (cluster) — regalloc r26↔r27 is textbook permuter territory; stack offset may resolve via permuter rearranging local declarations. If permuter fails: try declaring saved_pos before dir (would put dir at lower addr, but then saved_pos at higher — opposite of target), or experiment with adding/removing dummy locals to push the unused 16-byte gap above dir instead of between dir and saved_pos.
