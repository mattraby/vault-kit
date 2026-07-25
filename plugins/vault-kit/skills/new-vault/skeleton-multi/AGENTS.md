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

This schema is **topic-neutral**. It describes the shape of the vault, never the subject matter
of any particular research area. Topic-specific conventions belong in that topic's
`wiki/<topic>/index.md`, not here.

## Layout

Topics: multi

This vault holds **multiple independent research topics**. A topic is the first path segment
inside each layer, and it partitions the whole vault:

```
wiki/<topic>/<category>/<concept>.md
sources/<topic>/<source>.md
outputs/<topic>/<document>.md
```

The `Topics: multi` line above declares that; the conformance checker and lint scanner read it,
and they apply topic-level checks a single-topic vault is never asked to satisfy. Current topics
are listed in the root [index.md](index.md).

Why the partition exists: categories mean different things in different research areas — a
`market/` folder holding both AI-tooling competitors and venture capital sector data is two
subjects wearing one name. Each topic therefore owns **its own category set** under
`wiki/<topic>/`, chosen for that subject.

Cross-topic links are allowed and encouraged where the subjects genuinely touch. The partition
separates categories, not knowledge.

Adding a topic means: create `wiki/<topic>/`, `sources/<topic>/`, `outputs/<topic>/`, each with
an `index.md`; pick a category set under `wiki/<topic>/`; add the topic to the root `index.md`
and to each layer's `index.md`; log it.

> [!tip] Settle a topic's category set while it is still empty
> A file's path is its identity, so renaming a category means rewriting every inbound link.
> Empty directories rename for free — get the shape right before the notes land.

## The four layers

1. **Sources** (`sources/<topic>/`) — raw, **immutable** material: pasted articles, transcripts,
   exports, PDFs, screenshots. We read these but never edit their content. Each gets a thin
   wrapper page (frontmatter + provenance + link to the original). Non-markdown originals go in
   that topic's `attachments/` folder and are **assets, not pages** — whatever their extension
   (including `.md`), they are exempt from the frontmatter and link rules, because the wrapper
   page carries the metadata and immutability forbids editing them.
2. **Wiki** (`wiki/<topic>/`) — the knowledge we **own and maintain**: one markdown file per
   concept, cross-linked into a graph. This is where understanding accumulates.
3. **Outputs** (`outputs/<topic>/`) — long-form documents synthesized **from** the wiki and
   written for a reader outside this vault: handoffs to another project's agents, engineering
   standards, process descriptions. Whole documents with an intended audience, not atomic concepts.
4. **Schema** (this file) — the conventions and workflows that keep layers 1–3 coherent.

### Wiki or output?

The distinction is **shape and audience**, not subject matter.

| | `wiki/` | `outputs/` |
|---|---|---|
| Unit | one concept | one whole document |
| Reader | us, and agents querying the vault | someone outside this vault |
| Shape | short, atomic, heavily cross-linked | long-form, self-contained, readable start to finish |
| Lifecycle | edited in place as understanding changes | versioned as drafts; supersede rather than patch |

An output may be generated from another output — a machine-readable ruleset compiled from a
prose document, say. The derived file declares its origin on its first body line:

```
DERIVED FROM: [Source Document](source-document.md)
```

Say the same in `description`, and **never hand-edit the generated file** — regenerate it. The
lint scan reads that line and flags a derived file whose source has a newer timestamp.

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
├── index.md           # root catalog: topics, then layers (reserved — NO frontmatter)
├── log.md             # append-only history (reserved)
├── .bin/              # tool-neutral helper scripts (extraction, conformance, lint)
├── sources/           # raw, immutable source material
│   ├── index.md       # layer index — lists topics
│   └── <topic>/
│       ├── index.md   # topic catalog
│       └── attachments/
├── outputs/           # long-form documents for readers outside the vault
│   ├── index.md
│   └── <topic>/
│       ├── index.md
│       └── attachments/
└── wiki/              # synthesized concept pages (the graph)
    ├── index.md
    └── <topic>/
        ├── index.md   # topic index — lists this topic's categories
        └── <category>/
            └── index.md
```

The categories under the placeholder topic are starting suggestions; rename or replace them with
the ones the subject actually needs. A file's **path is its identity** — renaming a file means
renaming a concept. Obsidian is configured to update inbound links on rename, but that only
applies to moves made **inside Obsidian**. Moving files from a shell or an agent means
repointing the links yourself.

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
- [Some Concept](../another-category/some-concept.md)

## Citations
- [Source: Title](../../../sources/<topic>/some-source.md)
```

Note the depths from a concept at `wiki/<topic>/<category>/`: a sibling category is `../`, a
sibling topic is `../../<other-topic>/`, and the vault root is `../../../`.

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

Types used in `outputs/`: `Standard` (descriptive engineering standards) · `Handoff` (a briefing
addressed to a receiving agent and its human) · `Process` (a repeatable procedure).

Topics may extend this vocabulary with terms their subject needs. Keep additions in the same
short-noun style.

## Links

Link style: markdown

The line above declares this vault's link style. Every page follows it, and the conformance
checker enforces it.

