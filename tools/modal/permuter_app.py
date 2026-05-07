"""Modal app: run decomp-permuter on a single function in the cloud.

Architecture:
- Image bakes the GC compiler toolchain (mwcc + wibo + sjiswrap), binutils,
  decomp-permuter source, and the relevant repo subset (src/, extern/, include/).
- The local dispatcher (`tools/modal/dispatch.py`) tarballs `nonmatchings/<func>/`
  and invokes `run_permuter` over the wire.
- The function rewrites compile.sh to use the in-container repo path, then runs
  permuter.py with the requested wall-clock budget. The best `output-*` files
  are returned as a tarball.

Bring-up:
    pip install modal
    modal token new           # one-time auth
    modal deploy tools/modal/permuter_app.py
    python tools/modal/dispatch.py <func>

This is a single-container-per-function model — no controller, no p@h vouching.
For 87 queued functions, fanning out via `dispatch.py --batch` parallelizes
across containers.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path

import modal

APP_NAME = "melee-permuter"

# Repo paths (resolved on the *local* side at image-build time, then COPYed in)
REPO_ROOT = Path(__file__).resolve().parents[2]

# Container path where the repo lives. compile.sh is rewritten to cd here.
CONTAINER_REPO = "/repo"

# What we bake into the image. Keep this minimal — Modal rebuilds the image
# whenever any of these change. Toolchain rarely changes; src/ changes often,
# but it's only ~19MB so the layer rebuild is cheap.
IMAGE_INCLUDES = [
    "src",
    "extern",
    "include",
    "build-linux/wibo",
    "build-linux/binutils",
    "build-linux/compilers/GC",
    "build-linux/tools",
    "vendor/decomp-permuter/src",
    "vendor/decomp-permuter/permuter.py",
    "vendor/decomp-permuter/import.py",
    "vendor/decomp-permuter/default_weights.toml",
    "vendor/decomp-permuter/permuter_settings.toml",
    "vendor/decomp-permuter/prelude.inc",
    "vendor/decomp-permuter/perm_pycparser",
    "vendor/decomp-permuter/stubs",
]

image = (
    modal.Image.debian_slim(python_version="3.12")
    # wibo is a 32-bit ELF; needs i386 libc to run
    .apt_install("libc6-i386", "git", "build-essential")
    .pip_install(
        "pynacl==1.6.2",
        "pycparser==2.23",
        "levenshtein==0.27.3",
        "rapidfuzz==3.14.5",
        "toml==0.10.2",
        "attrs",
        "requests",
    )
    .add_local_dir(
        str(REPO_ROOT),
        remote_path=CONTAINER_REPO,
        # Only copy what we actually need; everything else (build artifacts,
        # nonmatchings/, .git, docs/, tests, asm-differ, etc.) stays out.
        ignore=lambda p: not _should_include(p, REPO_ROOT),
    )
)

app = modal.App(APP_NAME, image=image)


def _should_include(path: Path, root: Path) -> bool:
    """Return True if `path` is on the include list, OR is an ancestor of one
    (so Modal recurses into it)."""
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return False
    for inc in IMAGE_INCLUDES:
        inc_path = Path(inc)
        # rel == inc OR rel is descendant of inc OR rel is ancestor of inc
        if rel == inc_path:
            return True
        if inc_path in rel.parents:
            return True
        if rel in inc_path.parents:
            return True
    return False


@app.function(
    cpu=8.0,                # 8 vCPU per worker — permuter parallelizes well
    memory=8192,            # 8 GiB
    timeout=3600,           # 1 hour wall-clock cap (override per-call)
)
def run_permuter(
    func: str,
    nm_tarball: bytes,
    wall_seconds: int = 1800,
    workers: int = 8,
) -> dict:
    """Run permuter on a single function for `wall_seconds`, return outputs.

    Args:
        func: function name (just for logging / output naming).
        nm_tarball: gzipped tar of `nonmatchings/<func>/` (base.c, target.s,
                    target.o, compile.sh, settings.toml).
        wall_seconds: how long to let permuter cook before SIGTERM.
        workers: -j N passed to permuter.py.

    Returns:
        dict with:
          - status: "matched" | "timeout" | "error"
          - log_tail: last ~4KB of permuter stdout
          - results_tarball: gzipped tar of all `output-*` files produced
          - elapsed_seconds: wall time
    """
    work = Path("/tmp/work")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    # Unpack incoming nm_dir
    nm_tar_path = work / "nm.tar.gz"
    nm_tar_path.write_bytes(nm_tarball)
    nm_dir = work / func
    nm_dir.mkdir()
    with tarfile.open(nm_tar_path, "r:gz") as tf:
        tf.extractall(nm_dir)

    # Rewrite compile.sh: replace the WSL `cd /mnt/c/...` with our container path
    compile_sh = nm_dir / "compile.sh"
    if compile_sh.exists():
        text = compile_sh.read_text()
        new_lines = []
        for line in text.splitlines():
            if line.startswith("cd ") and ("/mnt/c/" in line or "melee" in line):
                new_lines.append(f"cd {CONTAINER_REPO}")
            else:
                new_lines.append(line)
        compile_sh.write_text("\n".join(new_lines) + "\n")
        compile_sh.chmod(0o755)

    # Permuter env: PERMUTER_AS for the assembler shim
    env = os.environ.copy()
    env["PERMUTER_AS"] = (
        f"{CONTAINER_REPO}/build-linux/binutils/powerpc-eabi-as -mgekko -mregnames"
    )
    # Permuter uses python from PATH inside compile.sh? No — compile.sh runs
    # wibo + mwcceppc.exe. We need wibo and the GC compilers reachable.
    env["PATH"] = (
        f"{CONTAINER_REPO}/build-linux/binutils:"
        f"{CONTAINER_REPO}/build-linux:"  # for wibo
        + env.get("PATH", "")
    )

    # Run permuter
    cmd = [
        "python3",
        f"{CONTAINER_REPO}/vendor/decomp-permuter/permuter.py",
        f"{nm_dir}/",
        "-j", str(workers),
        "--show-errors",
        "--stop-on-zero",
    ]
    log_path = work / "permuter.log"
    start = time.time()
    status = "timeout"

    with open(log_path, "wb") as logf:
        proc = subprocess.Popen(
            cmd,
            cwd=CONTAINER_REPO,
            env=env,
            stdout=logf,
            stderr=subprocess.STDOUT,
        )
        try:
            rc = proc.wait(timeout=wall_seconds)
            if rc == 0:
                status = "matched"
            else:
                status = "error"
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            status = "timeout"

    elapsed = time.time() - start

    # Tarball outputs
    out_tar = work / "out.tar.gz"
    with tarfile.open(out_tar, "w:gz") as tf:
        for p in sorted(nm_dir.glob("output-*")):
            tf.add(p, arcname=p.name)
        # Include the log so the user can see what happened
        tf.add(log_path, arcname="permuter.log")

    # Tail of log for inline display
    log_bytes = log_path.read_bytes()
    log_tail = log_bytes[-4096:].decode("utf-8", errors="replace")

    return {
        "status": status,
        "log_tail": log_tail,
        "results_tarball": out_tar.read_bytes(),
        "elapsed_seconds": elapsed,
        "func": func,
    }


@app.local_entrypoint()
def main(func: str, wall_seconds: int = 1800, workers: int = 8) -> None:
    """Quick smoke-test entrypoint: dispatch one function from the local repo.

    Usage:  modal run tools/modal/permuter_app.py --func <name>
    """
    nm_dir = REPO_ROOT / "nonmatchings" / func
    if not nm_dir.is_dir():
        raise SystemExit(f"missing {nm_dir} — run `permute.py permute {func}` locally first")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tar_path = Path(tmp.name)
    try:
        with tarfile.open(tar_path, "w:gz") as tf:
            for p in nm_dir.iterdir():
                # Skip prior outputs to keep the upload small
                if p.name.startswith("output-"):
                    continue
                tf.add(p, arcname=p.name)
        nm_bytes = tar_path.read_bytes()
    finally:
        tar_path.unlink(missing_ok=True)

    print(f"[modal] dispatching {func}: nm_tarball={len(nm_bytes)//1024} KB, "
          f"budget={wall_seconds}s, workers={workers}")
    result = run_permuter.remote(
        func=func,
        nm_tarball=nm_bytes,
        wall_seconds=wall_seconds,
        workers=workers,
    )
    print(f"[modal] {func}: status={result['status']} "
          f"elapsed={result['elapsed_seconds']:.0f}s "
          f"results={len(result['results_tarball'])//1024} KB")
    print("--- log tail ---")
    print(result["log_tail"])

    # Drop results next to the local nm_dir for inspection
    out_path = nm_dir / "modal-results.tar.gz"
    out_path.write_bytes(result["results_tarball"])
    print(f"[modal] wrote {out_path}")
