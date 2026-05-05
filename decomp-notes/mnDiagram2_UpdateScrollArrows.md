---
function: mnDiagram2_UpdateScrollArrows
tu: src/melee/mn/mndiagram2.c
headline: regalloc
tags: [regalloc]
---
## mnDiagram2_UpdateScrollArrows (`src/melee/mn/mndiagram2.c`) — regalloc

- **Tags:** `regalloc`
- **Best fuzzy:** 98.4016%
- **Diagnosis:** 35/39 mismatches are pure regalloc swap: target uses r30=data, r29=jobj; base produces r29=data, r30=jobj. Both use r31=base anchored to mnDiagram2_803EEAD0. The 4 'real' addi r4,r31,0x9c entries are identical-text diff-alignment artifacts caused by the regalloc divergence (objdiff flags surrounding instructions in differing blocks). Reloc relocations are identical (R_PPC_ADDR16_HA/LO mnDiagram2_803EEAD0 in both target+base).
- **Tried:** V1: swapped decl-init order base=...;data=... -> data=...;base=... (no change, 39 mismatches). V2: reordered local declarations so u8*base appears first (no change, 39 mismatches). mwcc saved-reg choice between r29 and r30 for data vs jobj is not driven by decl/init order in this function shape.
- **Likely fix:** Permuter territory - register allocation swap r29<->r30. Source-shape variants (decl order, init order) do not influence mwcc's choice here. Recommend: dispatch to permuter (cluster) to find a perm that flips reg assignment (e.g. an extra temp local or fold base into the jobj reload sequence).
