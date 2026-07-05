---
type: Concept
title: Open Knowledge Format (OKF)
description: A vendor-neutral spec for representing knowledge as markdown files with YAML frontmatter.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
tags: [okf, methodology, example]
timestamp: 2026-06-17T00:00:00Z
---

# Open Knowledge Format (OKF)

> [!example] Worked example
> This page demonstrates the **Concept** convention and cross-linking. It's real knowledge
> (it describes the format this vault uses), so keep it or delete it once the pattern is clear.

The Open Knowledge Format is an open, vendor-neutral specification for representing curated
knowledge as a directory of markdown files with YAML frontmatter — readable by humans in any
editor and parseable by agents without a translation layer.

## Summary

OKF formalizes the LLM-wiki idea into a portable bundle. A bundle is a directory of concept
files; each file's path is the concept's identity, and concepts cross-link into a graph.

## Details

- **Required frontmatter:** `type` (the only mandatory field). **Recommended:** `title`,
  `description`, `resource`, `tags`, `timestamp`.
- **Reserved files:** `index.md` (directory catalog, no frontmatter) and `log.md` (chronological
  history).
- **Links:** standard relative markdown links between `.md` files; broken links are allowed and
  represent not-yet-written pages.
- **Consumer tolerance:** consumers must accept unknown `type` values, unknown keys, missing
  optional fields, and broken links without rejecting the bundle.

## Related

- [Knowledge Vault schema](../../AGENTS.md) — how this vault applies OKF.

## Citations

- [Source: How the Open Knowledge Format can improve data sharing](../../sources/example-source.md)
