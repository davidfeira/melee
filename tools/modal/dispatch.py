"""Local dispatcher: fan out N permuter candidates to Modal in parallel.

Usage:
    python tools/modal/dispatch.py <func>                      # one function
    python tools/modal/dispatch.py --batch 10                  # top 10 by match%
    python tools/modal/dispatch.py --batch 10 --budget 1800    # 30 min each
    python tools/modal/dispatch.py --list                      # show queue
    python tools/modal/dispatch.py --list --min-pct 99         # only funcs ≥99%

Reads candidates from `tools/state/state.py` (which joins build/GALE01/report.json
with tools/state/notes.jsonl). Includes anything in the `permuter-queued`,
`near` (95-99.99%), or `partial` (<95%) buckets — i.e. anything with a
non-trivial decompilation that could benefit from permuter.

For each dispatched function, invokes the deployed `melee-permuter` Modal app.
Results unpack into `nonmatchings/<func>/` so existing `harvest`/`reap`
tooling (in `permute.py`) finds them.

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
NM_ROOT = REPO_ROOT / "nonmatchings"

sys.path.insert(0, str(REPO_ROOT / "tools" / "viz"))
sys.path.insert(0, str(REPO_ROOT / "tools"))


def candidates(min_pct: float = 0.0, max_pct: float = 99.99) -> list[tuple[str, float]]:
    """Return [(func_name, match_percent), ...] sorted by descending match%.

    Pulls from tools/state/state.py — the truthful current state. Excludes
    100% matches (already done) and not_started (no body yet to permute).
    """
    from state import state as state_mod
    out: list[tuple[str, float]] = []
    for s in state_mod.load_state():
        if s.match_percent is None:
            continue
        pct = float(s.match_percent)
        if pct < min_pct or pct > max_pct:
            continue
        out.append((s.name, pct))
    out.sort(key=lambda t: -t[1])
    return out


def already_dispatched(func: str) -> bool:
    """Check if this function already has a permuter run we haven't harvested."""
    return (NM_ROOT / func / "modal-results.tar.gz").exists()


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
    p.add_argument("--batch", type=int, default=0, help="dispatch top N candidates by match%% (descending)")
    p.add_argument("--list", action="store_true", help="list candidates and exit")
    p.add_argument("--min-pct", type=float, default=0.0,
                   help="only candidates with match%% >= this (default 0)")
    p.add_argument("--max-pct", type=float, default=99.99,
                   help="exclude candidates with match%% > this (default 99.99 — drops 100%% matches)")
    p.add_argument("--skip-prepped", action="store_true",
                   help="skip functions whose nonmatchings/<func>/ has a previous modal-results.tar.gz")
    p.add_argument("--budget", type=int, default=1800, help="wall-clock seconds per function (default 1800)")
    p.add_argument("--workers", type=int, default=8, help="-j N inside each container (default 8)")
    p.add_argument("--parallel", type=int, default=4, help="max concurrent Modal calls from this dispatcher (default 4)")
    args = p.parse_args()

    if args.list:
        rows = candidates(args.min_pct, args.max_pct)
        print(f"{len(rows)} candidates (match%% in [{args.min_pct}, {args.max_pct}])")
        for name, pct in rows:
            marker = " [prev]" if already_dispatched(name) else ""
            print(f"  {pct:6.2f}%  {name}{marker}")
        return 0

    if args.func and args.batch:
        sys.exit("pass <func> OR --batch, not both")

    if args.func:
        targets = [args.func]
    elif args.batch:
        rows = candidates(args.min_pct, args.max_pct)
        if args.skip_prepped:
            rows = [(n, p) for (n, p) in rows if not already_dispatched(n)]
        targets = [n for n, _ in rows[: args.batch]]
        if not targets:
            sys.exit("no candidates match the filter")
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
