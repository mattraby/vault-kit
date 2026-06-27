# vault-kit — Design Spec

**Date:** 2026-06-27
**Status:** Approved (brainstorming) — ready for implementation plan
**Repo:** `github.com/mattraby/vault-kit` (personal org)
**Local:** `/Users/matt/Development/mattraby/vault-kit`

## Problem

The Promethean engagement built a research knowledge base as an Obsidian vault that is
simultaneously a portable **Open Knowledge Format (OKF) v0.1** bundle, maintained in the
**LLM-wiki** style (an LLM curates a markdown knowledge base between us and raw sources). A
companion `ingest-source` skill turns external documents (PPTX, PDF, Markdown, URLs) into vault
knowledge following a fixed workflow.

This convention is good and we want to reuse it. Today it is fused to one engagement: the vault
skeleton lives inside the `promethean` repo and the ingest skill is project-local and hardcoded
to "the Promethean vault." There is no quick way to start a new project on the same standard.

## Goal

A single, reusable package that lets anyone start a new OKF/LLM-wiki vault in seconds, with the
ingest skill available, without copy-pasting from Promethean.

**Non-goals:** the SharePoint spike, customer deliverables, `docs/patterns`, and Azure
identity material from the Promethean repo. Those are engagement-specific and excluded.

## Decisions (from brainstorming)

| Decision | Choice | Rationale |
|---|---|---|
| Packaging form | **Plugin + template (hybrid)** | One source of truth (the `template/` dir), two entry points: a Claude Code plugin for `/new-vault` ergonomics, and a clone-able template for non-Claude-Code users. |
| Home | **New standalone repo** `mattraby/vault-kit` | Personal org; clean separation from any single engagement; the "standards home" the Promethean log anticipated. |
| Ingest skill home | **Plugin-global + template copy** | The plugin ships `ingest-source` globally (available in every project without copying); the template carries a copy for raw clones. One logical skill, two physical copies, one-way sync. |
| Scaffold copy behavior | **Skeleton only for plugin users** | `/new-vault` copies the `vault/` skeleton but not a local ingest skill, since the plugin already provides it globally. Avoids a redundant local copy shadowing the global one. The template's local copy exists solely for the clone-without-Claude-Code path. |
| Sync direction | **Plugin copy is canonical** | `scripts/sync-ingest.sh` mirrors the plugin's `ingest-source` into the template at release time. |

## Architecture

### Repo layout

```
vault-kit/
├── .claude-plugin/
│   └── marketplace.json          # repo is an addable marketplace: /plugin marketplace add mattraby/vault-kit
├── plugins/
│   └── vault-kit/
│       ├── plugin.json           # plugin manifest (name, version, description, skills)
│       └── skills/
│           ├── new-vault/
│           │   └── SKILL.md       # scaffolds a vault skeleton into the current repo
│           └── ingest-source/
│               ├── SKILL.md       # generalized ingest skill (canonical copy)
│               └── scripts/
│                   └── extract_pptx.py
├── template/                      # THE single source of truth for a new vault
│   ├── vault/                     # full OKF/LLM-wiki skeleton (see "Template contents")
│   │   ├── CLAUDE.md
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── .obsidian/             # config: relative md links, NOT wikilinks
│   │   ├── sources/
│   │   │   ├── index.md
│   │   │   ├── example-source.md
│   │   │   └── attachments/.gitkeep
│   │   └── wiki/
│   │       ├── index.md
│   │       ├── domain/{index.md, example-concept.md}
│   │       ├── stakeholders/index.md
│   │       ├── market/index.md
│   │       ├── requirements/index.md
│   │       └── architecture/index.md
│   └── .claude/
│       └── skills/
│           └── ingest-source/     # baked-in copy for non-Claude-Code cloners (synced from plugin)
├── scripts/
│   └── sync-ingest.sh             # copies plugins/vault-kit/skills/ingest-source -> template/.claude/skills/ingest-source
├── docs/
│   └── superpowers/specs/2026-06-27-vault-kit-design.md   # this file
├── .gitignore                     # ignore .DS_Store etc.
└── README.md                      # what this is + both entry points + how to update
```

