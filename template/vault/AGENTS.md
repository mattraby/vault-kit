# Knowledge Vault — Schema & Operating Manual

This file (`AGENTS.md`) is the **schema layer** of the vault: it defines how knowledge is
structured and maintained. It is configuration, not a concept page — it is exempt from the OKF
frontmatter rules below (like `index.md`, `log.md`, and the `CLAUDE.md` bridge). Read it before
adding or changing anything. Codex and other AGENTS.md-aware tools read it natively; Claude
Code loads it through `CLAUDE.md`, which contains only the import line `@AGENTS.md`.

The vault follows two complementary patterns: the **LLM-wiki** (an LLM maintains a markdown
knowledge base between us and the raw sources) and the **Open Knowledge Format (OKF) v0.1**
(that knowledge expressed as a portable markdown + YAML bundle). When they differ, OKF
conformance wins, because portability is a goal.

## The three layers

1. **Sources** (`sources/`) — raw, **immutable** material: pasted articles, transcripts,
   exports, PDFs, screenshots. We read these but never edit their content. Each gets a thin
   wrapper page (frontmatter + provenance + link to the original).
2. **Wiki** (`wiki/`) — the knowledge we **own and maintain**: one markdown file per concept,
   cross-linked into a graph. This is where understanding accumulates.
3. **Schema** (this file) — the conventions and workflows that keep layers 1–2 coherent.

> [!important] Human curates, the wiki compounds
> The human's job is to curate sources, direct analysis, ask good questions, and judge meaning.
> The wiki's job is to summarize, cross-reference, stay consistent, and do the bookkeeping that
> normally causes wikis to rot. Knowledge should compound, not scatter.

## Directory map

```
vault/
├── AGENTS.md          # this schema (config — exempt from frontmatter rules)
├── CLAUDE.md          # Claude Code bridge — a single `@AGENTS.md` import line
├── MEMORY.md          # durable project memory (frontmatter `type: Memory`)
├── index.md           # root catalog (reserved — NO frontmatter)
├── log.md             # append-only history (reserved)
├── .bin/              # tool-neutral helper scripts (extraction, conformance, lint)
├── sources/           # raw, immutable source material
│   └── index.md
└── wiki/              # synthesized concept pages (the graph)
    ├── index.md
    ├── domain/        # core concepts & glossary        (PLACEHOLDER — rename per PRD)
    ├── stakeholders/  # people & organizations          (PLACEHOLDER)
    ├── market/        # competitors & landscape         (PLACEHOLDER)
    ├── requirements/  # requirements & decisions        (PLACEHOLDER)
    └── architecture/  # technical approach & decisions  (PLACEHOLDER)
```

The five `wiki/` categories are placeholders chosen before the PRD; rename/replace them once
the real research areas are known. A file's **path is its identity** — renaming a file means
renaming a concept (Obsidian updates inbound links automatically; see Links).

## Concept files (every non-reserved `.md`)

Each concept page is one `.md` file with **YAML frontmatter then a markdown body**.

```yaml
---
type: Concept              # REQUIRED — the only mandatory field
title: Display Name        # recommended
description: One-sentence summary of what this concept is.   # recommended
resource: https://...      # recommended when it maps to an external asset (URL/URI)
tags: [topic, area]        # recommended
timestamp: 2026-06-17T00:00:00Z   # recommended — ISO 8601, last meaningful change
---

# Display Name

Lead with a 1–2 sentence definition.

## Summary
What matters in a few lines.

## Details
The substance. Link freely to related concepts and to the sources that back claims.

## Related
- [Some Concept](../domain/some-concept.md)

## Citations
- [Source: Title](../sources/some-source.md)
```

Rules:
- **`type` is required and non-empty** on every non-reserved `.md`. Everything else is optional
  but recommended in the order above.
- Producers may add custom frontmatter keys; consumers must tolerate unknown keys, unknown
  `type` values, missing optional fields, and broken links.
- Body section headings are conventional, not enforced. `# Schema` / `# Examples` / `# Citations`
  are the OKF standard headings; this vault also uses `# Summary` / `# Details` / `# Related`.

### Type vocabulary (starter — extend freely)

`Concept` · `Person` · `Organization` · `Competitor` · `Product` · `Requirement` ·
`Decision` · `Question` · `Source`. Pick a short, descriptive term; don't agonize — consumers
handle unknown types gracefully.

## Links

- Use **relative markdown links** to other vault files: `[Customers](../stakeholders/acme.md)`.
- **Do not use `[[wikilinks]]`.** They are not portable to non-Obsidian OKF consumers.
  Obsidian is configured (`.obsidian/app.json`) to generate relative markdown links and to keep
  them updated on rename, so authoring stays ergonomic and the graph view still works.
- Always link to the `.md` file (path = identity). **Broken links are allowed** — they mark a
  page that's worth writing but doesn't exist yet.

## Reserved files

- **`index.md`** — a per-directory catalog. **No frontmatter.** Group children by category with a
  one-line summary and a relative link each. Exists for progressive disclosure: an agent or human
  reads `index.md` to decide where to go next.
- **`log.md`** — append-only history. Group by date with `## YYYY-MM-DD` (ISO 8601). One line per
  meaningful change, newest date at the top. Example entry:
  `- ingest | Acme Q2 Report → wrote wiki/market/acme.md, updated market/index.md`.

## Memory (durable, portable)

`MEMORY.md` (frontmatter `type: Memory`) is the committed, tool-neutral memory for this
project: preferences, decisions-in-progress, pointers to ongoing work — the small operational
facts that belong in neither `wiki/` (knowledge) nor `log.md` (chronology). **Record durable
project facts there, not only in machine-local memory** — per-tool auto-memory does not travel
between machines or tools; everything committed does. Read it when starting substantial work.

## Workflows

Helper scripts for these workflows live in `.bin/` (stdlib Python and bash — no installs).

### Ingest (new source → knowledge)
1. **Read** the source and discuss takeaways with the human. Extraction helpers:
   `.bin/extract_pptx.py` (slides + speaker notes) and `.bin/extract_docx.py` (Word).
2. **Land** the raw material under `sources/` as an immutable wrapper page (provenance +
   link/copy of the original). Never edit a source's content later.
3. **Synthesize**: create or update the relevant `wiki/` concept page(s). A single source often
   touches several pages — add cross-links as you go.
4. **Index**: update the affected `index.md` files so the new/changed pages are discoverable.
5. **Log**: append an `ingest` entry to `log.md`.

### Query (question → cited answer)
1. Search `wiki/` (then `sources/` if needed).
2. Synthesize an answer **with citations** as relative links to the pages used.
3. If the answer is durable and reusable, **promote** it to a new/updated wiki page and index it.

### Lint (periodic health check)
Run the mechanical checks first: `bash .bin/check-okf.sh .` (conformance gate) and
`python3 .bin/lint_scan.py .` (broken links, orphans, thin pages, missing recommended
fields, oldest timestamps). Then scan for what needs judgment: contradictions between pages,
stale claims, missing cross-links, and **OKF conformance** — every non-reserved `.md`
(excluding `AGENTS.md`, `CLAUDE.md`, `index.md`, `log.md`) must have non-empty `type`
frontmatter. Propose fixes; don't silently rewrite source-backed claims.

## OKF conformance (definition of done for any page)

A page is conformant when: it has parseable YAML frontmatter with a non-empty `type`; links are
relative markdown links to `.md` files; and reserved files follow the structures above. The
whole `vault/` directory is a valid OKF bundle and can be rendered by any OKF consumer (e.g. the
OKF static HTML visualizer) without translation.
