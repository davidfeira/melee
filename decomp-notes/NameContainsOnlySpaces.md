---
function: NameContainsOnlySpaces
tu: src/melee/mn/mnnamenew.c
headline: regalloc + permuter-plateau
tags: [regalloc, permuter-plateau]
---
## NameContainsOnlySpaces (`src/melee/mn/mnnamenew.c`) — regalloc + permuter-plateau

- **Tags:** `regalloc`, `permuter-plateau`
- **Best fuzzy:** 97.0769%
- **Diagnosis:** Pure register allocation mismatch: 31 instructions differ only in register numbers (r3/r4 swap, r6/r5 swap, r7/r6 swap, r8/r0 swap). Source is structurally identical to upstream matched version. Target interleaves null_char load into r3 between lis r4 and addi r7 for text ptr; our compiler assigns r3 to text (lis r3) instead. Permuter has already run extensively (190+ outputs) and plateaued at score=190 (base score), unable to find a source shape that produces the correct register assignment.
- **Tried:** (1) Removed char* sp local, used mnNameNew_SpaceCharacter[1] inline — made score worse (77%). (2) Verified source is identical to upstream matched version. Upstream difference is only whitespace/formatting. Permuter output examined (output-190-40 best) — no improvement found.
- **Likely fix:** TU-level context difference or different MWCC optimization interaction. May need a different approach in the surrounding code or a compiler version quirk. Possibly upstream matched against a different TU state. Could try reordering other functions in the file or checking if a nearby function change affects this function's regalloc.

