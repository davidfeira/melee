---
function: it_2725_Logic43_Clanked
tu: src/melee/it/items/ityoshieggthrow.c
headline: regalloc + stack-offset
tags: [regalloc, stack-offset, paired-siblings]
---
## it_2725_Logic43_Clanked (`src/melee/it/items/ityoshieggthrow.c`) — regalloc + stack-offset

- **Tags:** `regalloc`, `stack-offset`, `paired-siblings`
- **Best fuzzy:** 91.0149%
- **Diagnosis:** 15 strict mismatches at fuzzy 91.09% (down from 16 baseline). After swapping decl order to jobj-before-attrs, base now has jobj->r30 (matching target), but ip and attrs registers still swapped: target r29=ip,r31=attrs vs base r31=ip,r29=attrs. Also remaining: scale at 0x20(r1) target vs 0x24(r1) base (same frame size 0x38, phantom 4-byte slot in base before scale). Plus 'addi r3,r28,0x0' vs 'mr r3,r28' instruction-form differences in 2 spots, and an extra 'addi r31,r3,0x0' move-after-load at the function head. Same diagnosis class as paired sibling it_802B2E7C.
- **Tried:** (a) swap decl order from attrs-first to jobj-first inside if-block: 16->15 mismatches, kept. (b) move all locals outside if (matching it_802B2E7C cousin shape) with PAD_STACK(0x10): no further improvement, reverted. Cousin already tried PAD_STACK(0x14) with no luck.
- **Likely fix:** The r29<->r31 ip/attrs swap suggests target wants ip materialized directly into r29 at the lwz (no r3->r31 move). Combined with stack-offset 0x20 vs 0x24 (4 bytes phantom), hint from cousin notes is to force a 4-byte stack spill via inline GET_ITEM(gobj) re-read or some local that occupies a slot just below scale. Solving sibling it_802B2E7C likely solves this too. Permuter false-positive risk LOW (these are real instruction differences not reloc-symbol noise) but the regalloc nature + small instr count makes it permuter-territory IF the source-shape door isn't found. Not dispatching since cousin has been on plateau; structural fix likely needed.
