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

Periodic health check, following the **Lint** workflow in `vault/AGENTS.md`: scripts do the
mechanical scanning, you do the judgment passes, and the human approves every fix. Never
silently rewrite source-backed claims.

## Step 1 — Conformance gate

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check-okf.sh" vault
```

Any FAIL is a structural defect (missing/unclosed frontmatter, empty `type`, wikilinks,
frontmatter on reserved files). Diagnose each one and include a proposed fix in the report.

## Step 2 — Mechanical scan

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/lint_scan.py" vault
```

The report distinguishes severity for you:

- **Missing attachments** — real defects; a page links to a file that does not exist.
- **Links to unwritten pages** — allowed by the schema (they mark planned work); flag only
  targets that look like typos of existing pages.
- **Orphaned pages** — nothing links to them; propose an index entry or a cross-link.
- **Thin pages** — near-empty; propose filling or merging them.
- **Missing recommended frontmatter** and **oldest timestamps** — staleness candidates.

The scanner reads both link syntaxes: markdown links resolve as paths, wikilinks by file name
(honoring the vault's `Link style:` declaration is the checker's job in Step 1).

## Step 3 — Judgment passes (read the pages, don't just scan)

- **Contradictions:** pages that disagree with each other or with their cited sources.
- **Staleness:** claims superseded by a newer source in `sources/`.
- **Missing cross-links:** related concepts that never reference each other.
- **Misfiled or duplicated concepts:** wrong category, or two pages for one concept.

## Step 4 — Report, get approval, then apply

Present findings grouped by severity, each with a one-line proposed fix. **Wait for the human
to choose what to apply.** Then make the approved changes, update any affected `index.md`,
and append one line to `log.md` under today's date, e.g.
`- lint | fixed 3 broken attachments, indexed 2 orphans`.
