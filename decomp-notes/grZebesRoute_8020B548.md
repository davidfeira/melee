---
function: grZebesRoute_8020B548
tu: src/melee/gr/grzebesroute.c
headline: permuter-queued + sdata2-anonymous-floats
tags: [permuter-queued, sdata2-anonymous-floats, frame-size, regalloc, instruction-scheduling]
---
## grZebesRoute_8020B548 (`src/melee/gr/grzebesroute.c`) — permuter-queued + sdata2-anonymous-floats

- **Tags:** `permuter-queued`, `sdata2-anonymous-floats`, `frame-size`, `regalloc`, `instruction-scheduling`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 195-instr loop over light objects (HSD_GObjGXLinkHead[4]'s LObj list). Manual source matched semantically (3-branch switch on flags & 3, lpos.y vs 500.0f, scaled Vec3 positions/interest, GXColor literals, HSD_LObjGetNext iter). Diff at 72.5% (147 mismatches) — dominated by sdata2 anonymous floats (@267-274) vs named grZe_Route_804DB92C-944, plus frame-size 0xA8 vs target 0xB8 (16 bytes short, outgoing-param reserve), and r25/r26 register allocation differences across the lobj_head/i/iter-var lifetimes. The sdata2-named-float symbols are post-link-equivalent (false-positive class) so a permuter run should report 'already 100%' and quit.
- **Tried:** (1) Initial source-shape with HSD_LObjGetNext loop, separate Vec3 locals per branch (pos0, pos1 for branch 1; pos2 for branch 2; pos3 for branch 3) — got 70-72% match. (2) Tried explicit pre-loop dist0/1/2 = 600/1000/400 * scale temporaries — same match (mwcc hoists scale*const naturally). Reverted to inline form.
- **Likely fix:** Frame-size diff (0x10 bytes) suggests a missing local slot or different struct copy strategy for Vec3 init from base[i]. Or different outgoing-param-area calc. Permuter (when back online) should resolve sdata2 naming + regalloc + scheduling automatically; current source likely matches post-link.

