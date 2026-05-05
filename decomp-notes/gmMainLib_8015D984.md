---
function: gmMainLib_8015D984
tu: src/melee/gm/gmmain_lib.c
headline: regalloc + permuter-territory
tags: [regalloc, permuter-territory]
---
## gmMainLib_8015D984 (`src/melee/gm/gmmain_lib.c`) — regalloc + permuter-territory

- **Tags:** `regalloc`, `permuter-territory`
- **Best fuzzy:** 85%
- **Diagnosis:** 2 instr off (99.64%): target schedules 'add r3,r3,r0; addi r31,r3,0x6c' (defers writing r31 until the +0x6c step), base emits 'add r31,r3,r0; addi r31,r31,0x6c' (writes r31 first then re-uses). Pure regalloc/scheduling on the &gmMainLib_804D3EE0->unk_6C[arg0] address calc before the lbTime_8000AFBC() call.
- **Tried:** 1) Inlined to 'gmMainLib_804D3EE0->unk_6C[arg0] = lbTime_8000AFBC();' � regressed to 80.25% (call hoisted ahead of address calc). 2) Combined to single 'u32* qwe = &gmMainLib_804D3EE0->unk_6C[arg0]; *qwe = ...;' � regressed to 85% (compiler pulled @sda21 load into r0 path).
- **Likely fix:** Permuter-territory: only 2 regalloc instructions remain, no source-shape leverage. Dispatch via 'permute.py diff gmMainLib_8015D984 --auto-permute --cluster'.
