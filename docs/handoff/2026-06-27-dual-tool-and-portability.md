# Handoff: vault-kit v0.2 — dual-tool (Claude Code + Codex) and cross-machine portability

**Date:** 2026-06-27
**Purpose:** Hand off an in-progress design discussion to a future LLM session. v0.1 of vault-kit is built, committed, and pushed (private repo). This document captures a proposed **v0.2** that makes a scaffolded vault work with BOTH Claude Code and Codex and be portable across machines. No v0.2 code has been written yet — only the design was discussed. Read this, confirm the open decisions with the human, then proceed.

---

## 1. What vault-kit is (orient yourself first)

vault-kit packages a reusable convention — an Obsidian-compatible, portable **Open Knowledge Format (OKF) v0.1** bundle maintained in the **LLM-wiki** style — as a Claude Code plugin plus a clone-able template.

- **Repo:** `github.com/mattraby/vault-kit` (PRIVATE, personal org). Local: `~/Development/mattraby/vault-kit`. Default branch `main`.
- **Read these to understand v0.1 fully:**
  - `README.md` — what it is, both entry points.
  - `docs/superpowers/specs/2026-06-27-vault-kit-design.md` — the v0.1 spec.
  - `docs/superpowers/plans/2026-06-27-vault-kit.md` — the v0.1 implementation plan (7 tasks).
- **Architecture (important):** the canonical source of truth is `plugins/vault-kit/`. The repo-root `template/` is a GENERATED, committed export produced by `scripts/build-template.sh`. NEVER hand-edit `template/`; edit the plugin sources and re-run the build script.
- **Two skills (Claude Code, namespaced):** `/vault-kit:new-vault` (scaffolds a `vault/` skeleton from `${CLAUDE_SKILL_DIR}/skeleton`) and `/vault-kit:ingest-source` (turns documents into vault knowledge).
- **Verifier:** `scripts/check-okf.sh <vault-dir>` (fails closed on missing/empty dirs).
- v0.1 was built via the superpowers pipeline: brainstorm -> spec -> plan -> subagent-driven execution -> whole-branch review -> fixes -> merge.

---

## 2. The problem v0.2 solves

The human uses **both Claude Code and Codex**, often has the repo on **more than one machine**, and hit three gaps:

1. **Instruction file:** the vault's schema doc is `vault/CLAUDE.md`. Codex reads `AGENTS.md`, not `CLAUDE.md`, so Codex never loads the schema.
2. **Skills:** `/vault-kit:*` are Claude Code skills; Codex has no plugin/skill system, so the ingest convenience doesn't exist there.
3. **Memory:** Claude Code's auto-memory (`MEMORY.md`) is machine-local and not committed, so it is invisible to Codex and absent on a second machine.

---

## 3. Verified facts about Claude Code (already researched — do NOT re-research)

Confirmed against current Claude Code docs (`https://code.claude.com/docs/en/memory.md`) on 2026-06-27:

- **Claude Code does NOT read `AGENTS.md` natively.** The documented bridge is either a `CLAUDE.md` that imports it, or a symlink.
- **`@path` imports work in CLAUDE.md.** Syntax: a line `@AGENTS.md` (or `@./AGENTS.md`, or absolute). Relative paths resolve relative to the importing file's location. Max 4 hops of recursion. Import syntax inside backticks or fenced code blocks is treated as literal text (not expanded). So a one-line `CLAUDE.md` containing `@AGENTS.md` works as a bridge.
- **Symlink also works:** `ln -s AGENTS.md CLAUDE.md`. BUT Windows needs Admin/Developer Mode for symlinks — since the human runs multiple machines, prefer the `@import` stub for portability.
- **Nested instruction files:** a subdirectory file like `vault/CLAUDE.md` (or `vault/AGENTS.md`) loads on-demand when the agent reads files under that subdir (root/ancestor files load at session start). This matches how the vault schema is meant to be used (only when working in the vault).
- **Auto-memory is deliberately machine-local** (`~/.claude/projects/<hash>/memory/`), not version-controlled, and there is NO supported way to make that managed memory itself repo-resident. The recommended portable-context pattern is to commit instruction files (CLAUDE.md/AGENTS.md, and optionally `.claude/rules/*.md` with `paths` frontmatter). Conclusion: make the REPO canonical and route around auto-memory.

Codex side (lower confidence — confirm if it matters): Codex reads `AGENTS.md` hierarchically and supports per-machine custom prompts under `~/.codex/prompts/`. The repo-shared, tool-neutral home is `AGENTS.md`.

---

## 4. Proposed v0.2 design (discussed, not yet built)

Guiding principle: **make the repo the single source of truth, and bridge Claude Code to it.**

### 4a. Schema file: AGENTS.md canonical, CLAUDE.md as bridge
- Rename the schema `vault/CLAUDE.md` -> `vault/AGENTS.md` (Codex reads it natively).
- Add `vault/CLAUDE.md` containing only `@AGENTS.md` (prefer the import stub over a symlink for Windows safety).
- AGENTS.md is the emerging cross-tool standard, so this is the right canonical regardless.

