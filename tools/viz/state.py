"""Derive current viz state from events.jsonl — mirrors town.html.

Lets the operator (or another agent) inspect what the viz *should* be rendering
without scraping the browser. Run `python tools/viz/state.py` for a summary or
`python tools/viz/state.py --json` for raw state.

Source-of-truth fields tracked:
- agents_in_flight: dispatched, no terminal event yet
- machines: active permuters (permuter_start without permuter_stop)
- matched / stuck: cumulative trophies
- log: tail of recent events
"""
import argparse
import json
import sys
from pathlib import Path

EVENTS = Path(__file__).parent / "events.jsonl"


def derive():
    agents = {}              # tool_use_id -> {subagent, func, agent_id, t}
    by_agent_id = {}         # agent_id -> tool_use_id
    machines = {}            # func -> {cluster, score, t}
    matched = []
    stuck = []
    events = []
    # Cumulative session counters — match town.html HUD semantics.
    permuters_started_total = 0

    if not EVENTS.exists():
        return _shape(agents, machines, matched, stuck, events)

    with open(EVENTS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(e)
            ev = e.get("event")
            if ev == "dispatch":
                tid = e.get("tool_use_id")
                if tid:
                    agents[tid] = {
                        "subagent": e.get("subagent"),
                        "func": e.get("func"),
                        "agent_id": None,
                        "description": e.get("description"),
                        "t": e.get("t"),
                    }
            elif ev == "agent_link":
                tid = e.get("tool_use_id")
                aid = e.get("agent_id")
                if tid in agents and aid:
                    agents[tid]["agent_id"] = aid
                    by_agent_id[aid] = tid
            elif ev == "agent_done":
                tid = e.get("tool_use_id")
                aid = e.get("agent_id")
                if tid and tid in agents:
                    agents.pop(tid, None)
                    if aid:
                        by_agent_id.pop(aid, None)
                elif aid and aid in by_agent_id:
                    tid = by_agent_id.pop(aid)
                    agents.pop(tid, None)
            elif ev == "permuter_start":
                f_ = e.get("func")
                if f_:
                    if f_ not in machines:
                        permuters_started_total += 1
                    machines[f_] = {
                        "cluster": e.get("cluster") == "1",
                        "score": None,
                        "t": e.get("t"),
                    }
                    # Mirrors town.html: handoff retires the attempter agent
                    # that owned this func (it "walked the work to the farm").
                    _retire_by_func(agents, by_agent_id, f_)
            elif ev == "permuter_state":
                f_ = e.get("func")
                if f_ in machines:
                    s = e.get("best_score")
                    machines[f_]["score"] = None if s in (None, "") else s
            elif ev == "permuter_stop":
                machines.pop(e.get("func"), None)
            elif ev == "match":
                matched.append({"func": e.get("func"), "t": e.get("t")})
                machines.pop(e.get("func"), None)
                # match also implicitly retires the agent that owned the func
                _retire_by_func(agents, by_agent_id, e.get("func"))
            elif ev in ("log_stuck", "stuck"):
                stuck.append({"func": e.get("func"), "tags": e.get("tags"), "t": e.get("t")})
                _retire_by_func(agents, by_agent_id, e.get("func"))

    return _shape(agents, machines, matched, stuck, events,
                  permuters_started_total)


def _retire_by_func(agents, by_agent_id, func):
    if not func:
        return
    for tid, a in list(agents.items()):
        if a.get("func") == func:
            aid = a.get("agent_id")
            agents.pop(tid, None)
            if aid:
                by_agent_id.pop(aid, None)


def _shape(agents, machines, matched, stuck, events, permuters_started_total):
    return {
        "agents_in_flight": list(agents.values()),
        "machines": [{"func": k, **v} for k, v in machines.items()],
        "matched": matched,
        "stuck": stuck,
        "log_tail": events[-20:],
        "totals": {
            "matched": len(matched),
            "stuck": len(stuck),
            "permuters_started": permuters_started_total,
            "agents_in_flight": len(agents),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="raw JSON dump")
    args = ap.parse_args()
    s = derive()
    if args.json:
        json.dump(s, sys.stdout, indent=2)
        print()
        return
    print(f"agents in flight: {len(s['agents_in_flight'])}")
    for a in s["agents_in_flight"]:
        func = a.get("func") or "(no func)"
        sub = a.get("subagent") or "agent"
        aid = (a.get("agent_id") or "?")[:10]
        print(f"  {sub:20} {func:32} agent_id={aid}")
    print(f"machines: {len(s['machines'])}")
    for m in s["machines"]:
        tag = "[cluster]" if m.get("cluster") else "[local]  "
        score = m.get("score") or "-"
        print(f"  {tag} {m['func']:32} score={score}")
    t = s["totals"]
    print(
        f"session totals: matched={t['matched']}  stuck={t['stuck']}  "
        f"permuters_started={t['permuters_started']}  "
        f"agents_in_flight={t['agents_in_flight']}"
    )


if __name__ == "__main__":
    main()
