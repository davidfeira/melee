"""Tiny HTTP+SSE server for the decomp town viz.

Routes:
    GET /         -> town.html
    GET /events   -> SSE stream tailing events.jsonl
    GET /history  -> all current events as JSON (initial state)
    GET /state    -> per-function state from tools/state/state.py (truthful match%)

Run:
    python tools/viz/serve.py            # http://localhost:7777/
    VIZ_PORT=8000 python tools/viz/serve.py
"""
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import time
from pathlib import Path

# Make tools/ importable so we can pull from state.state without packaging it.
_TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
try:
    from state import state as _state_mod  # type: ignore
except Exception:  # pragma: no cover — viz still works without state file
    _state_mod = None

try:
    import psutil
except Exception:
    psutil = None

# Background CPU sampler — single thread that ticks every 1s and stores the
# latest per-core / total %. The /cpu endpoint just reads the cache. Avoids
# the multi-threaded request handler racing psutil's baseline.
_cpu_state = {"cores": [], "total": 0.0}

def _upstream_fetcher():
    """Periodically refresh the upstream/master ref so the master log
    reflects recently-merged PRs without manual fetches.
    """
    # Skip the first interval — SessionStart hook just fetched.
    while True:
        time.sleep(600)  # 10 min
        try:
            _run(["git", "-C", str(REPO_ROOT),
                  "fetch", "upstream", "master", "--quiet"], timeout=60)
        except Exception:
            pass


def _cpu_sampler():
    if psutil is None:
        return
    # Priming call so the first sample isn't 0.
    psutil.cpu_percent(interval=None, percpu=True)
    psutil.cpu_percent(interval=None)
    while True:
        time.sleep(1.0)
        try:
            _cpu_state["cores"] = psutil.cpu_percent(interval=None, percpu=True)
            _cpu_state["total"] = psutil.cpu_percent(interval=None)
        except Exception:
            pass

ROOT = Path(__file__).parent
EVENTS = ROOT / "events.jsonl"
REPO_ROOT = ROOT.parent.parent  # tools/viz/ -> repo root
NOTES_DIR = REPO_ROOT / "decomp-notes"


def _run(cmd, timeout=10):
    # Force utf-8 — git emits messages with non-cp1252 chars (Japanese commit
    # subjects, accented author names) which crash the default Windows codec.
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.stdout


_FRONTMATTER_RX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_FUZZY_RX = re.compile(r"\*\*Best fuzzy:\*\*\s*([\d.]+%)")