### Components and responsibilities

Each component has one purpose, a clear interface, and explicit dependencies.

1. **`template/vault/` — the skeleton (data, not code).**
   What it does: a faithful, de-Prometheanized copy of the current Promethean vault skeleton — a
   valid OKF bundle on day one. Interface: a directory tree of markdown + `.obsidian/` config.
   Depends on: nothing. This is the artifact every entry point ultimately produces.

   De-Prometheanization required:
   - `CLAUDE.md` title `# Promethean Vault — Schema & Operating Manual` → generic
     (`# {{VAULT_NAME}} Vault — Schema & Operating Manual`, substituted at scaffold time;
     for the raw-clone path it ships as a neutral default like `# Knowledge Vault — Schema...`).
   - The CLAUDE.md body is already generic (placeholder categories, OKF rules) — keep as-is.
   - `index.md` / `log.md` headers carry no Promethean specifics beyond the title line — neutralize.
   - Keep the worked-example pair (`example-source.md` ↔ `example-concept.md`) and their
     `[!example]` "delete after sign-off" callouts: they teach the Source and Concept conventions.
     These examples are about OKF itself (the Google Cloud blog + format), so they stay generic.
   - Keep `.obsidian/` config verbatim — it is what makes Obsidian emit relative markdown links
     instead of `[[wikilinks]]`, which is load-bearing for OKF portability.

2. **`plugins/vault-kit/skills/new-vault/SKILL.md` — the scaffolder.**
   What it does: scaffolds a new vault into the current working repo. Interface: invoked by the
   user in Claude Code (`/new-vault` or natural language). Depends on: `template/vault/` resolved
   via the plugin's own install path (`${CLAUDE_PLUGIN_ROOT}` or equivalent — the plan pins the
   exact env/path mechanism against current Claude Code docs).

   Behavior:
   - Prompt for a **vault/project name** (used to title `CLAUDE.md` and root `index.md`). No other
     parameters — categories stay as the placeholders the convention already tells you to rename
     per-PRD (YAGNI; renaming is a documented step).
   - Target: `vault/` in the current repo root. If `vault/` already exists, stop and ask rather
     than overwrite.
   - Copy `template/vault/` → `./vault/`, substituting the vault name into the title lines.
   - Seed `log.md`'s first entry stamped with today's date:
     `- init | Vault scaffolded per LLM-wiki + OKF v0.1`.
   - Do **not** write a project-local `ingest-source` (the plugin provides it globally).
   - Print next steps: open `vault/` in Obsidian, read `CLAUDE.md`, rename placeholder categories,
     then ingest your first source.

3. **`plugins/vault-kit/skills/ingest-source/` — the generalized ingest skill (canonical).**
   What it does: turns one external source into vault knowledge via the 6-step Ingest workflow.
   Interface: the existing SKILL.md, unchanged in logic. Depends on: a vault at `vault/CLAUDE.md`
   in the working repo; bundled `scripts/extract_pptx.py` (stdlib only).

   Generalization required (wording only, no logic change):
   - Frontmatter `name`/`description`: drop "Promethean"; refer to "the knowledge vault."
   - Body: replace "the Promethean vault" with "the knowledge vault"; locate the convention at
     `vault/CLAUDE.md` (the nearest `vault/` containing a `CLAUDE.md`). Everything else — routing
     table, archive/source/synthesize/index/log steps, the review checkpoint, the script docs —
     stays verbatim.

4. **`template/.claude/skills/ingest-source/` — the clone-path copy (derived).**
   What it does: identical content to component 3, present so a raw `degit`/clone of `template/`
   is fully functional without the plugin. Interface: none (it is data). Depends on: kept current
   by `scripts/sync-ingest.sh`. Never edited directly.

