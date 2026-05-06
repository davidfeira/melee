---
function: grIceMt_801F865C
tu: src/melee/gr/gricemt.c
headline: permuter-blocked
tags: [permuter-blocked]
---
## grIceMt_801F865C (`src/melee/gr/gricemt.c`) — permuter-blocked

- **Tags:** `permuter-blocked`
- **Best fuzzy:** 80.8202%
- **Diagnosis:** 99.87% (11 mismatches). All remaining diffs are stack-frame size only: base allocates 0x30 bytes vs target 0x28. Source-shape correct: bit-clear via ((UnkFlagStruct*)&gp->gv.icemt2.xC4)->b0=0; struct copy via 'static const grIm_JointArr5 grIm_803B825C = {{1,2,3,4,5}};' assigned to 'grIm_JointArr5 joint_indices' inlines as lwz/lwz/lhz + stw/stw/sth. Call: grIceMt_801F8CDC(arg0, joint_indices.v, 5, gp->gv.icemt.xF8). Compiler places struct at sp+0x18 vs target sp+0x14 (8-byte alignment padding). Permuter offline (--auto-permute disabled per environment override); should resolve quickly via local-reorder when re-enabled.

