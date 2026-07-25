---
name: new-vault
description: >-
  Scaffold a new OKF / LLM-wiki knowledge vault into the current repository. Use when the user
  wants to start a new knowledge base, research vault, or "vault-kit" project — phrases like
  "start a new vault", "scaffold a knowledge base", "set up an OKF vault here". Creates a
  conformant <project>-vault/ (AGENTS.md schema + CLAUDE.md bridge, MEMORY.md, .bin/ helper
  scripts, sources/ + wiki/ + outputs/, worked examples, Obsidian config) in either a
  single-topic or multi-topic layout; works with any AGENTS.md-aware agent.
argument-hint: [vault-name]
---

# New Vault — scaffold an OKF / LLM-wiki knowledge base

Create a fresh, OKF-conformant vault in the current repository from a bundled skeleton in
`${CLAUDE_SKILL_DIR}/`. Each skeleton is itself a valid OKF bundle; you copy one, name it, and
seed the log.

## Step 1 — Ask the four questions, guard against overwrite

**Vault name.** From the user's request, or ask: "What should this vault be called?" (e.g.
"Acme Research"). It titles the schema and the root index.

**Directory name.** Default to `<project>-vault/`, derived from the repo:

```bash
basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"   # → acme  ⇒  acme-vault/
```

Confirm it with the user. Obsidian takes a vault's display name from the directory basename, so
a bare `vault/` shows up as "vault" in the switcher and is indistinguishable from every other
one open. Never scaffold to plain `vault/` unless the user asks for it.

**Topic layout.** Ask, unless the user already said:

- **single** (default) — one research subject. Layers organize directly by category:
  `wiki/<category>/`, `sources/`, `outputs/`.
- **multi** — several independent subjects, each owning its own category set:
  `wiki/<topic>/<category>/`, `sources/<topic>/`, `outputs/<topic>/`.

Choose multi when a second unrelated subject is already on the horizon. Converting later means
moving every file and repointing every link. If multi, also ask for the first topic's name.

**Link style.** **markdown** (default — portable, OKF-conformant, renders on GitHub, links are
checkable paths) or **wikilinks** (`[[...]]` — survives file moves made outside Obsidian, best
for Obsidian-heavy refactoring; trades away OKF conformance and GitHub rendering). No preference
means markdown.

If the chosen directory already exists, STOP and ask whether to remove it or scaffold elsewhere.
**Never overwrite an existing vault.**

## Step 2 — Copy the matching skeleton

```bash
export DIR="acme-vault"          # the directory name from Step 1
cp -R "${CLAUDE_SKILL_DIR}/skeleton" "./$DIR"          # single-topic
# or
cp -R "${CLAUDE_SKILL_DIR}/skeleton-multi" "./$DIR"    # multi-topic
```

You now have the vault with `AGENTS.md` (the schema — Codex and other tools read it natively),
`CLAUDE.md` (a one-line `@AGENTS.md` import bridge for Claude Code), `MEMORY.md` (committed
project memory), `.bin/` (tool-neutral helper scripts), `index.md`, `log.md`,
`.obsidian/app.json`, and the three content layers — `sources/` (raw, immutable), `wiki/`
(synthesized concepts), and `outputs/` (long-form documents for readers outside the vault) —
each with an `index.md` and a worked example.

## Step 3 — Substitute the vault name and directory name

```bash
export NAME="Acme Research"      # the vault name from Step 1
perl -0pi -e 's/^# Knowledge Vault — Schema & Operating Manual/# $ENV{NAME} Vault — Schema & Operating Manual/m' "$DIR/AGENTS.md"
perl -0pi -e 's/^# Knowledge Vault — Index/# $ENV{NAME} Vault — Index/m' "$DIR/index.md"
perl -0pi -e 's{^vault/$}{$ENV{DIR}/}m' "$DIR/AGENTS.md"
```

Both values travel via the environment (`$ENV{NAME}`, `$ENV{DIR}`), so names containing `/`,
`&`, quotes, or `$` cannot break the substitution. The third line fixes the root of the
directory map in the schema. (If `perl` is unavailable, edit those lines directly.)

## Step 4 — Name the first topic (multi-topic only)

The multi skeleton ships one placeholder topic, `topic-one` / "Topic One". Rename it to the real
subject — directories first, then every reference:

```bash
export T="ai-tooling"            # kebab-case, used in paths
export TITLE="AI Tooling"        # display name, used in prose
for L in wiki sources outputs; do mv "$DIR/$L/topic-one" "$DIR/$L/$T"; done
grep -rl 'topic-one' "$DIR" --include='*.md' | xargs perl -0pi -e 's/topic-one/$ENV{T}/g'
grep -rl 'Topic One' "$DIR" --include='*.md' | xargs perl -0pi -e 's/Topic One/$ENV{TITLE}/g'
```

For each **additional** topic: create `wiki/<topic>/`, `sources/<topic>/`, `outputs/<topic>/`
(each with an `index.md`, and an `attachments/` under sources and outputs), pick that topic's
category set under `wiki/<topic>/`, and add the topic to the root `index.md` and to all three
layer indexes. The conformance checker verifies every one of those.

## Step 5 — Apply the link style (only if the user chose wikilinks)

The skeletons are markdown-style. For a wikilinks vault, flip the declaration and the Obsidian
link generator:

```bash
perl -0pi -e 's/^Link style: markdown$/Link style: wikilinks/m' "$DIR/AGENTS.md"
perl -0pi -e 's/"useMarkdownLinks": true/"useMarkdownLinks": false/; s/"newLinkFormat": "relative"/"newLinkFormat": "shortest"/' "$DIR/.obsidian/app.json"
```

The conformance checker and lint scanner read the `Link style:` line, so no other change is
needed. Leave the worked examples' markdown links as they are — both styles resolve in
Obsidian, and the examples get deleted anyway.

## Step 6 — Seed the first log entry (today's date)

```bash
printf '\n## %s\n\n- init | Vault scaffolded per LLM-wiki + OKF v0.1\n' "$(date +%F)" >> "$DIR/log.md"
```

## Step 7 — Verify, then tell the user what's next

```bash
bash "$DIR/.bin/check-okf.sh" "$DIR"      # must print OK
python3 "$DIR/.bin/lint_scan.py" "$DIR"   # should report nothing but oldest-timestamp entries
```

Then:

- Open the vault directory in Obsidian — it's configured for relative markdown links
  (OKF-portable), and the directory name is what Obsidian shows in the switcher.
- Read `AGENTS.md` — the schema and workflows. Codex and other AGENTS.md-aware tools read it
  natively; Claude Code loads it through the `CLAUDE.md` bridge.
- Record durable project facts in `MEMORY.md` — it travels with the repo, unlike machine-local
  tool memory.
- Rename the placeholder wiki categories (`domain`, `stakeholders`, `market`, `requirements`,
  `architecture`) to the real research areas once known. Do it while they're still empty —
  a file's path is its identity, so renaming later costs every inbound link.
- Delete the three worked examples (`sources/…/example-source.md`,
  `wiki/…/domain/example-concept.md`, `outputs/…/example-output.md`) once the pattern is clear,
  and remove their index entries.
- Ingest the first source with the `ingest-source` skill (`/vault-kit:ingest-source`).
