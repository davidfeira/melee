"""Periodic poller: snapshot active permuters and emit `permuter_state` events.

The viz uses these to keep the permuter-farm in sync with reality even when
a permuter starts/stops outside the hooked codepaths (e.g. manual launch).

Run:
    python tools/viz/poll.py            # 10s cadence
    python tools/viz/poll.py --interval 5
"""
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# permute.py does `import permute_notes` as a sibling module, so tools/ must
# be on sys.path. Project root would only be needed if we used `tools.permute`.
sys.path.insert(0, str(ROOT / "tools"))

# Import lazily so a partially-broken permute.py doesn't break viz boot.
def _list_active():
    from permute import list_active_permuters  # type: ignore
    return list_active_permuters()


def _best_score(func: str):
    nm = ROOT / "nonmatchings" / func
    if not nm.is_dir():
        return None
    import re
    best = None
    for p in nm.iterdir():
        m = re.match(r"output-(\d+)-(\d+)$", p.name)
        if m:
            s = int(m.group(1))
            if best is None or s < best:
                best = s
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=10.0)
    args = ap.parse_args()

    from viz.emit import emit  # type: ignore
    from viz.state import derive  # type: ignore

    # Bootstrap: reconcile against any machines already in the viz state from
    # prior runs / synthetic emits. Anything claimed alive in the viz but not
    # actually running gets a permuter_stop on first tick.
    try:
        snapshot = derive()
        last_set: set[str] = {m["func"] for m in snapshot.get("machines", []) if m.get("func")}
    except Exception:
        last_set = set()
    while True:
        try:
            active = _list_active()
        except Exception as e:
            print(f"[poll] active-permuters failed: {e}", file=sys.stderr)
            active = []
        funcs = {f for f, _, _ in active}

        # Started-since-last-tick
        for f, pid, is_cluster in active:
            if f not in last_set:
                emit("permuter", "permuter_start", func=f, pid=str(pid),
                     cluster=("1" if is_cluster else "0"))

        # Stopped-since-last-tick
        for f in last_set - funcs:
            emit("permuter", "permuter_stop", func=f)

        # Progress for everyone still running
        for f, pid, is_cluster in active:
            score = _best_score(f)
            emit("permuter", "permuter_state", func=f,
                 best_score=("" if score is None else str(score)),
                 cluster=("1" if is_cluster else "0"))

        last_set = funcs
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
