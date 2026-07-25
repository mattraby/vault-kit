#!/usr/bin/env bash
# find-vault.sh — locate the OKF / LLM-wiki vault bundle in a project.
# Canonical copy: scripts/find-vault.sh. build-template.sh fans it out into the
# skills and the vault skeleton's .bin/ — edit here, then re-run the build.
#
# Vaults are no longer always named `vault/`: Obsidian takes a vault's display
# name from the directory basename, so scaffolds are named `<project>-vault/`.
# Nothing may assume the old name, and old vaults must keep working — hence
# detection by shape rather than by name.
#
# A directory is a vault bundle when it holds index.md AND log.md AND a schema
# doc (AGENTS.md, or CLAUDE.md in vaults predating the bridge).
#
# Usage: find-vault.sh [start-dir]        (default: current directory)
# Exit:  0 one found (path on stdout) | 1 none | 2 several (all on stdout)
set -uo pipefail

START="${1:-.}"

if [ ! -d "$START" ]; then
  echo "find-vault: $START is not a directory" >&2
  exit 1
fi

# Skeletons and generated templates are vault-shaped by design — they are the
# thing that *makes* vaults, not a vault to be linted or ingested into. Excluding
# them matters most inside vault-kit itself and any repo vendoring it.
found=()
while IFS= read -r schema; do
  d="$(dirname "$schema")"
  case "/$d/" in
    */.git/*|*/node_modules/*|*/skeleton/*|*/skeleton-*/*|*/template/*) continue ;;
  esac
  case "$(basename "$d")" in
    skeleton|skeleton-*|template) continue ;;
  esac
  [ -f "$d/index.md" ] && [ -f "$d/log.md" ] || continue
  # A directory holding both AGENTS.md and its CLAUDE.md bridge matches twice.
  case " ${found[*]-} " in *" $d "*) continue ;; esac
  found+=("$d")
done < <(find "$START" -maxdepth 4 \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \) -type f 2>/dev/null | sort)

case "${#found[@]}" in
  0)
    echo "find-vault: no vault bundle under $START" >&2
    echo "find-vault: a bundle is a directory with index.md, log.md, and AGENTS.md (or CLAUDE.md)." >&2
    echo "find-vault: scaffold one with the new-vault skill." >&2
    exit 1
    ;;
  1)
    echo "${found[0]}"
    ;;
  *)
    printf '%s\n' "${found[@]}"
    echo "find-vault: ${#found[@]} vault bundles found — pass the one you mean explicitly." >&2
    exit 2
    ;;
esac
