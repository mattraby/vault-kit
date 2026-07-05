---
name: new-vault
description: >-
  Scaffold a new OKF / LLM-wiki knowledge vault into the current repository. Use when the user
  wants to start a new knowledge base, research vault, or "vault-kit" project — phrases like
  "start a new vault", "scaffold a knowledge base", "set up an OKF vault here". Creates a
  conformant vault/ skeleton (CLAUDE.md schema, sources/ + wiki/ with placeholder categories,
  worked examples, Obsidian config) titled with a name you ask for.
argument-hint: [vault-name]
---

# New Vault — scaffold an OKF / LLM-wiki knowledge base

Create a fresh, OKF-conformant `vault/` in the current repository from the bundled skeleton at
`${CLAUDE_SKILL_DIR}/skeleton/`. The skeleton is itself a valid OKF bundle; you copy it, give it
a name, and seed the log.

## Step 1 — Name the vault and guard against overwrite

- Determine the **vault name** from the user's request, or ask: "What should this vault be
  called?" (e.g. "Acme Research"). It titles the schema and root index.
- If a `vault/` directory already exists here, STOP and ask whether to remove it or scaffold
  elsewhere. Never overwrite an existing vault.

## Step 2 — Copy the skeleton

```bash
cp -R "${CLAUDE_SKILL_DIR}/skeleton" ./vault
```

You now have `vault/` with `CLAUDE.md`, `index.md`, `log.md`, `.obsidian/app.json`, `sources/`
(a worked-example Source), and `wiki/` (placeholder categories, each with an `index.md`, plus a
worked-example Concept).

## Step 3 — Substitute the vault name into the two H1 titles

```bash
export NAME="<the vault name>"
perl -0pi -e 's/^# Knowledge Vault — Schema & Operating Manual/# $ENV{NAME} Vault — Schema & Operating Manual/m' vault/CLAUDE.md
perl -0pi -e 's/^# Knowledge Vault — Index/# $ENV{NAME} Vault — Index/m' vault/index.md
```

The name travels via the environment (`$ENV{NAME}`), so names containing `/`, `&`, quotes, or
`$` cannot break the substitution. (If `perl` is unavailable, edit the first line of each file
directly.)

## Step 4 — Seed the first log entry (today's date)

```bash
printf '\n## %s\n\n- init | Vault scaffolded per LLM-wiki + OKF v0.1\n' "$(date +%F)" >> vault/log.md
```

## Step 5 — Tell the user what's next

- Open `vault/` in Obsidian — it's configured for relative markdown links (OKF-portable).
- Read `vault/CLAUDE.md` — the schema and workflows.
- Rename the placeholder wiki categories (`domain`, `stakeholders`, `market`, `requirements`,
  `architecture`) to the real research areas once known.
- Delete the two worked examples (`sources/example-source.md`,
  `wiki/domain/example-concept.md`) once the pattern is clear.
- Ingest the first source with the `ingest-source` skill (`/vault-kit:ingest-source`).
