# vault-kit

Start a new **OKF / LLM-wiki knowledge vault** in seconds. vault-kit packages a proven
convention — an Obsidian-compatible, portable [Open Knowledge Format (OKF) v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
bundle maintained in the [LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
style — as a Claude Code plugin and a clone-able template. Scaffolded vaults are dual-tool:
the schema lives in `vault/AGENTS.md` (read natively by Codex and other AGENTS.md-aware
agents) with a one-line `vault/CLAUDE.md` import bridge for Claude Code, and the helper
scripts live at `vault/.bin/` where any agent can run them.

## What you get

- **`/vault-kit:new-vault`** — scaffolds a conformant `vault/` (AGENTS.md schema + CLAUDE.md
  bridge, committed MEMORY.md, `.bin/` helper scripts, `sources/` + `wiki/` with placeholder
  categories, worked examples, Obsidian config) into the current repo. Asks your link style
  up front: markdown (default, OKF-conformant) or Obsidian wikilinks — the vault declares the
  choice and the checker and lint scanner honor it.
- **`/vault-kit:ingest-source`** — turns an external document (PPTX, DOCX, PDF, Markdown, URL)
  into cross-linked vault knowledge, with a human review checkpoint. Also auto-invokes on
  requests like "ingest this deck."
- **`/vault-kit:lint-vault`** — vault health check: conformance gate, mechanical scan (broken
  links, orphans, thin pages, stale timestamps), judgment passes, fixes on approval.

## Install (Claude Code)

```
/plugin marketplace add mattraby/vault-kit
/plugin install vault-kit@mattraby
```

Then, in any project: `/vault-kit:new-vault` and start ingesting.

## Use without Claude Code

```
npx degit mattraby/vault-kit/template my-project
```

`template/` is a ready-to-use vault with the `ingest-source` and `lint-vault` skills bundled
under `.claude/`. Codex and other agents get the same workflows through `vault/AGENTS.md` and
the scripts in `vault/.bin/`.

## Memory that travels

Machine-local tool memory doesn't survive a second machine or a different agent. Scaffolded
vaults carry a committed `vault/MEMORY.md` (frontmatter `type: Memory`) for durable project
facts; the schema instructs agents to record there, not only in machine-local memory.

## Repo layout

- `plugins/vault-kit/` — the plugin (canonical source for skills and the vault skeleton).
  - `skills/new-vault/` — scaffolder; bundles the vault skeleton in `skeleton/`.
  - `skills/ingest-source/` — the ingest skill.
  - `skills/lint-vault/` — the health-check skill.
- `scripts/` — canonical helper scripts (`check-okf.sh`, `extract_pptx.py`, `extract_docx.py`,
  `lint_scan.py`) plus `build-template.sh`, which fans them out into the skills and the
  skeleton's `.bin/` and regenerates `template/`.
- `template/` — generated, committed export of the skeleton + skills (for the clone path).

## Maintaining

Canonical sources are `plugins/vault-kit/` (skills, skeleton) and `scripts/` (helper scripts).
The script copies inside the skills and the skeleton's `.bin/`, and everything under
`template/`, are generated — never edit them by hand. After any change, run:

```
scripts/build-template.sh
scripts/check-okf.sh plugins/vault-kit/skills/new-vault/skeleton
scripts/check-okf.sh template/vault
```

and commit the regenerated files.
