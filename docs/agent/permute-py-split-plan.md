# `tools/permute.py` Split Plan

The script grew to ~4500 lines and 28 subcommands. Splitting it into per-command-group modules makes individual commands testable, reduces merge churn, and lets an AI load only the relevant slice.

This is a multi-session refactor. The `notes` group has already been extracted to `tools/permute_notes.py` as a working pattern. Continue from there.

## The pattern (already in place)

A command group lives in a sibling `tools/permute_<group>.py` module. It:

1. Defines its own subcommand handlers (`cmd_*`)
2. Defines internal helpers it owns
3. Exposes an `add_subcommands(sub)` function that registers its parsers
4. Receives cross-module dependencies via a `_set_deps(...)` injection (called once from `main()` in `permute.py`) — this avoids circular imports

`tools/permute.py` becomes thinner over time. It imports each group module, calls `_set_deps` in `main()`, and calls `<module>.add_subcommands(sub)` instead of inlining the argparse blocks.

## Suggested extraction order

Order matters: extract leaves first (commands with few cross-dependencies), then trunks. Each step is independently committable and testable.

| Order | Module | Subcommands | Notes |
|------:|--------|-------------|-------|
| ✅ done | `permute_notes.py` | `notes`, `log-stuck` | Pattern reference. ~380 lines. |
| 1 | `permute_check.py` | `check`, `pr-check` | Trivial: thin wrappers around `wsl_ninja`. |
| 2 | `permute_budget.py` | `budget`, `permute-stop` | Owns pidfile coordination. |
| 3 | `permute_reset.py` | `reset-attempts` | Standalone, ~30 lines. |
| 4 | `permute_outputs.py` | `outputs` | Reads `nonmatchings/<func>/`. |
| 5 | `permute_picker.py` | `picker`, `backlog` | Reads `report.json`. |
| 6 | `permute_tu.py` | `tu-lock`, `tu-unlock`, `tu-brief` | Owns `_TU_LOCK_PATH`, `.tu-refactor.lock`. |
| 7 | `permute_match.py` | `commit-match`, `commit-improvements` | Touches git. |
| 8 | `permute_dispatch.py` | `dispatch`, `classify`, `brief`, `compact-brief` | Largest group; ~1200 lines. Deferred until others done. |
| 9 | `permute_harvest.py` | `harvest`, `reap` | Cross-cuts; needs careful extraction. |
| 10 | `permute_sweep.py` | `sweep-lha-extsh` | Specialized; can be last. |
| 11 | `permute_events.py` | `events` | Standalone reader. |
| 12 | `permute_prep.py` | `prep`, `permute`, `index-embeddings` | Heavy core; do last so common helpers can be factored to `permute_common.py` first. |

After 3-4 modules are extracted, identify recurring helpers and pull them into `permute_common.py`:

- `wsl()`, `wsl_ninja()` — process invocation
- `find_c_file()`, `find_c_file_by_symbol()`, `_load_or_build_symbol_cache()` — symbol lookup
- `_log_event()`, `BUILD_LINUX`, `ROOT`, `SRC` — paths + telemetry
- `disasm_and_extract()`, `_extract_function_pair()` — asm extraction
- `find_similar_via_embeddings()` — embedding lookup

## How to extract one group (recipe)

1. **Pick a group** from the table above. Read its `cmd_*` handlers and any helpers used only by them.
2. **Identify external dependencies** — anything called by the group but defined elsewhere. These will be injected via `_set_deps`.
3. **Create `tools/permute_<group>.py`**:
   - Copy the relevant `cmd_*`, helpers, and any group-owned state (paths, locks).
   - Add a `_deps: dict = {}` and a `_set_deps(...)` function for injection.
   - Add an `add_subcommands(sub)` function with the argparse blocks.
4. **In `tools/permute.py`**:
   - Add `import permute_<group>` at the top.
   - In `main()`, call `permute_<group>._set_deps(...)` with the needed callables.
   - Replace the inline argparse blocks with `permute_<group>.add_subcommands(sub)`.
   - Delete the now-duplicated `cmd_*` and helper definitions.
5. **Smoke test:**
   ```
   python tools/permute.py <subcmd> --help
   python tools/permute.py <subcmd> <typical args>
   ```
6. **Commit** before extracting the next group. Each module is one PR-sized change.

## Don't bite off more than this

- **One module per session.** It's tempting to do five at once; the cost of a broken daily-driver tool is high.
- **Don't refactor behavior while extracting.** Pure code-motion only. Behavior changes go in a separate commit so a bisect can pinpoint regressions.
- **`permute_common.py` is opportunistic.** Don't pre-create it and force everything through. Wait until 3+ modules genuinely share a helper, then extract it.
