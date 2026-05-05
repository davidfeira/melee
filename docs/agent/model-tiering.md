# Model Tiering for Subagent Dispatch

Empirical guidance for picking which model to use when spawning a subagent. Revisit as data accumulates.

The bottleneck for subagents is **iteration count**, not raw model speed. Each compile+diff cycle is 3-5s; a subagent that needs 10 attempts spends most of its time in tool calls regardless of model. Pick the model that converges in fewest attempts.

## Tier guidance

### Haiku 4.5
**Use only for fully mechanical tasks** (apply pattern X to file Y) WHERE THE 100% VERIFICATION CHECK IS HARD-CODED.

Haiku has been observed to commit partial matches. Only dispatch with explicit reinforcement: "do not commit unless `match: 100.0` in BOTH `permute.py diff` AND `report.json`".

### Sonnet 4.6
**Default for genuinely-easy near-misses** where the bug is obvious from the diff (off-by-ones, swapped args, motion-ID typos).

Observed to over-iterate on novel cases (50-85 tool uses, 7-17 min). Don't dispatch Sonnet against structural diagnoses.

### Opus 4.7
**Use for novel structural diagnoses, multi-file pattern discovery, anything where a wrong first guess wastes a lot of compile cycles.**

Often faster end-to-end than Sonnet despite being slower per-token because it converges in 1-2 attempts.

### Mama Claude (Opus)
Doesn't dispatch Opus subagents — escalations route back to mama directly.

## Hard cap

**Subagent budget is 2 source-shape attempts**, not 3. If neither works, report and escalate. The third attempt almost always overlaps the diagnostic territory where mama Claude or permuter is the right tool anyway.