5. **`scripts/sync-ingest.sh` — the sync tool.**
   What it does: `rsync`/`cp` the canonical plugin `ingest-source` over the template copy, so the
   two never drift. Interface: run manually before a release/commit that touches the skill.
   Depends on: the two paths. One-way, plugin → template. A short README note and (optionally) a
   pre-commit hook or CI check can warn if the two diverge — deferred unless wanted.

6. **`.claude-plugin/marketplace.json` + `plugins/vault-kit/plugin.json` — distribution manifests.**
   What they do: make the repo installable as a Claude Code plugin marketplace and describe the
   plugin/skills. Interface: consumed by `/plugin marketplace add` and `/plugin install`. Depends
   on: current Claude Code plugin schema — the implementation plan confirms exact field names and
   the skills-discovery convention (e.g. `skills/<name>/SKILL.md`) against live docs, since the
   schema evolves. (A `claude-code-guide` agent can verify the current format during planning.)

### Data flow

```
                         template/vault/  (single source of truth)
                                 │
        ┌────────────────────────┼─────────────────────────────┐
        │ (plugin path)          │                  (clone path)│
        ▼                        │                              ▼
  /new-vault skill               │                    degit mattraby/vault-kit/template
  copies skeleton +              │                    -> working vault WITH baked-in
  substitutes name               │                       .claude/skills/ingest-source
  -> ./vault/                    │                       (synced from plugin)
        │                        │
        ▼                        ▼
  new project's vault/   +  ingest-source available globally (plugin installed)
        │
        ▼
  user runs ingest-source -> reads vault/CLAUDE.md -> writes sources/ + wiki/, updates index/log
```

### Error handling

- **`vault/` already exists** when scaffolding → stop and ask; never overwrite an existing vault.
- **Plugin not installed but template cloned** → the clone carries its own `.claude/skills/ingest-source`, so ingest still works locally.
- **Template/plugin skill drift** → `sync-ingest.sh` is the guard; the README documents that the
  plugin copy is canonical and the template copy is generated.
- **Plugin manifest schema mismatch** (Claude Code changed the format) → caught at install time;
  the plan pins the schema against current docs to minimize this.

## Distribution / usage

- **Claude Code users:**
  `/plugin marketplace add mattraby/vault-kit` → `/plugin install vault-kit` →
  `new-vault` and `ingest-source` are available in every project.
- **Anyone else:**
  `degit mattraby/vault-kit/template myproject` (or split `template/` into a GitHub "template
  repo" later for the "Use this template" button) → a working vault with ingest baked in.

## Testing

- **Scaffold smoke test:** run `/new-vault` in an empty temp repo; assert the produced `vault/`
  is a valid OKF bundle — every non-reserved `.md` has non-empty `type` frontmatter; `index.md`
  and `log.md` carry no frontmatter; links are relative `.md` links, no `[[wikilinks]]`; the
  vault name was substituted; the `init` log entry exists.
- **Clone smoke test:** `degit template/` into a temp dir; assert the same OKF checks pass and
  `.claude/skills/ingest-source/SKILL.md` is present and Promethean-free.
- **Sync test:** run `sync-ingest.sh`; assert `template/.claude/skills/ingest-source` is byte-identical to the plugin copy; assert a `grep -ri promethean template/ plugins/` returns nothing.
- **Ingest dry-run:** point the generalized skill at a small sample source in a scaffolded vault
  and confirm it produces a conformant Source page + at least one wiki page (manual review
  checkpoint, per the skill's own design).

## Open questions / deferred

- Exact Claude Code plugin manifest schema and skills-discovery path — confirm during planning.
- Whether to add a pre-commit hook / CI check enforcing plugin↔template sync (deferred; manual
  script for v1).
- Whether to later split `template/` into its own GitHub template repo for the "Use this
  template" button (deferred; `degit` covers it for v1).
- Optional future parameters for `/new-vault` (category presets, seed a first source) — omitted
  for v1 per YAGNI.