### 4b. Ingest as a tool-neutral workflow
- The ingest workflow already lives in the schema doc, so once it's `AGENTS.md`, a Codex agent can follow its steps.
- Move (or also place) the bundled `extract_pptx.py` to a tool-neutral path (e.g. `vault/.bin/extract_pptx.py`) and reference it from `AGENTS.md`, so any agent finds it (today it lives only under `.claude/skills/...`).
- Keep the Claude Code `ingest-source` skill as a thin wrapper over that same workflow/script (preserves auto-trigger + `/vault-kit:ingest-source` ergonomics without duplicating the workflow).
- Optional, lower priority: ship a Codex-native prompt; it's per-machine config, not repo-shared, so less valuable than the AGENTS.md route.

### 4c. Memory: portable across machines and tools
- Lean into the vault itself as the durable, committed, tool-neutral memory: `wiki/` (curated knowledge) + `log.md` (chronological decisions) already serve this.
- For auto-memory-style facts (preferences, ongoing-work pointers), add a committed `vault/MEMORY.md` (or a `memory/` folder) and reference it from `AGENTS.md` with an instruction: "record durable project facts here, not only in machine-local memory."
- Be explicit about the limit: Claude Code will still keep its own per-machine auto-memory; v0.2 only makes the in-repo file canonical and instructs both tools to read/write it. Everything committed travels by `git pull`.

### 4d. Cohesive summary
`AGENTS.md` becomes canonical (schema + ingest workflow + memory pointer); `CLAUDE.md` is a one-line `@AGENTS.md` bridge; the extract script moves to a neutral path; a committed `MEMORY.md` lives in the scaffolded vault; the `new-vault` scaffolder generates all of this; the Claude Code skills remain thin ergonomic wrappers.

---

## 5. OPEN DECISIONS (resolve with the human before building)

1. **Ingest on Codex:** is "documented workflow in `AGENTS.md` + neutral script path" enough, or also ship a Codex-native command/prompt?
2. **Memory shape:** a single `vault/MEMORY.md`, or lean entirely on `log.md` + `wiki/` and skip a dedicated memory file?
3. **Process:** take v0.2 through the same brainstorm -> spec -> plan -> subagent-driven build used for v1, or something lighter?

---

## 6. Concrete files v0.2 will touch (a starting map, not exhaustive)

- `plugins/vault-kit/skills/new-vault/skeleton/CLAUDE.md` -> rename to `AGENTS.md`; add a `CLAUDE.md` stub (`@AGENTS.md`). Update its self-references ("this file is the schema layer...").
- `plugins/vault-kit/skills/new-vault/skeleton/wiki/domain/example-concept.md` and any other pages linking to `../../CLAUDE.md` -> point at the schema's new name.
- `plugins/vault-kit/skills/new-vault/SKILL.md` -> the title-substitution targets and "read CLAUDE.md" guidance must reflect AGENTS.md (the H1 `# Knowledge Vault — Schema & Operating Manual` lives in AGENTS.md now); still produce the CLAUDE.md bridge in scaffolded vaults.
- `plugins/vault-kit/skills/ingest-source/SKILL.md` -> references to `vault/CLAUDE.md` become `vault/AGENTS.md`; decide canonical path for `extract_pptx.py`.
- `extract_pptx.py` -> consider a tool-neutral home (currently `plugins/vault-kit/skills/ingest-source/scripts/extract_pptx.py`, mirrored into `template/.claude/skills/...`).
- `scripts/check-okf.sh` -> **IMPORTANT:** it currently exempts `CLAUDE.md` by name from BOTH the `type:`-frontmatter check and the `[[wikilink]]` scan (the schema file has no frontmatter and quotes the wikilink rule). If the schema becomes `AGENTS.md`, the checker must exempt `AGENTS.md` too, or it will report false failures.
- `scripts/build-template.sh` -> re-run after changes to regenerate `template/`; confirm it still produces an in-sync, conformant tree.
- `README.md` -> update file names, commands, and the dual-tool story.
- Always finish with: `scripts/build-template.sh` then `scripts/check-okf.sh` on both `plugins/.../skeleton` and `template/vault`, and `grep -ri promethean template/ plugins/` (must be clean).

---

## 7. Carry-over from v1 (deferred Minor findings — the SDD ledger was gitignored, so they live only here now)

From the v1 final whole-branch review, accepted as deferrable:
- `check-okf.sh`: `head -n1` is CRLF-sensitive (a `\r\n` file gets a false FAIL — fails closed, so safe). Consider `tr -d '\r'`.
- `check-okf.sh`: a file with an opening `---` but no closing `---` whose body contains `type:` passes (false negative). Spec-silent.
- `new-vault` SKILL.md: the vault name is interpolated into a `perl` substitution; a name containing `/` or `&` would break it. Low risk for developer-chosen names; consider switching the `s///` delimiter or sanitizing.
- Commit-trailer style across the branch reads "Claude Opus 4.8 (1M context)" vs the documented "Claude Opus 4.8" — cosmetic, commit-message only.

Also not yet done from v1: the interactive plugin-install smoke test (`/plugin marketplace add ~/Development/mattraby/vault-kit`, install `vault-kit@mattraby`, run `/vault-kit:new-vault` in a scratch dir, confirm a conformant `vault/` appears).

---

## 8. Suggested first move for the next session

1. Read Section 1's three docs + this whole file.
2. Ask the human the three Section 5 decisions.
3. If proceeding: brainstorm -> write a `docs/superpowers/specs/<date>-vault-kit-v0.2-*.md` spec -> plan -> build on a feature branch -> review -> merge. Keep the canonical/generated discipline (edit the plugin, regenerate `template/`).
