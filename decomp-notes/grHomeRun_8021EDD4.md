---
function: grHomeRun_8021EDD4
tu: src/melee/gr/grhomerun.c
headline: permuter-false-positive + sdata2-float
tags: [permuter-false-positive, sdata2-float, sdata2-named-floats, sdata2-anonymous-floats, frame-size, float-regalloc, stack-offset]
---
## grHomeRun_8021EDD4 (`src/melee/gr/grhomerun.c`) — permuter-false-positive + sdata2-float

- **Tags:** `permuter-false-positive`, `sdata2-float`, `sdata2-named-floats`, `sdata2-anonymous-floats`, `frame-size`, `float-regalloc`, `stack-offset`
- **Best fuzzy:** 97.9821%
- **Diagnosis:** 99.05% strict (25 mismatches). Two root issues: (1) Stack frame 0x40 (base) vs 0x38 (target) - 8 extra bytes causing cascade of stack-offset mismatches in prologue/epilogue and scratch slots. All 5 f32 locals should fit in f28-f31 plus f1 caller-saved without spill, yet base allocates 8 extra bytes. Cause: likely one f32 local is being forced to stack due to a named-variable spill decision by MWCC. (2) sdata2-float false-positives: target uses named grHr_804DBC88/8C/90/70/30/48/28 and double grHr_804DBC50 for int-to-float bias; base generates anonymous sda21 symbols. Post-link bytes match so this is a strict-vs-fuzzy gap only.
- **Tried:** Attempt 1: Added extern const f32/double declarations for all 8 named constants and replaced float literals with named references. Float names now correct in base, BUT frame still 0x40 and double grHr_804DBC50 still anonymous @505@sda21 (extern declaration alone does not force compiler to use named double for int cast bias), and register allocation shifted giving 29 mismatches (worse). Attempt 2: Removed dist local variable, inlined final expression. 42 mismatches - much worse. Both attempts reverted.
- **Likely fix:** The frame-size blocker (0x40 vs 0x38, 8 bytes) is the true structural mismatch. The sdata2 symbol mismatches are permuter-false-positive class and will match post-link. For the frame: need to find what causes MWCC to allocate 8 extra stack bytes. Possible: try PAD_STACK(0) or restructuring local variable declarations. For grHr_804DBC50: MWCC reuses it when compiling full TU (sibling grHomeRun_8021EA30 uses it), so post-link it merges. Upstream already has this matched so comparing to upstream impl may reveal the right approach.

