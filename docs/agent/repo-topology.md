# Repo Topology

Three remotes, three roles. Keeping them straight prevents wasted PRs and accidental leaks of private tooling.

## The three remotes

```
upstream  →  github.com/doldecomp/melee     (source of truth; fetch only)
origin    →  github.com/davidfeira/meleeDecomp  (private working repo)
fork      →  github.com/davidfeira/melee    (public PR fork)
```

## Why two `davidfeira/...` repos?

When this project was first set up, `davidfeira/meleeDecomp` was created as a separate GitHub repo that happened to share git history with `doldecomp/melee` — but GitHub doesn't recognize it as a fork. That meant cross-repo PRs to upstream were blocked.

Later, `davidfeira/melee` was created as a *real* fork (via `gh repo fork doldecomp/melee`). Both repos coexist because they serve different purposes.

## Role of each repo

### `davidfeira/meleeDecomp` — private working repo
- Tracks `master`, which contains:
  - Everything from upstream
  - Our unique matches
  - Private tooling: `tools/permute*.py`, `tools/upstream_overlap.py`
  - Agent infra: `.claude/agents/`, `CLAUDE.md`, `docs/agent/`
  - All `decomp-notes/<func>.md` diagnostic entries
- Reviewers from doldecomp **don't see this**
- Backs up our work across machines

### `davidfeira/melee` — public PR fork
- A real GitHub fork of `doldecomp/melee`
- Used **only for clean feature branches** that get filed as PRs upstream
- Keep this tidy — anything pushed here is visible to upstream maintainers
- Naming convention for branches: `claude/<topic>` (e.g. `claude/various-stage-fighter-matches`)

### `doldecomp/melee` — upstream
- Fetch only. Never push.
- The single source of truth for what's already matched.
- `permute.py upstream-check` queries this remote.

## Workflow

### When to push where

| Action | Remote | Branch |
|--------|--------|--------|
| Daily working commits | `origin` | `master` |
| New feature work | `origin` | local feature branch, push to origin |
| **Filing a PR upstream** | `fork` | `claude/<topic>` branched off `upstream/master` |
| Fetching latest upstream | `upstream` | `master` (fetch only) |

### Filing a PR (recipe)

```bash
# 1. Make sure upstream is current
git fetch upstream master

# 2. Create a clean branch off upstream/master (no private tooling on it)
git switch -c claude/<topic> upstream/master

# 3. Cherry-pick or copy in only the .c/.h changes you want to upstream
#    (don't include CLAUDE.md, decomp-notes/, tools/permute*.py, etc.)
git checkout master -- <specific files>
git commit -m "..."

# 4. Push to the fork (NOT origin)
git push fork claude/<topic>

# 5. Open the PR (gh CLI auto-detects the fork relationship)
gh pr create --repo doldecomp/melee --base master \
    --head davidfeira:claude/<topic> --title "..." --body "..."
```

## What NOT to do

- **Don't push `master` to `fork`.** That would publish the agent infra to the public fork. The fork is for PR branches only.
- **Don't push to `upstream`.** It's not your fork.
- **Don't switch `origin` to point at the public fork.** Then `git push` (default to origin/master) would leak private state.
- **Don't put private tooling on a `claude/<topic>` branch.** Those branches are visible to upstream reviewers.

## Sanity check

`git remote -v` should always show:
```
fork      https://github.com/davidfeira/melee.git       (fetch)
fork      https://github.com/davidfeira/melee.git       (push)
origin    https://github.com/davidfeira/meleeDecomp.git (fetch)
origin    https://github.com/davidfeira/meleeDecomp.git (push)
upstream  https://github.com/doldecomp/melee            (fetch)
upstream  https://github.com/doldecomp/melee            (push)
```

If it doesn't, restore with:
```bash
git remote set-url origin https://github.com/davidfeira/meleeDecomp.git
git remote set-url fork   https://github.com/davidfeira/melee.git
```
