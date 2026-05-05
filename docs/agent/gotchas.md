# Gotchas

Known pitfalls. Reach for this when something behaves unexpectedly.

- **`tools/decomp.py` flag forwarding** — uses `argparse.REMAINDER`, so flags like `--no-copy` after the function name get forwarded to m2c and crash. Pass flags *before* the function name, or use `permute.py prep --m2c` which handles this correctly.

- **m2c context regeneration** — `decomp.py` regenerates `build/ctx.c` on every call by default (~5s). `permute.py prep --m2c` caches via header mtime check.

- **Stale `report.json`** — `permute.py picker` reads `build-linux/GALE01/report.json`. If numbers look stale, run a ninja first.

- **`/mnt/c` is slow vs ext4** — single-file rebuild via wibo+mwcc is ~18s. First full WSL ninja takes 20-30 min; incremental is fast.

- **`build.ninja` is generated** — overwritten by `configure.py`. The current one is WSL/wibo-mode. To switch to Windows-native, re-run `configure.py` without `--wrapper`.

- **Game files are gitignored locally** — `Dolphin-x64/`, `*.iso`, `sys/` are gitignored; don't try to commit them.
