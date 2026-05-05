---
function: mpColl_80046224_LeftWall
tu: src/melee/mp/mpcoll.c
headline: regalloc + paired-siblings
tags: [regalloc, paired-siblings, permuter-false-positive]
---
## mpColl_80046224_LeftWall (`src/melee/mp/mpcoll.c`) — regalloc + paired-siblings

- **Tags:** `regalloc`, `paired-siblings`, `permuter-false-positive`
- **Best fuzzy:** 99.8136%
- **Diagnosis:** Same 18 mismatches as prior V1/V2 attempts. Target keeps line_id in r25 (callee-saved), base in r26. Stmw r25 vs r26 (one extra saved GPR). The previous notes' likely-fix (a) sub-scope local for inline-Ceiling block won't help: sister mpColl_800454A4_RightWall uses function-level line_id in the same way and matches. The asymmetric piece is the int* arr loop walker (extra callee-saved) PLUS line_id ALSO in callee-saved; cannot remove arr without losing the 0x24-base preinit form (target shows addi r30,r31,0x24; lwz r28,0x0(r30) which is pointer-walk). Subscript form generates 0x24 offset on each load, regresses to 36 mismatches. Plus 2 sda21 anchor false-positives (lfs f0,@1504@sda21 vs mpColl_804D7FA0@sda21; lfs f31,@308@sda21 vs @225@sda21).
- **Tried:** Re-attempt session: V3=remove u8 _[4] + subscript form + unshadow inner line_id (36, regressed); V4=just subscript form (36, regressed, frame 0xd8 vs 0xd0, line_id still in r25 not r26). Confirms prior V1 finding: subscript form is wrong; pointer-walk arr is correct shape.
- **Likely fix:** The int* arr is correct for target's 0x24 preinit. Need source shape where mwcc keeps int* arr in callee-saved BUT line_id in a non-saved temp. Try: (1) hoist 'int* end = mpColl_80458810.left + mpColl_804D648C' and loop 'for (arr = ...; arr != end; arr++)' (no i counter — frees one reg, may let line_id collapse to non-saved); (2) break inline-Ceiling block out into a static inline helper taking line_id by value — function-level line_id then doesn't live across that block's calls. Permuter false-positive class for the 2 sda21 anchors; skip permuter (scorer treats anchor-id mismatches as equivalent so won't surface a fix).
