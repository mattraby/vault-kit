---
type: Source
title: How the Open Knowledge Format can improve data sharing
description: Google Cloud blog post introducing OKF v0.1, the spec this vault follows.
resource: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
tags: [okf, knowledge-management, methodology, example]
timestamp: 2026-06-17T00:00:00Z
---

# How the Open Knowledge Format can improve data sharing

> [!example] Worked example
> This page demonstrates the **Source** convention (an immutable wrapper around external
> material). It documents one of the two sources this vault's design is based on, so it's real —
> keep it, or delete it once you've seen how the pattern works.

## Provenance

- **Publisher:** Google Cloud Blog (Data Analytics)
- **URL:** <https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>
- **Captured:** 2026-06-17

## Key points

- Introduces the **Open Knowledge Format (OKF) v0.1** — a vendor-neutral standard that represents
  knowledge as a directory of markdown files with YAML frontmatter.
- Three design principles: *just markdown*, *just files*, *just YAML frontmatter*.
- Only `type` is required; `title` / `description` / `resource` / `tags` / `timestamp` are
  recommended. Concepts cross-link via normal markdown links, forming a graph.
- Reference implementations: an enrichment agent, a static HTML graph visualizer, and sample bundles.

## Synthesized into

- [Open Knowledge Format (OKF)](../wiki/domain/example-concept.md)
