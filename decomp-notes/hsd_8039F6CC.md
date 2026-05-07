---
function: hsd_8039F6CC
tu: src/sysdolphin/baselib/particle.c
headline: header-prototype + header-required
tags: [header-prototype, header-required, data-anchor, regalloc]
---
## hsd_8039F6CC (`src/sysdolphin/baselib/particle.c`) — header-prototype + header-required

- **Tags:** `header-prototype`, `header-required`, `data-anchor`, `regalloc`
- **Best fuzzy:** 92.5%
- **Diagnosis:** Improved to 96.25% (6 mismatches). Dead beq pattern solved: if(gen==NULL) return NULL; if(gen!=NULL){ gen->jobj=jobj; if(jobj!=NULL){ ref_INC(jobj); } }. Remaining: (1) extsb r3,r3 extra -- hsd_8039F05C declared s8 linkNo in particle.h:145 but both callee body and callers show no sign-extension in target, needs s32; (2) addi r30,r6,0x0 vs mr r30,r6 -- pure regalloc; (3-6) lbl_8040C2A4/lbl_8040C2B0 vs @3586/@3587 -- anonymous string literals from ref_INC inline in object.h vs named symbols in target data section; fuzzy also reports 6 mismatches, not a permuter-false-positive.
- **Tried:** Attempt 1: added outer if(jobj!=NULL) around ref_INC -- got one dead beq (94.17%). Attempt 2: added if(gen!=NULL) wrapper for gen->jobj and if(jobj!=NULL){ ref_INC } -- both dead beqs resolved (96.25%).
- **Likely fix:** Change particle.h:145 hsd_8039F05C first param from s8 to s32 to eliminate extsb. For data-anchor: declare static char lbl_8040C2A4[9] = 'object.h' and lbl_8040C2B0[0x27] = 'HSD_OBJ(o)->ref_count != HSD_OBJ_NOREF' in particle.c at correct data position and inline ref_INC manually with explicit named string args. Regalloc mismatch is permuter territory.

