---
function: ftCo_800B2AFC
tu: src/melee/ft/chara/ftCommon/ftCo_0A01.c
headline: frame-size + regalloc
tags: [frame-size, regalloc, stack-offset, instruction-scheduling, permuter-blocked]
---
## ftCo_800B2AFC (`src/melee/ft/chara/ftCommon/ftCo_0A01.c`) — frame-size + regalloc

- **Tags:** `frame-size`, `regalloc`, `stack-offset`, `instruction-scheduling`, `permuter-blocked`
- **Best fuzzy:** (unknown)
- **Diagnosis:** 557-instr jumptable dispatch over fp->x1A88.xC; 4 cases (0/1/3/26) inline mpCheckFloor block with distinct stack-allocated Vec3 hit_pos, Vec3 hit_normal, u32 flags, int line_id. Target uses 0xc8 frame with 4 NON-overlapping stack regions per case (case0:0x8c-0xab, case1:0x68-0x87, case3:0x48-0x67, case26:0x18-0x37) and only 3 saved GPRs (r29,r30,r31) via separate stw. Base built source produces 0xb8 frame and stmw r27 (5 saved regs) — compiler is merging at least one case's stack region and spilling to r27/r28 due to extra register pressure. Cannot easily push mwcc into 4 distinct stack regions: distinct named locals at function-top (hit_pos0/1/3/26) still get merged. Additional churn: f1-vs-f3 register choice for ax arg, and float-literal load order (e.g. fadds f2 source register, base loads 0.0f first vs target loads 1000.0f then 10.0f then 0.0f). Plateau at ~50% match, 389 mismatches. Permuter is offline so cannot dispatch; tagging permuter-blocked. (Note: structural mismatch is too large for permuter anyway — would need source restructuring first.)
- **Tried:** Attempt1: per-case block-scope locals — 49.56%. Attempt2: function-top distinct named locals (hit_pos0,hit_pos1,hit_pos3,hit_pos26 etc) with shared int ret/var_r29/float x/y — 49.73%. Bit-clear order corrected (xF9_b4 before xF9_b3 to match rlwimi sh=3 vs sh=4 ordering). Inline helpers inlineI0 and inlineI1_alt confirmed correct for 23/25 prefixes.
- **Likely fix:** (1) refactor each mpCheckFloor case body into a separate static helper function (one per case) so locals get distinct stack frames — risk of breaking other matches; (2) declare locals inside per-case else-blocks of an if-ladder instead of switch to disable mwcc switch-arm stack merging; (3) use per-case struct types or arrays so compiler treats each as its own object. Permuter unlikely to bridge ~50%+389-mismatch gap from stack/register-allocation alone.

