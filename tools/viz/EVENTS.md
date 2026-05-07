# Decomp Town event schema (v1)

The viz, master log, and work log all derive from a single append-only event
log at `tools/viz/events.jsonl`. Any orchestrator/harness can drive the
visualization by appending events in this format. Subscribe live via SSE on
`GET /events`, replay history via `GET /history`, or POST one event at a
time to `POST /events`.

## Common fields

Every event line is a JSON object with at least:

```
{
  "v": 1,            // schema version (defaults to 1 if omitted)
  "t": 1778100000.0, // unix timestamp (server fills in if absent)
  "actor": "...",    // who emitted: "mama", "permute", "permuter", or a custom name
  "event": "..."     // event type — see below
}
```

Additional fields are event-specific.

## Event types

### Agent lifecycle (driven by the orchestrator / harness)

| event             | required fields            | optional       | semantics |
|-------------------|----------------------------|----------------|-----------|
| `dispatch`        | `subagent`                 | `func`, `description`, `tool_use_id` | Parent agent kicked off a subagent. `tool_use_id` is the harness's per-invocation id (Claude Code's `tool_use_id`, codex's call id, etc.). |
| `agent_link`      | `tool_use_id`, `agent_id`  |                | Backgrounded subagent is now running. Bridges the dispatch's `tool_use_id` to the subagent's persistent `agent_id` so a later termination can be matched. Foreground (synchronous) subagents skip this — they emit `agent_done` directly. |
| `agent_done`      | one of `tool_use_id` or `agent_id` | `last_message` | Subagent finished. The viz retires the sprite. |
| `agent_activity`  | `agent_id`, `tool`, `summary` |             | A subagent invoked a tool — used for the speech-bubble feed. Optional; omit if your harness can't surface this. |
| `mama_activity`   | `tool`, `summary`          |                | Main-thread (orchestrator/parent) tool call — drives the bubble above Mama. Optional. |

### Decomp lifecycle (driven by `permute.py`)

| event             | required fields            | optional       | semantics |
|-------------------|----------------------------|----------------|-----------|
| `match`           | `func`                     | `sha`, `fuzzy` | Function reached 100% and was committed. |
| `stuck`           | `func`                     | `tags`, `fuzzy` | Function `log-stuck`'d. Tags drive routing: if any tag matches the permuter-queued family (`permuter-dispatched`, `permuter-queued*`, `permuter-territory`, `permuter-blocked`, `permuter-ready`) the func goes to the **Permuter Queue** zone; otherwise the **Stuck Shelf**. |
| `permuter_start`  | `func`                     | `cluster` ("0"/"1"), `pid` | A permuter is now running on `func`. Emitted by `tools/viz/poll.py` from pidfile presence — orchestrators usually don't emit this directly. |
| `permuter_state`  | `func`                     | `best_score`, `cluster` | Score update from a running permuter. |
| `permuter_stop`   | `func`                     |                | Permuter exited. |

### Picker / discovery

| event             | required fields | optional       | semantics |
|-------------------|-----------------|----------------|-----------|
| `brief`           | `func`          | `recommendation`, `fuzzy`, `strict`, `total_mismatches`, `classes`, `tu_stucks` | An agent ran `permute.py prep` (or `compact-brief`) — surfaces the func into the **Picker Queue** zone. |
| `picked`          | `func`          |                | Lighter-weight equivalent of `brief` — adds to picker without metadata. |

## Event-flow contract

A typical lifecycle for one in-flight subagent:

```
{event:"dispatch",   tool_use_id:"x", subagent:"match-attempter", func:"fn_X"}
{event:"agent_link", tool_use_id:"x", agent_id:"a1234"}
{event:"agent_activity", agent_id:"a1234", tool:"Bash", summary:"permute.py prep fn_X ..."}
{event:"agent_activity", agent_id:"a1234", tool:"Edit", summary:"edit src/...c"}
{event:"agent_activity", agent_id:"a1234", tool:"Bash", summary:"permute.py diff fn_X"}
{event:"match",      func:"fn_X", sha:"abc1234", fuzzy:"100.0"}
{event:"agent_done", agent_id:"a1234", last_message:"matched fn_X"}
```

Or, if the agent gets stuck instead of matching:

```
{event:"dispatch",   tool_use_id:"x", subagent:"match-attempter", func:"fn_X"}
{event:"agent_link", tool_use_id:"x", agent_id:"a1234"}
... activity ...
{event:"stuck",      func:"fn_X", tags:["regalloc","permuter-territory"], fuzzy:"94.6%"}
{event:"agent_done", agent_id:"a1234", last_message:"logged stuck"}
```

For foreground (synchronous) dispatches you can skip `agent_link` — emit
`agent_done` keyed on `tool_use_id` instead.

## How to emit

Three options, pick whichever your harness can do:

1. **CLI**: `python tools/viz/emit.py <actor> <event> [k=v ...]`
2. **Python lib**: `from viz.emit import emit; emit("mama", "dispatch", func="fn_X", tool_use_id="x")`
3. **HTTP**: `POST /events` with a JSON body shaped like one event line.

All three append to `events.jsonl` and broadcast to SSE subscribers.

## Versioning

Field set is stable as `v: 1`. Breaking changes will bump to `v: 2` and the
server will accept both shapes for at least one minor version.
