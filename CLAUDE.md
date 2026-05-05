# Melee Decomp Agent Notes

This file is loaded into every conversation. It covers daily-driver commands and load-bearing rules. Reference material lives under `docs/agent/`.

## Environment

- Project root: `C:\Users\david\projects\melee` (WSL: `/mnt/c/Users/david/projects/melee`).
- Build is WSL-backed via `build-linux/` (wibo + Linux PowerPC binutils). The checked-in `build.ninja` targets `build-linux`.
- Full builds run inside WSL Ubuntu so wibo can launch the Windows mwcc binaries:
  `wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/david/projects/melee && ninja"`
- Native Windows tools (`build/tools/dtk.exe`, `build/tools/objdiff-cli.exe`) live under `build/`; `permute.py` calls them directly from Windows.
- Python: system Python on PATH. The only venvs are inside WSL (`vendor/decomp-permuter/.venv-linux/` and `.venv-embeddings/`).

For full tooling inventory see `docs/agent/tooling.md`.

## Health Check

- Full ninja:
  `wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/david/projects/melee && ninja"`
- Success line: `build-linux/GALE01/main.dol: OK`
- Quick "did our edit break anything":
  `python tools/permute.py check` (wraps the ninja; reports `SHA1 OK` or `SHA1 FAILED`)

## Daily-Driver: `tools/permute.py`

Always invoked with system `python`, from the repo root.

- `prep <func>` — extract asm + show referenced symbol signatures. `-q` skips asm dump, `--m2c` adds an m2c starter, `--examples N` for in-TU side-by-side examples, `--similar N` for embedding-based cross-TU matches. Standard briefing: `prep <func> -q --m2c --similar 3 --examples 2`. **Auto-runs `upstream-check` first** — refuses if upstream/master already has the function matched (use `--skip-upstream-check` only for intentional re-work).
- `upstream-check <func>` — pre-flight: is `func` already matched or stubbed in `doldecomp/melee` upstream/master? Exit codes: 0=safe, 1=unknown, 2=already matched. Hooked into `prep`; auto-fetches upstream if local data is >24h stale.
- `diff <func>` — match% + per-instruction diff. `--auto-permute` launches background permuter when the near-miss is below `--permute-threshold` mismatched instructions (default 15). Add `--cluster` to dispatch to the local p@h cluster.
- `picker [--mode untouched|in_progress|all] [--max-size N] [--limit N]` — list candidates from `report.json`, sorted by size.
- `commit-match <func>` — re-verifies 100% in BOTH objdiff AND `report.json`; refuses otherwise. The only authorized commit path for matches.
- `log-stuck <func> --tags=… --diagnosis=…` — append a structured diagnostic entry to `decomp-notes.md`. Tags validated against canonical inventory; see `notes --tag-inventory`.
- `notes [<func>] [--blocker TAG] [--tag-inventory]` — query prior diagnoses for a function or by tag.
- `budget` — list active local + cluster permuters; reaps stale pidfiles.
- `reap`, `harvest` — orchestrator loop tools (see `docs/agent/swarm-protocol.md`).
- `permute <func>`, `permute-stop <func>` — manual permuter setup/teardown.
- `index-embeddings` — one-time, builds the function-similarity embedding index (~3-5 min on the GPU). Stored at `build-linux/embeddings.npz`.

## Permuter Boundary

- Manual pass first: confirm types, fields, constants, calls, and control flow are semantically right.
- Run `python tools/permute.py diff <func>`.
- Switch to permuter after 2 manual source-shape attempts if the remaining diff is mostly: register allocation, temp lifetimes, instruction scheduling, expression order, or hoisting/sinking small constants.
- Prefer mismatch count over percentage. A small function at 80-95% can be permuter-ready if only a few register/order choices remain. A large function at 99% may still need manual structural work.
- Don't hand-shuffle locals to chase `r4` vs `r7`, avoid `lhau`, or move `li r0, 0`. Those are good permuter cases.
- Don't use permuter for false diffs from equivalent BSS/global base symbols. Verify whether the source really needs changing first.

## Upstream sync hygiene

`origin` is the user's fork (`davidfeira/meleeDecomp`). `upstream` is the real project (`doldecomp/melee`). The decomp project is hot — Jj/* PRs land daily. **Always check upstream before starting a function** or you'll redo work.

- `prep` runs `upstream-check` automatically and refuses already-matched functions.
- A `SessionStart` hook in `.claude/settings.local.json` runs `git fetch upstream master` at every Claude Code session start.
- `permute.py upstream-check` auto-fetches if local data is >24h stale.
- For retrospective audit of past matches vs upstream: `python tools/upstream_overlap.py`.

## Concurrency

- Other agents may be editing files or running permuters.
- Always run `git status --short` before edits.
- Do not revert user or other-agent changes.
- Check existing background permuters before launching duplicates: `python tools/permute.py budget`.
- Common work area: `nonmatchings/`. Never touch a `nonmatchings/<other-func>/` you didn't create.

## Multi-agent / swarm protocol

Subagent-side rules live in `.claude/agents/permuter-attempter.md` and `.claude/agents/plateau-rescuer.md`. When dispatching, the Agent tool auto-loads them — you don't need to re-explain the protocol in the prompt.

Mama Claude's orchestration loop, CPU budget rules, harvest/reap flow, and the permuter false-positive class are documented in `docs/agent/swarm-protocol.md`.

Visual diagrams of all three loops: `docs/agent-loops.md`.

## Hard-stop rules (apply to mama Claude AND subagents)

- Never push to origin without explicit user approval.
- Never edit files outside `src/melee/`, `src/sysdolphin/`, or your specific assigned function (no tool changes, no `.gitignore` edits).
- Never kill a permuter you didn't launch.
- If `git status --short` shows unexpected changes you don't recognize, **stop and report**.
- **Never run destructive working-tree ops.** No `git stash` (push or pop), `git restore`, `git checkout -- <file>`, `git checkout .`, `git reset --hard`, `git clean -f`, `rm` on tracked files. The working tree is shared with other agents — those commands clobber uncommitted work. Revert your own edits surgically with the Edit tool.
- **`commit-match` only commits the `.c` file by design.** If your match also requires a `.h` / `.static.h` change, REPORT that explicitly. Mama Claude lands header changes in a follow-up.

## Reference docs

- `docs/agent/swarm-protocol.md` — orchestration loop, CPU budgets, false-positive class
- `docs/agent/model-tiering.md` — Haiku/Sonnet/Opus dispatch guidance
- `docs/agent/cluster.md` — local p@h cluster setup
- `docs/agent/tooling.md` — installed binaries, venvs, Python deps
- `docs/agent/gotchas.md` — known pitfalls
- `docs/agent-loops.md` — visual diagrams (Mermaid)
