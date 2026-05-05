# Swarm Protocol — Mama Claude Reference

The orchestration loop run by mama Claude. Subagent-side rules are codified in `.claude/agents/permuter-attempter.md` and `.claude/agents/plateau-rescuer.md` — when dispatching, those agents auto-load the per-function rules. This file is mama Claude's view.

## Dispatch flow

1. **Pick targets** — `python tools/permute.py picker --mode in_progress` (near-misses) or `--mode untouched`
2. **Spawn ≤3 subagents in parallel** via the Agent tool with `subagent_type=permuter-attempter` (or `plateau-rescuer` for plateau follow-ups)
3. **Periodically:**
   - `python tools/permute.py reap` — kills permuters past 60min wall-clock OR silent for 15min
   - `python tools/permute.py harvest` — reports per-function status:
     - **HIT 100%**: candidate at `nonmatchings/<func>/output-100-N`. Manual port to `src/<file>.c` (preprocessed source — can't be copied verbatim), then `commit-match`.
     - **PLATEAU**: best <100%, no new outputs in 15min. Dispatch `plateau-rescuer` against this function.
     - **PROGRESSING**: leave alone.
4. **Tunables:** `reap --wall-cap-min N --silent-cap-min N`, `harvest --plateau-min N`. Defaults work for most cases.

## Diagrams

See `docs/agent-loops.md` for visual diagrams of all three loops.

## CPU budget rules

Current host: Ryzen 5 5600X, 6c/12t.

- Max 2 concurrent **local** permuters at `-j 4` (uses 8 of 12 logical cores).
- Cluster permuters do NOT count — use `--cluster` to bypass the cap.
- Single-permuter wall-clock cap: 60 min (cluster) — enforced by `reap`.
- Mama Claude can spawn up to 3 subagents in parallel. They mostly think+read, but compile bursts can stack with active permuters. Drop to 2 if the build feels slow.
- `python tools/permute.py budget` distinguishes [local] from [cluster] active jobs.

## Coordination via filesystem

- Active permuter pidfiles: `build-linux/permuter-<func>.pid` (WSL pid) and `.winpid` (Windows pid).
- Active permuter logs: `build-linux/permuter-<func>.log`.
- `python tools/permute.py budget` is the single source of truth; reaps stale pidfiles automatically.
- Permuter scratch dirs: `nonmatchings/<func>/`. Subagents must never touch a `nonmatchings/<other-func>/` they didn't create.

## Permuter false-positive class

Don't dispatch the permuter on near-misses dominated by `@ha`/`@l` reloc-symbol mismatches:

- BSS-anchor: `bss.0+0xN` vs `lbl_X+0`
- sdata2 float: `@N@sda21` vs named global
- Data anchor: `.data.0+0xN` vs `lbl_X`

The permuter scorer treats those as equivalent (post-link bytes match) but `report.json` fuzzy does not. The run will return immediately with "already 100%" and you'll waste a slot. Tag as `permuter-false-positive` + the layout class and `log-stuck` instead.

## Model tiering

See `docs/agent/model-tiering.md`.
