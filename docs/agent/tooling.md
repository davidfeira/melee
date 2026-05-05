# Installed Tooling

Reference list of binaries, venvs, and Python packages the agent stack depends on.

## Binaries

- **WSL Ubuntu** — main build host (sudo password lives with the user)
- `build/tools/dtk.exe` — Windows-side dtk, called by `permute.py` for asm extraction
- `build/tools/objdiff-cli.exe` — Windows-side objdiff, called by `permute.py diff`
- `build-linux/wibo` — Linux PE loader, runs the Windows mwcc binaries inside WSL
- `build-linux/binutils/powerpc-eabi-*` — Linux PowerPC binutils (`as`, `objdump`, etc.)
- `build-linux/compilers/GC/<version>/mwcceppc.exe` — auto-fetched per-TU compilers

## Vendored repos

- `vendor/decomp-permuter/` — patched for Windows path handling and PowerPC prelude
  - Linux venv: `vendor/decomp-permuter/.venv-linux/`

## Python venvs

- `.venv-embeddings/` — torch + transformers for the jina embedding model used by `permute.py prep --similar` and `notes`

## System Python (`pip install --user`)

- `pyelftools`, `m2c`, `pcpp`, `pyperclip`, `pygments`, `graphviz`, `ninja`, `requests`
