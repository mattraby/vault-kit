# vault-kit

Knowledge vaults that agents maintain and humans curate.

vault-kit scaffolds an Obsidian-compatible markdown knowledge base — a portable
[Open Knowledge Format (OKF) v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
bundle maintained in the [LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
style — and ships the agent workflows that keep it healthy: ingestion with a human review
checkpoint, and a lint pass that catches rot before it spreads.

**Why this exists.** Wikis die of bookkeeping: indexes go stale, links break, pages
contradict each other, and trust erodes until nobody reads them. vault-kit's bargain is that
the agent does the bookkeeping — extraction, cross-linking, indexing, logging, conformance —
and the human judges meaning. Nothing lands without human review.

**Tool-neutral by design.** The schema lives in the vault's `AGENTS.md`, which Codex and other
AGENTS.md-aware agents read natively; a one-line `CLAUDE.md` bridge imports it for
Claude Code; and the helper scripts in `.bin/` are standard-library Python and bash —
no installs. Everything is plain markdown and YAML in git: no database, no service, no
lock-in.

## Quick start (Claude Code)

```
/plugin marketplace add mattraby/vault-kit
/plugin install vault-kit@mattraby
```

Then, in any project:

```
/vault-kit:new-vault
```

and start ingesting — "ingest this deck", "add this PDF to the vault", or
`/vault-kit:ingest-source path/to/file`.

## Quick start (without the plugin)

```
npx degit mattraby/vault-kit/template my-project
```

`template/` is a ready-to-use vault with the `ingest-source` and `lint-vault` skills bundled
under `.claude/` for Claude Code. Any other agent gets the same workflows from
`vault/AGENTS.md` and the scripts in `vault/.bin/`.

## The skills

- **new-vault** — scaffolds a conformant `<project>-vault/` into the current repo. Asks four
  questions up front: the vault's name, the directory name, the **topic layout**
  (single-topic or multi-topic), and the link style — relative markdown links (the default:
  OKF-conformant, renders on GitHub, mechanically checkable) or Obsidian wikilinks (resilient
  to file moves during heavy refactoring). The vault records the choices and the tooling
  honors them.
- **ingest-source** — turns an external document (PowerPoint including speaker notes, Word,
  PDF, markdown, web page) into an archived immutable source plus cross-linked wiki pages,
  updates the indexes and log, verifies conformance, and stops for human review before
  anything is committed.
- **lint-vault** — the health check: a conformance gate, a mechanical scan (broken links,
  orphaned pages, unindexed and uncited outputs, drifted generated documents, topic coverage,
  thin pages, missing frontmatter, stale timestamps), judgment passes for contradictions and
  missing cross-links, and fixes applied only on approval.

## What a scaffolded vault looks like

```
acme-vault/
├── AGENTS.md      # the schema: layers, frontmatter rules, workflows — any agent reads this
├── CLAUDE.md      # one-line import bridge so Claude Code loads AGENTS.md
├── MEMORY.md      # committed project memory — travels with the repo
├── index.md       # root catalog
├── log.md         # append-only change history
├── .bin/          # helper scripts: vault detection, extraction, conformance check, lint scan
├── .obsidian/     # Obsidian config (link style, auto-update links on rename)
├── sources/       # raw, immutable source material
├── outputs/       # long-form documents written from the vault for readers outside it
└── wiki/          # synthesized, cross-linked concept pages — where knowledge accumulates
```

**The directory is named for the project**, not `vault/`. Obsidian takes a vault's display name
from the directory basename, so a dozen projects each holding a `vault/` are a dozen entries
called "vault" in the switcher.

Three content layers, one rule each: `sources/` is immutable (what was said), `wiki/` is owned
and maintained (what we understand), `outputs/` is published (what we tell someone else). Wiki
versus output is a question of **shape and audience, not subject** — a wiki page is one atomic
concept written for us and for agents querying the vault; an output is one whole self-contained
document written for a reader outside it, superseded rather than silently patched. Every page is
YAML frontmatter plus markdown, and `type` is the only required field. Worked examples are
included and meant to be deleted once the pattern is clear.

## One topic or several

A vault declares its layout with a `Topics:` line in `AGENTS.md`, and every script follows it.

|  | `Topics: single` (default) | `Topics: multi` |
|---|---|---|
| wiki | `wiki/<category>/` | `wiki/<topic>/<category>/` |
| sources | `sources/` | `sources/<topic>/` |
| outputs | `outputs/` | `outputs/<topic>/` |
| categories | one set for the vault | each topic picks its own |

Multi-topic exists because categories mean different things in different research areas — a
`market/` folder holding both AI-tooling competitors and venture capital sector data is two
subjects wearing one name. Pick multi when a second unrelated subject is already on the horizon;
converting later means moving every file and repointing every link. Vaults with no `Topics:`
line are single-topic, so anything scaffolded before this existed keeps working untouched.

## Memory that travels

Machine-local tool memory doesn't survive a second machine or a different agent. Scaffolded
vaults carry a committed `vault/MEMORY.md` for durable project facts, and the schema
instructs agents to record there — everything committed travels by `git pull`.

## Repo layout

- `plugins/vault-kit/` — the plugin (canonical source for skills and the vault skeletons).
  - `skills/new-vault/` — scaffolder; bundles both vault skeletons, `skeleton/`
    (single-topic) and `skeleton-multi/` (multi-topic).
  - `skills/ingest-source/` — the ingest skill.
  - `skills/lint-vault/` — the health-check skill.
- `scripts/` — canonical helper scripts (`find-vault.sh`, `check-okf.sh`, `extract_pptx.py`,
  `extract_docx.py`, `lint_scan.py`) plus `build-template.sh`, which fans them out into the
  skills and both skeletons' `.bin/` and regenerates `template/`.
- `template/` — generated, committed export of the single-topic skeleton + skills (for the
  clone path).

## Maintaining

Canonical sources are `plugins/vault-kit/` (skills, skeleton) and `scripts/` (helper
scripts). The script copies inside the skills and the skeleton's `.bin/`, and everything
under `template/`, are generated — never edit them by hand. After any change, run:

```
scripts/build-template.sh
scripts/check-okf.sh plugins/vault-kit/skills/new-vault/skeleton
scripts/check-okf.sh plugins/vault-kit/skills/new-vault/skeleton-multi
scripts/check-okf.sh template/vault
```

and commit the regenerated files.

The two skeletons are both canonical — their schema prose diverges in the sections that
describe topics, layer paths, and link depth, so a schema change means editing both. The
`check-okf.sh` runs above are what catch it when only one gets updated.

Changes to the checker or the scanner should be re-run against real vaults before release,
not just the skeletons. Backward compatibility is the constraint that matters: a vault
scaffolded by an earlier version must keep passing with no edits.

## License

[MIT](LICENSE).
