#!/usr/bin/env bash
# check-okf.sh — verify a directory is a conformant OKF / LLM-wiki vault bundle.
# Canonical copy: scripts/check-okf.sh. build-template.sh fans it out into the
# skills and the vault skeleton's .bin/ — edit here, then re-run the build.
# Usage: check-okf.sh <vault-dir>
set -uo pipefail

VAULT="${1:?usage: check-okf.sh <vault-dir>}"

if [ ! -d "$VAULT" ]; then
  echo "FAIL: $VAULT is not a directory"
  exit 1
fi

fail=0

# Require at least one .md file — an empty/non-vault dir is not conformant.
md_count="$(find "$VAULT" -name '*.md' -type f | wc -l | tr -d ' ')"
if [ "$md_count" -eq 0 ]; then
  echo "FAIL: $VAULT contains no .md files (not a vault)"
  fail=1
fi

# 1. Every non-reserved .md must have YAML frontmatter with a non-empty type:
#    (AGENTS.md and its CLAUDE.md bridge are schema config, exempt like index.md/log.md;
#     archived originals under sources/attachments/ are assets, not pages — the wrapper
#     page carries the metadata, and sources are immutable so we never edit them to add
#     frontmatter; head -n1 is CRLF-tolerant, and the frontmatter must actually close
#     with ---)
while IFS= read -r f; do
  case "$f" in
    */sources/attachments/*) continue ;;
  esac
  case "$(basename "$f")" in
    index.md|log.md|CLAUDE.md|AGENTS.md) continue ;;
  esac
  if [ "$(head -n1 "$f" | tr -d '\r')" != "---" ]; then
    echo "FAIL: $f missing YAML frontmatter (no leading ---)"; fail=1; continue
  fi
  if ! awk 'NR==1{next} /^---[[:space:]]*$/{closed=1; exit} /^type:[[:space:]]*[^[:space:]]/{found=1} END{exit !(found && closed)}' "$f"; then
    echo "FAIL: $f frontmatter has no non-empty 'type:' or never closes with ---"; fail=1
  fi
done < <(find "$VAULT" -name '*.md' -type f)

# 2. Reserved index.md / log.md must NOT start with frontmatter
while IFS= read -r f; do
  if [ "$(head -n1 "$f" | tr -d '\r')" = "---" ]; then
    echo "FAIL: reserved $f must not have YAML frontmatter"; fail=1
  fi
done < <(find "$VAULT" \( -name 'index.md' -o -name 'log.md' \) -type f)

# 3. No [[wikilinks]] anywhere — but only in markdown-style vaults. A vault declares
#    its style with a "Link style: wikilinks|markdown" line in AGENTS.md (or CLAUDE.md
#    in older vaults); absent a declaration, markdown is assumed. The schema quotes the
#    rule, so exempt it and the bridge; raw originals under sources/attachments/ may
#    contain [[...]] text we don't control, so they are exempt too.
STYLE="$(grep -hEo '^Link style: (markdown|wikilinks)' "$VAULT/AGENTS.md" "$VAULT/CLAUDE.md" 2>/dev/null | head -n1 | awk '{print $3}')"
if [ "${STYLE:-markdown}" = "markdown" ]; then
  while IFS= read -r f; do
    if grep -Iq '\[\[' "$f"; then
      echo "FAIL: wikilinks ([[...]]) found in $f (vault link style is markdown)"; fail=1
    fi
  done < <(find "$VAULT" -name '*.md' -type f ! -name 'CLAUDE.md' ! -name 'AGENTS.md' ! -path '*/sources/attachments/*')
fi

if [ "$fail" -eq 0 ]; then echo "OK: $VAULT is OKF-conformant"; fi
exit "$fail"
