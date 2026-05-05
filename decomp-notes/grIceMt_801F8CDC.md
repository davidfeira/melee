---
function: grIceMt_801F8CDC
tu: src/melee/gr/gricemt.c
headline: permuter-false-positive + tu-data-osreport
tags: [permuter-false-positive, tu-data-osreport, regalloc, stack-offset]
---
## grIceMt_801F8CDC (`src/melee/gr/gricemt.c`) — permuter-false-positive + tu-data-osreport

- **Tags:** `permuter-false-positive`, `tu-data-osreport`, `regalloc`, `stack-offset`
- **Best fuzzy:** 99.4%
- **Diagnosis:** 99.45% fuzzy / 98.93% strict, 19 mismatches. 10/19 are reloc-symbol false-positives (4 sdata2 floats: grIm_804DB574/B0/B4/B8 vs anonymous @424/@588/@589/@590; 6 rodata @l offsets via grIm_803E4068 anchor for assert strings: target r28+0x690/0x7f0/0x810/0x81c vs base r28+0x178/0x1bc/0x1c8/0x1d4 -- TU rodata layout differs). Of remaining 9: 8 pure regalloc swaps (target uses r23/r22/r25 for arg2/arg3/i; base uses r25/r23/r22) + 1 stack offset (target parent_jobjs base at r1+0x1c, base at r1+0x18, 4-byte delta) with frame size 0xb0 in both.
- **Tried:** (1) Reordered locals to put unused[24] before parent_jobjs[20] -- no score change but changes layout intent; reverted as inert. (2) Tried u8 unused[28] -- grew frame to 0xb8 (worse). (3) Tried adding int unused2 -- grew frame. Cannot find a 4-byte local that occupies parent_jobjs's expected lower-pad without growing frame; mwcc seems to want padding of 20 bytes below parent_jobjs, but I produce only 16.
- **Likely fix:** Permuter false-positive class dominates -- do NOT dispatch permuter (per protocol section 6). Real remaining work is the 4-byte stack-offset puzzle. Possible: target source has an additional small local variable that mwcc places at the bottom of frame, or parent_jobjs[] is sized larger than 20 (e.g. 21 -> 84 bytes) with no separate unused. Try: HSD_JObj* parent_jobjs[21] alone (no unused). Or mwcc may align the array boundary differently if there's a struct local.
