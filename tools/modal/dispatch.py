"""Local dispatcher: fan out N permuter-queued functions to Modal in parallel.

Usage:
    python tools/modal/dispatch.py <func>                      # one function
    python tools/modal/dispatch.py --batch 10                  # top 10 from queue
    python tools/modal/dispatch.py --batch 10 --budget 1800    # 30 min each

Reads `decomp-notes/<func>.md` frontmatter to pull the `permuter-queued` set,
then invokes the deployed `melee-permuter` Modal app once per function. Results
are unpacked into `nonmatchings/<func>/` so existing `harvest`/`reap` tooling
(in `permute.py`) finds them.

Requires the Modal app to be deployed first:
    modal deploy tools/modal/permuter_app.py
"""
from __future__ import annotations

import argparse
import concurrent.futures
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTES_DIR = REPO_ROOT / "decomp-notes"
NM_ROOT = REPO_ROOT / "nonmatchings"


def queued_functions() -> list[str]:
    """Return functions tagged `permuter-queued` in their decomp-notes frontmatter."""
    out: list[str] = []
    for note in sorted(NOTES_DIR.glob("*.md")):
        text = note.read_text(encoding="utf-8", errors="replace")
        if "permuter-queued" in text and not _has_tag(text, "permuter-dispatched"):
            out.append(note.stem)
    return out


def _has_tag(text: str, tag: str) -> bool:
    """Cheap frontmatter tag check — avoids YAML dep."""
    head, _, _ = text.partition("---\n---")
    return tag in head


def _tar_nm_dir(func: str) -> bytes:
    nm_dir = NM_ROOT / func
    if not nm_dir.is_dir():
        raise SystemExit(f"missing {nm_dir} — set up locally with `permute.py permute {func}` first")
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tar_path = Path(tmp.name)
    try:
        with tarfile.open(tar_path, "w:gz") as tf:
            for p in nm_dir.iterdir():
                if p.name.startswith("output-") or p.name == "modal-results.tar.gz":
                    continue
                tf.add(p, arcname=p.name)
        return tar_path.read_bytes()
    finally:
        tar_path.unlink(missing_ok=True)


def _unpack_results(func: str, tarball: bytes) -> int:
    nm_dir = NM_ROOT / func
    nm_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tar_path = Path(tmp.name)
    try:
        tar_path.write_bytes(tarball)
        with tarfile.open(tar_path, "r:gz") as tf:
            members = tf.getmembers()
            tf.extractall(nm_dir)
            return sum(1 for m in members if m.name.startswith("output-"))
    finally:
        tar_path.unlink(missing_ok=True)


def dispatch_one(func: str, wall_seconds: int, workers: int) -> dict:
    # Lazy import so `--list` works without modal installed
    import modal

    fn = modal.Function.from_name("melee-permuter", "run_permuter")
    nm_bytes = _tar_nm_dir(func)
    print(f"[{func}] dispatching ({len(nm_bytes)//1024} KB nm_dir, budget={wall_seconds}s)")
    result = fn.remote(
        func=func,
        nm_tarball=nm_bytes,
        wall_seconds=wall_seconds,
        workers=workers,
    )
    n_outputs = _unpack_results(func, result["results_tarball"])
    print(f"[{func}] {result['status']} in {result['elapsed_seconds']:.0f}s — "
          f"{n_outputs} outputs unpacked")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("func", nargs="?", help="single function name (mutually exclusive with --batch)")
    p.add_argument("--batch", type=int, default=0, help="dispatch top N from permuter-queued")
    p.add_argument("--list", action="store_true", help="list queued functions and exit")
    p.add_argument("--budget", type=int, default=1800, help="wall-clock seconds per function (default 1800)")
    p.add_argument("--workers", type=int, default=8, help="-j N inside each container (default 8)")
    p.add_argument("--parallel", type=int, default=4, help="max concurrent Modal calls from this dispatcher (default 4)")
    args = p.parse_args()

    if args.list:
        for f in queued_functions():
            print(f)
        return 0

    if args.func and args.batch:
        sys.exit("pass <func> OR --batch, not both")

    if args.func:
        targets = [args.func]
    elif args.batch:
        targets = queued_functions()[: args.batch]
        if not targets:
            sys.exit("no permuter-queued functions found")
    else:
        p.print_help()
        return 1

    print(f"[modal] dispatching {len(targets)} function(s), parallel={args.parallel}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futures = {
            ex.submit(dispatch_one, f, args.budget, args.workers): f
            for f in targets
        }
        for fut in concurrent.futures.as_completed(futures):
            f = futures[fut]
            try:
                fut.result()
            except Exception as e:
                print(f"[{f}] FAILED: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
