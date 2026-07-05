#!/usr/bin/env python3
"""Mechanical health scan for an OKF / LLM-wiki vault. Standard library only.

Usage:
    python3 lint_scan.py VAULT_DIR [--json]

Reports (Markdown on stdout): broken internal links (split into missing .md
pages, which the schema allows as planned work, and missing attachments, which
are real defects), orphaned pages, thin pages, missing recommended frontmatter
fields, and the oldest timestamps. Informational only -- always exits 0; use
check-okf.sh as the conformance gate.
"""
import argparse
import json
import os
import re
import sys

RESERVED = {"index.md", "log.md", "CLAUDE.md", "AGENTS.md"}
SKIP_DIRS = {".obsidian", ".bin", ".git"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
RECOMMENDED = ("title", "description", "timestamp")
THIN_BODY_LINES = 5


def md_files(vault):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(root, f)


def parse_page(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    fm, body_start = {}, 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break
            m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if m:
                fm[m.group(1)] = m.group(2).strip()
    body = lines[body_start:]
    return fm, body


def strip_code(text):
    """Drop fenced blocks and inline code spans — links in there are examples, not links."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def scan(vault):
    vault = vault.rstrip("/")
    pages = {}
    for path in md_files(vault):
        rel = os.path.relpath(path, vault)
        fm, body = parse_page(path)
        text = strip_code("\n".join(body))
        links = []
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue  # external URL or same-page anchor
            resolved = os.path.normpath(os.path.join(os.path.dirname(rel), target.split("#")[0]))
            links.append(resolved)
        wikilinks = [t.strip() for t in WIKILINK_RE.findall(text) if t.strip()]
        pages[rel] = {"frontmatter": fm, "body": body, "links": links, "wikilinks": wikilinks}

    # Wikilinks resolve by name: bare stem ("acme") or vault-relative path ("wiki/domain/acme").
    by_name = {}
    for rel in pages:
        no_ext = rel[:-3]
        for key in {os.path.basename(no_ext), no_ext}:
            by_name.setdefault(key.lower(), []).append(rel)

    inbound = {rel: 0 for rel in pages}
    planned, missing_attachments = [], []
    for rel, page in pages.items():
        for target in page["links"]:
            if target in pages:
                inbound[target] += 1
            elif os.path.exists(os.path.join(vault, target)):
                pass  # existing non-md asset
            elif target.endswith(".md"):
                planned.append({"page": rel, "target": target})
            else:
                missing_attachments.append({"page": rel, "target": target})
        for name in page["wikilinks"]:
            matches = by_name.get(name.lower().removesuffix(".md"), [])
            for m in matches:  # count every candidate so ambiguity never fakes an orphan
                inbound[m] += 1
            if not matches:
                planned.append({"page": rel, "target": f"[[{name}]]"})

    def reserved(rel):
        return os.path.basename(rel) in RESERVED

    orphans = [rel for rel, n in inbound.items() if n == 0 and not reserved(rel)]
    thin = [rel for rel, p in pages.items() if not reserved(rel)
            and len([l for l in p["body"] if l.strip()]) < THIN_BODY_LINES]
    missing_fields = {rel: [k for k in RECOMMENDED if not p["frontmatter"].get(k)]
                      for rel, p in pages.items() if not reserved(rel)}
    missing_fields = {rel: ks for rel, ks in missing_fields.items() if ks}

    stamped = sorted(((p["frontmatter"]["timestamp"], rel) for rel, p in pages.items()
                      if p["frontmatter"].get("timestamp")))
    return {"page_count": len(pages), "planned_links": planned,
            "missing_attachments": missing_attachments, "orphans": sorted(orphans),
            "thin_pages": sorted(thin), "missing_fields": missing_fields,
            "oldest_timestamps": [{"page": rel, "timestamp": ts} for ts, rel in stamped[:5]]}


def to_markdown(r):
    out = [f"# Vault lint scan — {r['page_count']} pages\n"]

    def section(title, items, render, empty):
        out.append(f"## {title}")
        out.extend(render(i) for i in items) if items else out.append(f"_{empty}_")
        out.append("")

    section("Missing attachments (defects — the linked file does not exist)",
            r["missing_attachments"], lambda i: f"- `{i['page']}` → `{i['target']}`", "none")
    section("Links to unwritten pages (allowed — flag only ones that look like typos)",
            r["planned_links"], lambda i: f"- `{i['page']}` → `{i['target']}`", "none")
    section("Orphaned pages (no inbound links — index them or justify)",
            r["orphans"], lambda i: f"- `{i}`", "none")
    section(f"Thin pages (fewer than {THIN_BODY_LINES} non-empty body lines)",
            r["thin_pages"], lambda i: f"- `{i}`", "none")
    section("Missing recommended frontmatter fields",
            sorted(r["missing_fields"].items()),
            lambda i: f"- `{i[0]}`: {', '.join(i[1])}", "none")
    section("Oldest timestamps (staleness candidates)",
            r["oldest_timestamps"], lambda i: f"- {i['timestamp']} — `{i['page']}`", "no timestamps found")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Mechanical vault health scan (stdlib only).")
    ap.add_argument("vault")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = ap.parse_args()

    if not os.path.isdir(args.vault):
        sys.exit(f"not a directory: {args.vault}")
    result = scan(args.vault)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else to_markdown(result))


if __name__ == "__main__":
    main()