- **markdown** (default, OKF-conformant) — relative markdown links to other vault files:
  `[Customers](../stakeholders/acme.md)`. Portable to GitHub and any markdown tool, and
  mechanically checkable as paths. Obsidian is configured (`.obsidian/app.json`) to generate
  relative markdown links and keep them updated on rename, so authoring stays ergonomic and
  the graph view still works. **Do not use `[[wikilinks]]`** in a markdown-style vault.
- **wikilinks** (Obsidian-style) — `[[acme]]` or `[[acme|Customers]]`, resolved by file name.
  They survive file moves made outside Obsidian (agent-driven refactors), at the price of OKF
  conformance, GitHub rendering, and path-checkable links. Pages with non-unique names (like
  the `index.md` files) still need path-qualified links.
- Whichever the style: link to the `.md` file (its path/name is its identity), and **broken
  links are allowed** — they mark a page that's worth writing but doesn't exist yet.
- Cross-topic links use the same form, just a longer path:
  `../../<other-topic>/<category>/<concept>.md`.

## Reserved files

- **`index.md`** — a per-directory catalog. **No frontmatter.** Group children by category with a
  one-line summary and a relative link each. Exists for progressive disclosure: an agent or human
  reads `index.md` to decide where to go next. Every directory has one — the root lists topics,
  layer indexes list topics, topic indexes list categories (or, in `sources/` and `outputs/`,
  the pages themselves), category indexes list concepts.
- **`log.md`** — append-only history. Group by date with `## YYYY-MM-DD` (ISO 8601). One line per
  meaningful change, newest date at the top. Entries name the topic they touched. Example:
  `- ingest | acme-research | Acme Q2 Report → wrote wiki/acme-research/market/acme.md, updated that index`.

An output nobody indexed is an output nobody finds: outputs are entry points for outside readers
rather than nodes in the graph, so `outputs/<topic>/index.md` is the only thing that makes them
discoverable.

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
2. **Place** it in a topic. If it doesn't fit an existing one, say so before inventing a topic —
   a new topic is a structural change, not a filing decision.
3. **Land** the raw material under `sources/<topic>/` as an immutable wrapper page (provenance +
   link/copy of the original, archived in `sources/<topic>/attachments/`). Never edit a source's
   content later.
4. **Synthesize**: create or update the relevant `wiki/<topic>/` concept page(s). A single source
   often touches several pages — add cross-links as you go.
5. **Index**: update the affected `index.md` files so the new/changed pages are discoverable.
6. **Log**: append an `ingest` entry to `log.md`, naming the topic.

### Publish (vault knowledge → external document)
1. **Draft** into `outputs/<topic>/` with `type`, `title`, `description`, `tags`, `timestamp`
   frontmatter.
2. **Cite** the wiki pages and sources it rests on, as relative links. An output that cites
   nothing is a signal the knowledge never landed in the wiki — put it there first.
3. **Index**: add it to `outputs/<topic>/index.md` under the right heading.
4. **Log**: append a `publish` entry to `log.md`, naming the topic.

Outputs are point-in-time. When one goes stale, supersede it with a new document and note which
file replaced it, rather than silently rewriting a document someone may already be working from.

### Query (question → cited answer)
1. Identify the topic, then search its `wiki/` (then its `sources/` if needed). Search other
   topics only when the question genuinely spans them.
2. Synthesize an answer **with citations** as relative links to the pages used.
3. If the answer is durable and reusable, **promote** it to a new/updated wiki page and index it.

### Lint (periodic health check)
Run the mechanical checks first: `bash .bin/check-okf.sh .` (conformance gate) and
`python3 .bin/lint_scan.py .` (broken links, orphans, unindexed and uncited outputs, drifted
derived outputs, topic coverage, thin pages, missing recommended fields, oldest timestamps).
Then scan for what needs judgment: contradictions between pages, stale claims, missing
cross-links, and **OKF conformance** — every non-reserved `.md` (excluding `AGENTS.md`,
`CLAUDE.md`, `index.md`, `log.md`, and archived originals in any `attachments/` directory) must
have non-empty `type` frontmatter. Propose fixes; don't silently rewrite source-backed claims.

**Topic-level checks:** every topic appears in the root `index.md` and in all three layer
indexes; no concept page sits directly in `wiki/<topic>/` outside a category; no file sits at a
layer root outside a topic directory; every topic directory has an `index.md`.

**Orphan rules differ by layer.** A wiki page or source with no inbound links is a defect —
index it or cross-link it. An output with none is normal, because outputs are entry points, not
graph nodes; never "fix" one by inventing links to it. What outputs are held to instead: every
output is listed in its topic's `outputs/<topic>/index.md`, every output cites the wiki pages it
rests on, and a generated output still matches the document it was derived from.

## OKF conformance (definition of done for any page)

A page is conformant when: it has parseable YAML frontmatter with a non-empty `type`; links are
relative markdown links to `.md` files (the default link style — a vault declared
`Link style: wikilinks` deliberately trades this away for move-resilience); and reserved files
follow the structures above. Archived originals in any `attachments/` directory are assets, not
pages — the rules do not apply to them, whatever their extension. Pages in `outputs/` carry
ordinary frontmatter like any other page, so the fourth layer changes nothing about conformance.
The topic segment is ordinary directory structure — it needs no special support from a consumer.
The whole vault directory is a valid OKF bundle and can be rendered by any OKF consumer (e.g.
the OKF static HTML visualizer) without translation.
