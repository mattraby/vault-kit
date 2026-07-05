#!/usr/bin/env bash
# check-okf.sh — verify a directory is a conformant OKF / LLM-wiki vault bundle.
# Thin wrapper: the canonical copy ships inside the ingest-source skill so vaults
# can self-verify wherever the plugin or template is installed.
# Usage: scripts/check-okf.sh <vault-dir>
exec "$(cd "$(dirname "$0")/.." && pwd)/plugins/vault-kit/skills/ingest-source/scripts/check-okf.sh" "$@"
