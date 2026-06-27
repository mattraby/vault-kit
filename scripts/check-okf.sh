#!/usr/bin/env bash
# check-okf.sh — verify a directory is a conformant OKF / LLM-wiki vault bundle.
# Usage: scripts/check-okf.sh <vault-dir>
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
while IFS= read -r f; do
  case "$(basename "$f")" in
    index.md|log.md|CLAUDE.md) continue ;;
  esac
  if [ "$(head -n1 "$f")" != "---" ]; then
    echo "FAIL: $f missing YAML frontmatter (no leading ---)"; fail=1; continue
  fi
  if ! awk 'NR==1{next} /^---/{exit} /^type:[[:space:]]*[^[:space:]]/{found=1} END{exit !found}' "$f"; then
    echo "FAIL: $f frontmatter has no non-empty 'type:'"; fail=1
  fi
done < <(find "$VAULT" -name '*.md' -type f)

# 2. Reserved index.md / log.md must NOT start with frontmatter
while IFS= read -r f; do
  if [ "$(head -n1 "$f")" = "---" ]; then
    echo "FAIL: reserved $f must not have YAML frontmatter"; fail=1
  fi
done < <(find "$VAULT" \( -name 'index.md' -o -name 'log.md' \) -type f)

# 3. No [[wikilinks]] anywhere (CLAUDE.md quotes the rule, so exempt it)
while IFS= read -r f; do
  if grep -Iq '\[\[' "$f"; then
    echo "FAIL: wikilinks ([[...]]) found in $f"; fail=1
  fi
done < <(find "$VAULT" -name '*.md' -type f ! -name 'CLAUDE.md')

if [ "$fail" -eq 0 ]; then echo "OK: $VAULT is OKF-conformant"; fi
exit "$fail"
