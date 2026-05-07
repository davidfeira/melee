# Modal permuter workers

Cloud CPU runner for `decomp-permuter`. Drains the `permuter-queued` backlog
faster than the local CPU budget allows.

## Why this design (not p@h)

Vendored `permuter@home` workers require docker-in-docker on the worker host.
Modal containers don't naturally support that, so instead each Modal container
runs `permuter.py` directly on a single function. One container per function;
parallelism comes from spawning many containers, not from a shared controller.

For our backlog (~1400 candidates total, ~170 in the easy 99.5%+ pool as of
the truthful state-tracking pass) this is actually a better fit — work is
naturally shardable per-function and we don't need cross-worker progress
sharing.

## One-time setup

```
pip install modal
modal token new                              # browser auth
modal deploy tools/modal/permuter_app.py     # builds image, deploys app
```

The first deploy bakes the toolchain (`build-linux/wibo`, GC compilers,
binutils, decomp-permuter source, repo subset under `src/`/`extern/`/`include/`)
into the image — ~250 MB layer. Subsequent deploys only rebuild the layers
whose contents changed (typically just `src/`).

## Running

Single function:

```
python tools/modal/dispatch.py fn_803AC3F8 --budget 1800
```

Batch from the truthful candidate pool (sourced from `tools/state/state.py`,
which joins `build/GALE01/report.json` with `tools/state/notes.jsonl`):

```
python tools/modal/dispatch.py --list                              # all <100% candidates
python tools/modal/dispatch.py --list --min-pct 99.5               # easy flips (~172)
python tools/modal/dispatch.py --list --min-pct 95 --max-pct 99.5  # mid-tier
python tools/modal/dispatch.py --batch 10 --min-pct 99.5           # top 10 easy flips
python tools/modal/dispatch.py --batch 10 --skip-prepped           # skip already-tried
```

`--parallel N` caps concurrent Modal invocations from your laptop (default 4);
Modal itself runs every dispatched container in parallel.

**Recommended cadence for the easy pool (>99.5%):**
1. `--list --min-pct 99.5` to preview (~172 functions)
2. `--batch 20 --min-pct 99.5 --budget 600` — 20 funcs, 10 min each
3. Each container that hits 100% leaves a winning `output-*` in
   `nonmatchings/<func>/`; `python tools/permute.py harvest <func>` extracts
   the winner. The full-TU regression scan in `tools/state/verify.py` will
   refuse the commit if a neighbor regresses.

Results land in `nonmatchings/<func>/output-*` so the normal `harvest` /
`commit-match` flow picks them up.

## Cost-watch

- 8 vCPU × 30 min ≈ 4 vCPU-hours per dispatch
- Modal CPU billing as of 2026: ~$0.000131 / vCPU-second → ~$1.90 / dispatch
- $30/mo free credit ≈ 15 dispatches before paying
- For sustained heavy use, reconsider Hetzner CCX33 (~$0.10/hr dedicated)

## Limits

- No live progress streaming — final tarball returns at end of wall-clock budget
- 1-hour Modal timeout cap on `run_permuter`; raise via `@app.function(timeout=)` for longer cooks
- Dispatcher refuses if `nonmatchings/<func>/` doesn't exist locally —
  run `permute.py permute <func>` once first to bootstrap base.c/target.s
