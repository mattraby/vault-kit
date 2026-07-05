---
name: ingest-source
description: >-
  Ingest an external source into a knowledge vault (an OKF / LLM-wiki
  bundle). Use whenever the user wants to add, ingest, capture, process, digest, or
  pull a document into the vault — a PowerPoint (.pptx), Word (.docx), PDF, Markdown,
  text file, or web page/URL. Triggers on phrases like "ingest this deck", "add this
  PDF to the vault", "process the kickoff presentation", "capture this article", or
  "get this into the knowledge base". Use it even when the user doesn't say the word
  "ingest" — any request to turn an external document into vault knowledge should
  trigger this skill.
argument-hint: [path-or-url]
---

# Ingest Source

Turn one external source into durable vault knowledge, following the **Ingest** workflow
in `vault/AGENTS.md`. The bargain: **you do extraction and synthesis bookkeeping; the human
judges meaning.** So go all the way to a drafted synthesis, then *stop and show your work*
before committing — interpretation the human hasn't seen should never land silently.

## The vault contract (read `vault/AGENTS.md` first)

Everything you write must satisfy the vault's conventions. The essentials:

- **Two content layers:** `sources/` is raw and **immutable**; `wiki/` is synthesized and owned.
- **OKF frontmatter:** every non-reserved `.md` needs a non-empty `type`; also set `title`,
  `description`, `resource`, `tags`, `timestamp` (ISO 8601).
- **Links:** follow the vault's declared style — the `Link style:` line in `vault/AGENTS.md`.
  `markdown` (the default): relative markdown links (e.g. `[Acme](../stakeholders/acme.md)`),
  never `[[wikilinks]]`. `wikilinks`: `[[acme]]`-style, resolved by file name.
- **Reserved files:** `index.md` (per-directory catalog, no frontmatter) and `log.md` (append-only).

If `vault/AGENTS.md` and these notes ever disagree, `AGENTS.md` wins. (In older vaults the
schema is `vault/CLAUDE.md`; in current ones `CLAUDE.md` is a one-line bridge that imports
`AGENTS.md`.)

## Step 1 — Identify the source and extract

Route by type. The goal is clean text plus, where it matters, the visuals.

| Source | How to extract |
|---|---|
| **PowerPoint** `.pptx`/`.ppt` | Run `${CLAUDE_SKILL_DIR}/scripts/extract_pptx.py DECK.pptx` → Markdown of every slide **plus speaker notes** (notes never survive a PDF export, so this is essential). **If a same-named `.pdf` sits beside the deck, also read that PDF visually** (see the PDF row) — slide charts/diagrams are usually vector (`.emf`/`.svg`) that don't extract as images, and the PDF is the faithful visual. |
| **PDF** | Prefer `Read` with the `pages` parameter (renders visually). **If `Read` reports `pdftoppm`/poppler missing**, render the pages yourself and read the images — the Read tool's PATH can be stale right after a fresh poppler install: `pdftoppm -png -r 120 FILE.pdf /tmp/deck/page` then `Read` the resulting `/tmp/deck/page-*.png`. Install poppler if truly absent (`brew install poppler`). Read only the visually-rich pages — skip slides whose text the extractor already captured. |
| **Markdown / text** | `Read` the file directly. |
| **Web page / URL** | Use the `defuddle` skill if the `defuddle` CLI is installed; otherwise `WebFetch`. |
| **Image / screenshot** | `Read` the file directly. |
| **Word** `.docx` | Run `${CLAUDE_SKILL_DIR}/scripts/extract_docx.py FILE.docx` → Markdown of headings, paragraphs, lists, and tables plus metadata. If the media inventory reports vector media, ask for a PDF export for the visuals. |

Skim the extracted content and tell the human the gist before writing pages — a sentence or two
confirms you understood it and gives them a chance to redirect.

## Step 2 — Archive the original (immutable)

Move the original into `sources/attachments/` (create it if needed). This is the permanent,
unedited record. Keep the human's copy if they want one; the vault keeps its own.

## Step 3 — Write the Source page

Create `sources/<slug>.md` (`<slug>` = kebab-case of the title). If that file already exists,
stop and check with the human — the source may already be ingested, and sources are immutable,
so never overwrite one silently. Frontmatter `type: Source`, with `title`, `description`,
`resource` (the URL, or the archived file path), `tags`, `timestamp` — take the timestamp from
the real clock (`date -u +%Y-%m-%dT%H:%M:%SZ`), never from memory.
Body: provenance (who/when/where), the key extracted points, a link to the archived original, and
a `## Synthesized into` list of the wiki pages you create in Step 4.

## Step 4 — Synthesize into the wiki (the actual value)

Distill, don't transcribe. Create or update `wiki/` concept pages — one file per concept, with the
right `type` (`Person`, `Organization`, `Requirement`, `Decision`, `Concept`, `Competitor`, …).
Put each in the fitting category folder. **Cross-link**: source ↔ each concept, and concepts to each
other. Prefer updating an existing page over duplicating one. Broken links to not-yet-written pages
are fine — they mark future work.

## Step 5 — Update indexes and the log

Add new/changed pages to the relevant `index.md` catalogs (one-line summary + relative link each).
Append one line per change to `log.md` under today's `## YYYY-MM-DD`, e.g.
`- ingest | <Source title> → wrote wiki/…, updated …/index.md`.

## Step 6 — Verify, then review checkpoint, then commit

First run the bundled conformance check against the vault directory and fix any FAIL it reports:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check-okf.sh" vault
```

Then stop and present a concise summary: the Source page, every wiki page created/updated (with a
one-line "why"), and any index/log changes — ideally as a diff. **Wait for the human to confirm or
correct** (rename concepts, fix interpretation, flag priorities). Only after approval, commit (or
let the human commit). This checkpoint is the point of the whole skill — it keeps the human judging
meaning while you handle the mechanics.

## Bundled scripts

Both are stdlib only (no installs), and both also live at `vault/.bin/` in scaffolded vaults
so non-Claude agents can use them:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_pptx.py DECK.pptx              # Markdown: metadata + per-slide text + notes
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_docx.py FILE.docx              # Markdown: metadata + headings/paragraphs/lists/tables
# both accept --json (structured output) and --media-dir DIR (extract raster images)
```

`extract_pptx.py` orders slides numerically, maps speaker notes via each slide's `.rels`, reads
core metadata (title/author/dates), and reports a media inventory — flagging that vector media
means you should read the companion PDF for visuals. `extract_docx.py` walks the document body
in order, mapping heading styles to `#`-headings, numbered paragraphs to bullets, and tables to
Markdown tables.