def _parse_note_frontmatter(path: Path) -> dict:
    """Lightweight YAML-ish frontmatter parser. Handles `key: value` and
    `tags: [a, b]` — the only two shapes our log-stuck writes."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = _FRONTMATTER_RX.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if k == "tags" and v.startswith("[") and v.endswith("]"):
            out[k] = [t.strip() for t in v[1:-1].split(",") if t.strip()]
        elif k == "headline" and v.startswith('"') and v.endswith('"'):
            out[k] = v[1:-1]
        else:
            out[k] = v
    return out


def _extract_fuzzy(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _FUZZY_RX.search(text)
    return m.group(1) if m else None


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_POST(self):
        if self.path.startswith("/permuter-mode"):
            self._permuter_mode("POST")
        elif self.path == "/events":
            self._post_event()
        else:
            self.send_response(404)
            self.end_headers()

    def _post_event(self):
        """Accept one event JSON object, append to events.jsonl. Public
        contract — see EVENTS.md. Server fills in `t` if absent."""
        length = int(self.headers.get("Content-Length") or "0")
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid json"}')
            return
        if "event" not in body:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"missing event field"}')
            return
        body.setdefault("v", 1)
        body.setdefault("t", time.time())
        body.setdefault("actor", "external")
        try:
            EVENTS.parent.mkdir(parents=True, exist_ok=True)
            with open(EVENTS, "a", encoding="utf-8") as f:
                f.write(json.dumps(body) + "\n")
        except OSError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        out = json.dumps({"ok": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):
        if self.path == "/events":
            self._stream()
        elif self.path == "/history":
            self._history()
        elif self.path == "/master-log":
            self._master_log()
        elif self.path == "/state":
            self._state()
        elif self.path.startswith("/note?"):
            self._note()
        elif self.path == "/cpu":
            self._cpu()
        elif self.path == "/refresh-upstream":
            self._refresh_upstream()
        elif self.path.startswith("/permuter-mode"):
            self._permuter_mode("GET")
        elif self.path in ("/", ""):
            self.path = "/town.html"
            super().do_GET()
        else:
            super().do_GET()

    def _history(self):
        EVENTS.touch(exist_ok=True)
        try:
            text = EVENTS.read_text(encoding="utf-8")
        except OSError:
            text = ""
        events = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        body = json.dumps(events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _permuter_mode(self, method: str):
        """GET: returns {mode: 'on'|'off'}. POST with body {mode: 'on'|'off'}
        flips the toggle. permute.py reads this file before launching any
        permuter and bails when off."""
        path = ROOT / "permuter_mode.txt"
        if method == "POST":
            length = int(self.headers.get("Content-Length") or "0")
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                body = {}
            mode = (body.get("mode") or "").lower()
            if mode in ("on", "off"):
                path.write_text(mode, encoding="utf-8")
        cur = path.read_text(encoding="utf-8").strip().lower() if path.exists() else "on"
        if cur not in ("on", "off"):
            cur = "on"
        body = json.dumps({"mode": cur}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _refresh_upstream(self):
        """Run `git fetch upstream master` and report duration."""
        t0 = time.time()
        try:
            _run(["git", "-C", str(REPO_ROOT),
                  "fetch", "upstream", "master", "--quiet"], timeout=60)
            payload = {"ok": True, "took_s": round(time.time() - t0, 2)}
        except Exception as e:
            payload = {"ok": False, "error": str(e)}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cpu(self):
        """Per-core CPU% snapshot. Reads the cache populated by _cpu_sampler."""
        if psutil is None:
            payload = {"cores": [], "total": 0, "error": "psutil not installed"}
        else:
            payload = {"cores": list(_cpu_state["cores"]),
                       "total": _cpu_state["total"]}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _note(self):
        """Return raw markdown body of decomp-notes/<func>.md for drill-down."""
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query).get("func", [""])[0]
        # Strict allow-list — only accept the func-name shape we use as
        # filenames (alphanumeric + underscore). Stops path traversal.
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", q):
            self.send_response(400)
            self.end_headers()
            return
        path = NOTES_DIR / f"{q}.md"
        try:
            text = path.read_text(encoding="utf-8") if path.exists() else ""
        except OSError:
            text = ""
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _state(self):
        """Truthful per-function state from build/GALE01/report.json + notes.jsonl.

        Returns: {"funcs": [{name, tu, match_percent, status, notes}, ...],
                  "summary": {status: count}}.

        Status values:
          matched         match_percent == 100.0
          near            95.0 <= mp < 100.0
          partial         0 < mp < 95.0
          not_started     mp is None
          + manual overrides via notes.jsonl: permuter-queued, blocked,
            ready-to-ship, ignored
        """
        if _state_mod is None:
            payload = {"error": "tools/state not importable", "funcs": []}
        else:
            try:
                states = _state_mod.load_state()
                payload = {
                    "funcs": [s.to_dict() for s in states],
                    "summary": _state_mod.summarize(states),
                    "source": "build/GALE01/report.json + tools/state/notes.jsonl",
                }
            except Exception as e:
                payload = {"error": str(e), "funcs": []}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _master_log(self):
        """Aggregate every function we've ever worked on across all sessions.

        Source-of-truth is now build/GALE01/report.json + tools/state/notes.jsonl
        (via tools.state.state). Commit log is consulted only for author/timestamp
        enrichment — never to determine whether a function actually matches.
        That eliminates the failure mode where a hand-typed "Match X" commit
        labels a 99% near-miss as matched.

        Classification:
        - matched-upstream: state==matched and TU is `Matching` in upstream
                            (linked into upstream's binary)
        - matched-local:    state==matched but TU still NonMatching upstream
                            (waiting on PR)
        - near:             state==near (95-99.99% — auto permuter candidate)
        - partial:          state==partial (<95%)
        - not_started:      no .c body
        - queued/blocked:   manual annotation in notes.jsonl
        """
        try:
            body = json.dumps(self._derive_master_log()).encode()
        except Exception as e:
            body = json.dumps({"error": str(e), "funcs": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _derive_master_log(self):
        funcs = {}  # name -> {state, fuzzy, tags, commit, headline, author, ts, tu}

        # 1. Parse all decomp-notes — these are the stuck/queued funcs.
        # Pull author/timestamp from git log of the notes file (single batch).
        notes_meta = self._git_authors_for_dir("decomp-notes")
        if NOTES_DIR.is_dir():
            for note in NOTES_DIR.glob("*.md"):
                meta = _parse_note_frontmatter(note)
                if not meta.get("function"):
                    continue
                name = meta["function"]
                tags = meta.get("tags", [])
                fuzzy = _extract_fuzzy(note)
                # Match the viz's PERMUTER_TAG_RX: any tag that means
                # "permuter-ready, waiting on cycles" routes to queue.
                queued = any(
                    t in ("permuter-dispatched", "permuter-territory",
                          "permuter-blocked", "permuter-ready")
                    or t.startswith("permuter-queued")
                    for t in tags
                )
                rel_path = f"decomp-notes/{note.name}"
                am = notes_meta.get(rel_path, {})
                funcs[name] = {
                    "state": "queued" if queued else "stuck",
                    "fuzzy": fuzzy,
                    "tags": tags,
                    "headline": meta.get("headline", ""),
                    "commit": None,
                    "author": am.get("author"),
                    "ts": am.get("ts"),
                    "tu": meta.get("tu", ""),
                }

        # 2. Walk git log --all for Match / Improve commits — newest wins.
        # Single shot: parse %H, author, timestamp, subject for ALL commits.
        try:
            log = _run(["git", "-C", str(REPO_ROOT),
                        "log", "--all", "--pretty=format:%H\t%an\t%at\t%s"],
                       timeout=20)
        except Exception:
            log = ""
        match_rx = re.compile(r"^Match\s+([A-Za-z_][A-Za-z0-9_]*)\b")
        improve_rx = re.compile(r"^Improve\s+([A-Za-z_][A-Za-z0-9_]*)\s+to\s+([\d.]+%)")
        for line in log.splitlines():
            parts = line.split("\t", 3)
            if len(parts) < 4:
                continue
            sha, author, ts_str, msg = parts
            try:
                ts = int(ts_str)
            except ValueError:
                ts = None
            m = match_rx.match(msg)
            if m:
                name = m.group(1)
                e = funcs.setdefault(name, {"tags": [], "headline": "", "tu": ""})
                if e.get("state") not in ("matched-upstream",):
                    e.update({"state": "matched-local", "commit": sha[:9],
                              "fuzzy": "100%", "author": author, "ts": ts})
                continue
            m = improve_rx.match(msg)
            if m:
                name, pct = m.group(1), m.group(2)
                e = funcs.setdefault(name, {"tags": [], "headline": "", "tu": ""})
                if e.get("state") not in ("matched-local", "matched-upstream"):
                    e.update({"state": "improved", "commit": sha[:9],
                              "fuzzy": e.get("fuzzy") or pct,
                              "author": author, "ts": ts})

        # 3. Cross-check upstream/master — funcs whose Match landed publicly.
        try:
            upstream_log = _run(["git", "-C", str(REPO_ROOT),
                                  "log", "upstream/master", "--pretty=format:%s"],
                                 timeout=15)
        except Exception:
            upstream_log = ""
        upstream_matched = set()
        for msg in upstream_log.splitlines():
            m = match_rx.match(msg)
            if m:
                upstream_matched.add(m.group(1))
        for name, e in funcs.items():
            if name in upstream_matched and e.get("state", "").startswith("matched"):
                e["state"] = "matched-upstream"

        # 4. Mark "this session" funcs by cross-referencing events.jsonl.
        session_funcs = set()
        if EVENTS.exists():
            try:
                for line in EVENTS.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    f = ev.get("func")
                    if f:
                        session_funcs.add(f)
            except OSError:
                pass
        for name, e in funcs.items():
            e["this_session"] = name in session_funcs

        # 4b. Truthful state override — replace commit-message-derived state with
        # build/GALE01/report.json + tools/state/notes.jsonl. The commit-log walk
        # above is preserved purely to populate author/commit/ts metadata.
        if _state_mod is not None:
            try:
                states = {s.name: s for s in _state_mod.load_state()}
            except Exception:
                states = {}
            for name, e in funcs.items():
                s = states.get(name)
                if s is None:
                    continue
                ds = s.derived_status
                # Map state.derived_status → master-log "state" enum.
                if ds == "matched":
                    e["state"] = "matched-upstream" if name in upstream_matched else "matched-local"
                elif ds == "near":
                    e["state"] = "near"
                elif ds == "partial":
                    e["state"] = "improved"
                elif ds == "not_started":
                    e["state"] = "not_started"
                elif ds == "permuter-queued":
                    e["state"] = "queued"
                elif ds == "blocked":
                    e["state"] = "stuck"
                elif ds == "ready-to-ship":
                    e["state"] = "matched-local"
                # Always replace fuzzy with the truthful number.
                if s.match_percent is not None:
                    e["fuzzy"] = f"{s.match_percent:.2f}%"

        # 5. Get current user email/name to mark "mine" rows.
        try:
            me_email = _run(["git", "-C", str(REPO_ROOT),
                              "config", "user.email"], timeout=5).strip()
            me_name = _run(["git", "-C", str(REPO_ROOT),
                             "config", "user.name"], timeout=5).strip()
        except Exception:
            me_email = me_name = ""

        out = [{"name": n, **e} for n, e in funcs.items()]
        return {"funcs": out, "me": {"email": me_email, "name": me_name}}

    def _git_authors_for_dir(self, rel_dir: str) -> dict:
        """For each file in `rel_dir`, return last-touched {author, ts}.
        One git log call, parsed with --name-only.
        """
        try:
            out = _run(["git", "-C", str(REPO_ROOT),
                        "log", "--all", "--name-only",
                        "--pretty=format:__C__%an\t%at",
                        "--", rel_dir],
                       timeout=20)
        except Exception:
            return {}
        authors = {}
        cur_author = cur_ts = None
        for line in out.splitlines():
            if line.startswith("__C__"):
                rest = line[5:]
                if "\t" in rest:
                    cur_author, ts_str = rest.split("\t", 1)
                    try:
                        cur_ts = int(ts_str)
                    except ValueError:
                        cur_ts = None
            elif line and cur_author:
                # Newest commit first; only record first sighting per file.
                if line not in authors:
                    authors[line] = {"author": cur_author, "ts": cur_ts}
        return authors

    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        EVENTS.touch(exist_ok=True)
        try:
            f = open(EVENTS, "r", encoding="utf-8")
        except OSError:
            return
        f.seek(0, 2)  # tail from end
        last_keepalive = time.time()
        try:
            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        self.wfile.write(f"data: {line}\n\n".encode())
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        break
                else:
                    if time.time() - last_keepalive > 15:
                        try:
                            self.wfile.write(b": keepalive\n\n")
                            self.wfile.flush()
                            last_keepalive = time.time()
                        except (BrokenPipeError, ConnectionResetError):
                            break
                    time.sleep(0.3)
        finally:
            f.close()

    def log_message(self, *a, **k):
        pass


class ThreadedServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    import threading
    threading.Thread(target=_cpu_sampler, daemon=True).start()
    threading.Thread(target=_upstream_fetcher, daemon=True).start()
    port = int(os.environ.get("VIZ_PORT", "7777"))
    with ThreadedServer(("127.0.0.1", port), Handler) as httpd:
        print(f"[viz] http://localhost:{port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
