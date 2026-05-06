---
function: HSD_SynthSFXGroupDataReaddress
tu: src/sysdolphin/baselib/synth.c
headline: permuter-queued + regalloc
tags: [permuter-queued, regalloc, instruction-scheduling]
---
## HSD_SynthSFXGroupDataReaddress (`src/sysdolphin/baselib/synth.c`) — permuter-queued + regalloc

- **Tags:** `permuter-queued`, `regalloc`, `instruction-scheduling`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 94.1% (19 mismatches). Source shape is correct: outer loop walks p=&vpb->index, inner loop processes count=p[2] entries of stride 0x40 modifying offsets 0x14/0x18/0x1C, then advances p by (count<<6)+0x10. Remaining diffs are pure register allocation: outer counter i in r5 vs target r4, inner pointer q in r4 vs target r3, count in r3 vs target r5. Also (count<<6)+0x10 collapses to one addi in base but stays two ops (slwi + addi r29,r29,0x10) in target, and add operands are reversed (add r29,r0,r29 vs r29,r29,r0). Classic permuter territory.
- **Tried:** form 1: do/while with --count, missed mtctr. form 2: for(j=count;j>0;j--) inner, for(i=0;...) outer with p=&vpb->index hoisted before HSD_DevComRequest call.
- **Likely fix:** Permuter to swap r3/r4/r5 register choices for the loop counter/pointer/count triple and tweak the (count<<6)+0x10 expression form (e.g. (s32)(count*64+16) cast or temp variable).

