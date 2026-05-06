---
function: grFourside_801F3274
tu: src/melee/gr/grfourside.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, sdata2-named-floats, frame-size]
---
## grFourside_801F3274 (`src/melee/gr/grfourside.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `sdata2-named-floats`, `frame-size`
- **Best fuzzy:** 89.153%
- **Diagnosis:** 89.0% match, 108 mismatches. Cascading regalloc/frame diff: target uses r30 for gobj+r29 for crane_iron with frame 0x50; base swaps to r29 for gobj+r30 for crane_iron with frame 0x38. Float literal references use named sdata2 globals (grFs_804DB4F8=0.0f, grFs_804DB500=1.0f, grFs_804DB504=400.0f) in target vs anonymous pool entries (@249/@336/@337) in base — these are deduped sdata2 entries shared TU-wide that mwcc names by address. Also f31 vs f1 alloc for crane_iron_down_min, instruction reordering around fctiwz/double-conversion spills, OSReport varargs. Source semantics correct (control flow + struct fields verified). Attempt 1 (remove unused jobj decl) did not change match. All remaining diff is classic permuter territory: register pressure, literal pool layout, scheduler. Permuter offline — queue for later.

