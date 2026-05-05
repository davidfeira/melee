# Decomp Investigation Notes — moved

This monolith has been split into per-function files with YAML frontmatter under
`decomp-notes/<func>.md`. Migration was performed by `tools/migrate_notes_split.py`.

**To query:**

```
python tools/permute.py notes <func>           # entry for a function (and embedding-similar ones)
python tools/permute.py notes --blocker TAG    # all entries with a tag
python tools/permute.py notes                  # tag inventory
python tools/permute.py notes --tag-inventory  # canonical tag list (validated by log-stuck)
```

**To add a new entry**, run `python tools/permute.py log-stuck <func> --tags=… --diagnosis=…` —
it writes a new file to `decomp-notes/<func>.md` with frontmatter automatically.

The legacy parser still falls back to this file if `decomp-notes/` does not exist, so
historical revisions remain readable via `git show <old-sha>:decomp-notes.md`.
