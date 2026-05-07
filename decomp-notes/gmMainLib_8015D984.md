---
function: gmMainLib_8015D984
tu: src/melee/gm/gmmain_lib.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-territory]
---
## gmMainLib_8015D984 (`src/melee/gm/gmmain_lib.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-territory`
- **Best fuzzy:** 99.6429%
- **Diagnosis:** 2 instr off at 99.64%: target emits 'add r3,r3,r0; addi r31,r3,0x6c' (ptr+arg0*4 computed in r3, then +0x6c assigned to r31), base emits 'add r31,r3,r0; addi r31,r31,0x6c' (ptr+arg0*4 directly into r31). Pure regalloc: which register holds the intermediate of the array-index add.
- **Tried:** Attempt 1 (this session): single-expression 'u32* qwe = &gmMainLib_804D3EE0->unk_6C[arg0];' -> 85% (6 mismatches, compiler reorders sda21 load and uses r3 for slwi). Attempt 2 (this session): cast arithmetic '(u32*)gmMainLib_804D3EE0 + (arg0 + 0x6c/4)' -> tool blocked before diff. Best shape remains two-step: base=&unk_6C[0]; qwe=&base[arg0].
- **Likely fix:** Permuter-territory: only 2 regalloc instructions, no source-shape leverage found across 4 total attempts (2 prior + 2 this session). Permuter with --cluster is the correct path.

