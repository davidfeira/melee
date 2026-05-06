---
function: ftKb_SpecialAirLw_Coll
tu: src/melee/ft/chara/ftKirby/ftKb_SpecialN.c
headline: permuter-queued + scheduler
tags: [permuter-queued, scheduler, instruction-scheduling, sdata2-anonymous-floats, frame-size]
---
## ftKb_SpecialAirLw_Coll (`src/melee/ft/chara/ftKirby/ftKb_SpecialN.c`) — permuter-queued + scheduler

- **Tags:** `permuter-queued`, `scheduler`, `instruction-scheduling`, `sdata2-anonymous-floats`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 91.58% match (45 mismatches). Source structure correct: Air branch does field-wise Vec3 component assignment (x24/x54, x30/x60, x3C/x6C, x48/x78 pairs) with xC4 cached in float temp; Ground branch uses ftKb_Init_803CB490_layout p->vec whole-struct copy. Remaining diffs are: (1) instruction scheduling — target precomputes addi r4=r3+0xc, r5=r3+0x4 helper regs and increments them through later vec stores; mwcc on this source uses direct r3 offsets (within reach). (2) sdata2 anon vs named float — target uses ftKb_Init_804D9390@sda21 for 0.0f, base emits @193@sda21 anonymous. Likely TU-ordering or fuzzy-equivalence (post-link bytes match). (3) Stack frame -0x40 vs -0x30 (16 bytes — PAD_STACK(16) candidate). All structural semantics match.
- **Tried:** (1) field-wise air branch with inlined fp->mv.kb.specialhi.xC4 — got 86.5%, mwcc reloaded xC4 each pair. (2) Cached xC4 in float temp + declared Init_803CB490 ptr at function top so r31 holds it across both branches — got 91.58%.
- **Likely fix:** Permuter scheduling pass. Also try PAD_STACK(16) for stack alignment, and verify if 0.0f literal needs to come from named global ftKb_Init_804D9390. May need --with-fuzzy diff to confirm @193 vs ftKb_Init_804D9390 are link-equivalent — if so most remaining 'mismatches' are false positives.

