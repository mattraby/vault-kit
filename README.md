# vault-kit

Start a new **OKF / LLM-wiki knowledge vault** in seconds. vault-kit packages a proven
convention — an Obsidian-compatible, portable [Open Knowledge Format (OKF) v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
bundle maintained in the [LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
style — as a Claude Code plugin and a clone-able template.

## What you get

- **`/vault-kit:new-vault`** — scaffolds a conformant `vault/` (schema, `sources/` + `wiki/` with
  placeholder categories, worked examples, Obsidian config) into the current repo.
- **`/vault-kit:ingest-source`** — turns an external document (PPTX, PDF, Markdown, URL) into
  cross-linked vault knowledge, with a human review checkpoint. Also auto-invokes on requests
  like "ingest this deck."

## Install (Claude Code)

```
/plugin marketplace add mattraby/vault-kit
/plugin install vault-kit@mattraby
```

Then, in any project: `/vault-kit:new-vault` and start ingesting.

## Use without Claude Code

```
npx degit mattraby/vault-kit/template my-project
```

`template/` is a ready-to-use vault with the `ingest-source` skill bundled under `.claude/`.

## Repo layout

- `plugins/vault-kit/` — the plugin (canonical source).
  - `skills/new-vault/` — scaffolder; bundles the vault skeleton in `skeleton/`.
  - `skills/ingest-source/` — the ingest skill + `extract_pptx.py`.
- `template/` — generated, committed export of the skeleton + ingest skill (for the clone path).
- `scripts/check-okf.sh` — verifies a vault is OKF-conformant (wrapper; the canonical copy is
  bundled inside the ingest-source skill so installed vaults can self-verify).
- `scripts/build-template.sh` — regenerates `template/` from the plugin sources.

## Maintaining

The plugin under `plugins/vault-kit/` is the single source of truth. `template/` is generated —
never edit it by hand. After changing the skeleton or the ingest skill, run:

```
scripts/build-template.sh
scripts/check-okf.sh template/vault
```

and commit the regenerated `template/`.
