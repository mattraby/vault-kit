---
name: new-vault
description: >-
  Scaffold a new OKF / LLM-wiki knowledge vault into the current repository. Use when the user
  wants to start a new knowledge base, research vault, or "vault-kit" project — phrases like
  "start a new vault", "scaffold a knowledge base", "set up an OKF vault here". Creates a
  conformant vault/ (AGENTS.md schema + CLAUDE.md bridge, MEMORY.md, .bin/ helper scripts,
  sources/ + wiki/, worked examples, Obsidian config) titled with a name you ask for; works
  with any AGENTS.md-aware agent.
argument-hint: [vault-name]
---

# New Vault — scaffold an OKF / LLM-wiki knowledge base

Create a fresh, OKF-conformant `vault/` in the current repository from the bundled skeleton at
`${CLAUDE_SKILL_DIR}/skeleton/`. The skeleton is itself a valid OKF bundle; you copy it, give it
a name, and seed the log.

## Step 1 — Name the vault, pick the link style, guard against overwrite

- Determine the **vault name** from the user's request, or ask: "What should this vault be
  called?" (e.g. "Acme Research"). It titles the schema and root index.
- Ask the **link style** (unless the user already said): **markdown** (default — portable,
  OKF-conformant, renders on GitHub, links are checkable paths) or **wikilinks** (`[[...]]` —
  survives file moves made outside Obsidian, best for Obsidian-heavy refactoring; trades away
  OKF conformance and GitHub rendering). No preference means markdown.
- If a `vault/` directory already exists here, STOP and ask whether to remove it or scaffold
  elsewhere. Never overwrite an existing vault.

## Step 2 — Copy the skeleton

```bash
cp -R "${CLAUDE_SKILL_DIR}/skeleton" ./vault
```

You now have `vault/` with `AGENTS.md` (the schema — Codex and other tools read it natively),
`CLAUDE.md` (a one-line `@AGENTS.md` import bridge for Claude Code), `MEMORY.md` (committed
project memory), `.bin/` (tool-neutral helper scripts), `index.md`, `log.md`,
`.obsidian/app.json`, `sources/` (a worked-example Source), and `wiki/` (placeholder
categories, each with an `index.md`, plus a worked-example Concept).

## Step 3 — Substitute the vault name into the two H1 titles

```bash
export NAME="<the vault name>"
perl -0pi -e 's/^# Knowledge Vault — Schema & Operating Manual/# $ENV{NAME} Vault — Schema & Operating Manual/m' vault/AGENTS.md
perl -0pi -e 's/^# Knowledge Vault — Index/# $ENV{NAME} Vault — Index/m' vault/index.md
```

The name travels via the environment (`$ENV{NAME}`), so names containing `/`, `&`, quotes, or
`$` cannot break the substitution. (If `perl` is unavailable, edit the first line of each file
directly.)

## Step 4 — Apply the link style (only if the user chose wikilinks)

The skeleton is markdown-style. For a wikilinks vault, flip the declaration and the Obsidian
link generator:

```bash
perl -0pi -e 's/^Link style: markdown$/Link style: wikilinks/m' vault/AGENTS.md
perl -0pi -e 's/"useMarkdownLinks": true/"useMarkdownLinks": false/; s/"newLinkFormat": "relative"/"newLinkFormat": "shortest"/' vault/.obsidian/app.json
```

The conformance checker and lint scanner read the `Link style:` line, so no other change is
needed. Leave the worked examples' markdown links as they are — both styles resolve in
Obsidian, and the examples get deleted anyway.

## Step 5 — Seed the first log entry (today's date)

```bash
printf '\n## %s\n\n- init | Vault scaffolded per LLM-wiki + OKF v0.1\n' "$(date +%F)" >> vault/log.md
```

## Step 6 — Tell the user what's next

- Open `vault/` in Obsidian — it's configured for relative markdown links (OKF-portable).
- Read `vault/AGENTS.md` — the schema and workflows. Codex and other AGENTS.md-aware tools
  read it natively; Claude Code loads it through the `vault/CLAUDE.md` bridge.
- Record durable project facts in `vault/MEMORY.md` — it travels with the repo, unlike
  machine-local tool memory.
- Rename the placeholder wiki categories (`domain`, `stakeholders`, `market`, `requirements`,
  `architecture`) to the real research areas once known.
- Delete the two worked examples (`sources/example-source.md`,
  `wiki/domain/example-concept.md`) once the pattern is clear.
- Ingest the first source with the `ingest-source` skill (`/vault-kit:ingest-source`).
