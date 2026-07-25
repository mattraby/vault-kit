---
type: Standard
title: Vault Conventions Brief
description: How this knowledge vault is organized and what an agent working in it must honor.
tags: [conventions, okf, example]
timestamp: 2026-06-17T00:00:00Z
---

# Vault Conventions Brief

> [!example] Worked example
> This page demonstrates the **Output** convention: a whole document written for a reader
> outside the vault, synthesized from what the wiki already knows. Keep it, or delete it once
> the pattern is clear.

A briefing for an agent joining this project: what the vault is, and the handful of rules that
keep it from rotting.

## What this vault is

A portable [Open Knowledge Format](../wiki/domain/example-concept.md) bundle — a directory of
markdown files with YAML frontmatter, no database and no service. It is maintained in the
LLM-wiki style: the agent does the bookkeeping, the human judges meaning.

## What you must honor

- **`sources/` is immutable.** Read it, cite it, never edit it. Archived originals live in
  `attachments/` and are assets, not pages.
- **`wiki/` is owned.** One concept per file, cross-linked. Update an existing page rather than
  duplicating it. A wiki page nothing links to is a defect.
- **`outputs/` is for outside readers.** Whole documents, self-contained, listed in
  `outputs/index.md`. Supersede them rather than silently patching them.
- **`type` frontmatter is required** on every page. Everything else is recommended.
- **Links are relative markdown links** to `.md` files. Broken links are allowed — they mark
  work worth doing.

## Before you commit

Run the conformance gate and the health scan, and fix what they report:

```bash
bash .bin/check-okf.sh .
python3 .bin/lint_scan.py .
```

## Citations

- [Open Knowledge Format (OKF)](../wiki/domain/example-concept.md)
- [Source: How the Open Knowledge Format can improve data sharing](../sources/example-source.md)
