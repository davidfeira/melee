# Modal permuter workers

Cloud CPU runner for `decomp-permuter`. Drains the `permuter-queued` backlog
faster than the local CPU budget allows.

## Why this design (not p@h)

Vendored `permuter@home` workers require docker-in-docker on the worker host.
Modal containers don't naturally support that, so instead each Modal container
runs `permuter.py` directly on a single function. One container per function;
parallelism comes from spawning many containers, not from a shared controller.

For our 87-function backlog this is actually a better fit — work is naturally
shardable per-function and we don't need cross-worker progress sharing.

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

Batch from `permuter-queued` queue:

```
python tools/modal/dispatch.py --list                    # preview
python tools/modal/dispatch.py --batch 10 --budget 1800  # top 10, 30 min each
```

`--parallel N` caps concurrent Modal invocations from your laptop (default 4);
Modal itself runs every dispatched container in parallel.

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
