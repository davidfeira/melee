---
function: DevText_Setup
tu: src/melee/if/textdraw.c
headline: regalloc + instruction-scheduling
tags: [regalloc, instruction-scheduling, permuter-plateau]
---
## DevText_Setup (`src/melee/if/textdraw.c`) — regalloc + instruction-scheduling

- **Tags:** `regalloc`, `instruction-scheduling`, `permuter-plateau`
- **Best fuzzy:** 96.9737%
- **Diagnosis:** Baseline strict diff has 14 mismatches: most are private sbss symbol-name mismatches (devtext_* vs un_804D6E*) plus argument-register scheduling around GObj_SetupGXLink. Target loads gx_link into r5 and render_priority into r0, then truncates both; current source loads/truncates only gx_link because GObj_SetupGXLink's prototype has u8 for the third arg and u32 for the fourth.
- **Tried:** Codex attempts: casting render_priority to u8 compiled but worsened to 15 mismatches by loading render before gx; local temp shape with both casts also worsened to 15 mismatches and still used the opposite load/register order. Both edits were reverted. Prior permuter plateau best was output-60-1 using repeated render_priority & 0xFF masks, not a source-quality match.
- **Likely fix:** Likely needs either TU-private sbss symbol renaming/layout cleanup plus a very specific MWCC argument-evaluation shape, or another permuter run seeded around the output-60-1 mask idea. Do not hand-grind the obvious cast/temp variants further.
