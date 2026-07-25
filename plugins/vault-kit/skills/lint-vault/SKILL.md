---
name: lint-vault
description: >-
  Run a health check on a knowledge vault (an OKF / LLM-wiki bundle). Use when the user wants
  to lint the vault, run a vault health check, audit the vault or wiki, check vault
  consistency, verify OKF conformance, or find orphaned pages, broken links, or stale pages —
  phrases like "lint the vault", "vault health check", "audit the wiki", "is the vault
  conformant". Runs the bundled conformance gate and mechanical scan, then proposes fixes
  for human approval.
argument-hint: [vault-dir]
---

# Lint Vault

Periodic health check, following the **Lint** workflow in the vault's `AGENTS.md`: scripts do the
mechanical scanning, you do the judgment passes, and the human approves every fix. Never
silently rewrite source-backed claims.

## Step 0 — Locate the vault

Vaults are named for their project (`acme-vault/`), not always `vault/`:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/find-vault.sh" .
```

One match prints the path. No match exits 1; several exit 2 — ask the user which one. If the
user named a vault explicitly, use theirs and skip this. Export it as `$VAULT` for the steps below.

## Step 1 — Conformance gate

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check-okf.sh" "$VAULT"
```

Any FAIL is a structural defect: missing/unclosed frontmatter, empty `type`, wikilinks in a
markdown-style vault, frontmatter on reserved files. A vault declaring `Topics: multi` is also
checked for topic structure — no page at a layer root, no wiki concept loose in `wiki/<topic>/`
outside a category, every topic directory carrying an `index.md`. Diagnose each failure and
include a proposed fix in the report.

## Step 2 — Mechanical scan

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/lint_scan.py" "$VAULT"
```

The report distinguishes severity for you:

- **Missing attachments** — real defects; a page links to a file that does not exist.
- **Links to unwritten pages** — allowed by the schema (they mark planned work); flag only
  targets that look like typos of existing pages.
- **Orphaned pages** — nothing links to them; propose an index entry or a cross-link.
- **Outputs missing from their index** — real defects; add the entry.
- **Outputs citing no wiki page or source** — the knowledge never landed in the wiki. The fix is
  to write the wiki pages, not to bolt citations onto the output.
- **Derived outputs that may have drifted** — a file declaring `DERIVED FROM:` whose source has a
  newer timestamp. Regenerate it; never hand-edit a generated file.
- **Topics missing from an index** — multi-topic only; the topic is invisible to anyone browsing.
- **Thin pages** — near-empty; propose filling or merging them.
- **Missing recommended frontmatter** and **oldest timestamps** — staleness candidates.

> [!important] Orphan rules differ by layer
> A wiki page or source with no inbound links is a defect. **An output with none is normal** —
> outputs are entry points for readers outside the vault, not nodes in the graph. The scan
> already exempts them; don't "fix" an output by inventing links to it. What outputs owe is an
> index entry and citations, both checked above.

The scanner reads both link syntaxes: markdown links resolve as paths, wikilinks by file name
(honoring the vault's `Link style:` declaration is the checker's job in Step 1). It reads the
`Topics:` declaration the same way, and skips the topic checks in single-topic vaults.

## Step 3 — Judgment passes (read the pages, don't just scan)

- **Contradictions:** pages that disagree with each other or with their cited sources.
- **Staleness:** claims superseded by a newer source in `sources/`.
- **Missing cross-links:** related concepts that never reference each other.
- **Misfiled or duplicated concepts:** wrong category, or two pages for one concept. In a
  multi-topic vault, also: a concept filed under the wrong topic, or one that genuinely spans
  two topics and should be cross-linked rather than duplicated.
- **Outputs against their sources:** does a generated output still match the document it was
  derived from, beyond the timestamp check? Does a standing output still reflect the wiki?

## Step 4 — Report, get approval, then apply

Present findings grouped by severity, each with a one-line proposed fix. **Wait for the human
to choose what to apply.** Then make the approved changes, update any affected `index.md`,
and append one line to `log.md` under today's date, e.g.
`- lint | fixed 3 broken attachments, indexed 2 orphans`.
