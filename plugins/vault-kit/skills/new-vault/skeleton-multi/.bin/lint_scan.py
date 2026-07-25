#!/usr/bin/env python3
"""Mechanical health scan for an OKF / LLM-wiki vault. Standard library only.

Usage:
    python3 lint_scan.py VAULT_DIR [--json]

Reports (Markdown on stdout): broken internal links (split into missing .md
pages, which the schema allows as planned work, and missing attachments, which
are real defects), orphaned pages, thin pages, missing recommended frontmatter
fields, and the oldest timestamps. Informational only -- always exits 0; use
check-okf.sh as the conformance gate.

Several checks are layer-aware, because the layers have different rules. An
orphaned wiki page is a defect; an orphaned output is normal, since outputs are
entry points for readers outside the vault rather than nodes in the graph. What
matters for an output instead is that its index lists it and that it cites the
wiki pages it rests on. Multi-topic vaults (declared with "Topics: multi" in the
schema doc) additionally get topic-coverage checks.
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import unquote

RESERVED = {"index.md", "log.md", "CLAUDE.md", "AGENTS.md"}
SKIP_DIRS = {".obsidian", ".bin", ".git"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
# A generated output declares its origin, so lint can tell when it has drifted.
DERIVED_RE = re.compile(r"^DERIVED FROM:\s*\[[^\]]*\]\(([^)\s]+)\)", re.M)
MODE_RE = re.compile(r"^Topics: (single|multi)$", re.M)
RECOMMENDED = ("title", "description", "timestamp")
THIN_BODY_LINES = 5
LAYERS = ("sources", "wiki", "outputs")


def md_files(vault):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(root, f)


def parts(rel):
    return rel.replace(os.sep, "/").split("/")


def is_attachment(rel):
    """Archived originals in any attachments/ directory are assets, not pages —
    the wrapper page carries the metadata, so they are not scanned as pages.
    Layout-agnostic on purpose: attachments/ sits under sources/ in a
    single-topic vault, under sources/<topic>/ in a multi-topic one, and
    outputs/ may carry its own."""
    return "attachments" in parts(rel)[:-1]


def layer_of(rel):
    """Which content layer a page belongs to: sources, wiki, outputs, or root."""
    head = parts(rel)[0]
    return head if head in LAYERS else "root"


def topic_of(rel):
    """Second path segment — the topic, in a multi-topic vault."""
    p = parts(rel)
    return p[1] if len(p) > 2 and p[0] in LAYERS else None


def read_mode(vault):
    """Topic layout, declared in the schema doc exactly like Link style. Older
    vaults carry the schema in CLAUDE.md; absent a declaration, single."""
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = os.path.join(vault, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                m = MODE_RE.search(fh.read())
            if m:
                return m.group(1)
    return "single"


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
        if is_attachment(rel):
            continue  # asset, not a page — links to it resolve via os.path.exists
        fm, body = parse_page(path)
        text = strip_code("\n".join(body))
        links = []
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue  # external URL or same-page anchor
            # %-decode after dropping the fragment: paths with spaces are written %20-encoded
            resolved = os.path.normpath(os.path.join(os.path.dirname(rel), unquote(target.split("#")[0])))
            links.append(resolved)
        wikilinks = [t.strip() for t in WIKILINK_RE.findall(text) if t.strip()]
        derived = DERIVED_RE.search(text)
        derived_from = (os.path.normpath(os.path.join(os.path.dirname(rel),
                                                      unquote(derived.group(1).split("#")[0])))
                        if derived else None)
        pages[rel] = {"frontmatter": fm, "body": body, "links": links,
                      "wikilinks": wikilinks, "derived_from": derived_from}

    # Wikilinks resolve by name: bare stem ("acme") or vault-relative path ("wiki/domain/acme").
    by_name = {}
    for rel in pages:
        no_ext = rel[:-3]
        for key in {os.path.basename(no_ext), no_ext}:
            by_name.setdefault(key.lower(), []).append(rel)

    def reserved(rel):
        return os.path.basename(rel) in RESERVED

    inbound = {rel: 0 for rel in pages}
    # Tracked separately: being linked from an index.md is what "catalogued" means,
    # and it is the check that matters for outputs.
    indexed = {rel: 0 for rel in pages}
    planned, missing_attachments = [], []
    for rel, page in pages.items():
        from_index = os.path.basename(rel) == "index.md"
        for target in page["links"]:
            if target in pages:
                inbound[target] += 1
                if from_index:
                    indexed[target] += 1
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
                if from_index:
                    indexed[m] += 1
            if not matches:
                planned.append({"page": rel, "target": f"[[{name}]]"})

    # Orphans are layer-aware. An unreferenced wiki page or source is a defect; an
    # unreferenced output is not, because outputs are entry points for readers outside
    # the vault, not nodes in the graph. Outputs are held to the index check below.
    orphans = [rel for rel, n in inbound.items()
               if n == 0 and not reserved(rel) and layer_of(rel) != "outputs"]

    outputs = [rel for rel in pages if layer_of(rel) == "outputs" and not reserved(rel)]
    unindexed_outputs = sorted(rel for rel in outputs if indexed[rel] == 0)
    # An output that cites nothing means the knowledge never landed in the wiki. A derived
    # output is exempt: it rests on the output it was compiled from, which carries the
    # citations. Broken links don't count as citations — the page has to exist.
    uncited_outputs = sorted(
        rel for rel in outputs
        if not pages[rel]["derived_from"]
        and not any(layer_of(t) in ("wiki", "sources") for t in pages[rel]["links"] if t in pages)
        and not any(layer_of(m) in ("wiki", "sources")
                    for name in pages[rel]["wikilinks"]
                    for m in by_name.get(name.lower().removesuffix(".md"), []))
    )
    # A generated file whose origin changed after it did has drifted. Timestamp order is
    # the mechanical proxy; whether the content still matches is a judgment pass.
    stale_derived = []
    for rel in sorted(pages):
        src = pages[rel]["derived_from"]
        if not src:
            continue
        if src not in pages:
            stale_derived.append({"page": rel, "source": src, "reason": "source does not exist"})
            continue
        mine = pages[rel]["frontmatter"].get("timestamp")
        theirs = pages[src]["frontmatter"].get("timestamp")
        if mine and theirs and theirs > mine:
            stale_derived.append({"page": rel, "source": src,
                                  "reason": f"source updated {theirs}, derived file stamped {mine}"})

    # Multi-topic only: a topic that no index mentions is invisible to anyone browsing.
    missing_topic_entries = []
    if read_mode(vault) == "multi":
        topics = sorted({t for rel in pages if (t := topic_of(rel))})
        root_links = pages.get("index.md", {}).get("links", [])
        for topic in topics:
            if not any(f"/{topic}/" in "/" + t.replace(os.sep, "/") for t in root_links):
                missing_topic_entries.append({"topic": topic, "index": "index.md"})
            for lyr in LAYERS:
                lyr_index = f"{lyr}/index.md"
                if lyr_index not in pages or not os.path.isdir(os.path.join(vault, lyr, topic)):
                    continue
                if not any(parts(t)[:2] == [lyr, topic] for t in pages[lyr_index]["links"]):
                    missing_topic_entries.append({"topic": topic, "index": lyr_index})
    thin = [rel for rel, p in pages.items() if not reserved(rel)
            and len([l for l in p["body"] if l.strip()]) < THIN_BODY_LINES]
    missing_fields = {rel: [k for k in RECOMMENDED if not p["frontmatter"].get(k)]
                      for rel, p in pages.items() if not reserved(rel)}
    missing_fields = {rel: ks for rel, ks in missing_fields.items() if ks}

    stamped = sorted(((p["frontmatter"]["timestamp"], rel) for rel, p in pages.items()
                      if p["frontmatter"].get("timestamp")))
    return {"page_count": len(pages), "topic_mode": read_mode(vault),
            "planned_links": planned,
            "missing_attachments": missing_attachments, "orphans": sorted(orphans),
            "unindexed_outputs": unindexed_outputs, "uncited_outputs": uncited_outputs,
            "stale_derived": stale_derived, "missing_topic_entries": missing_topic_entries,
            "thin_pages": sorted(thin), "missing_fields": missing_fields,
            "oldest_timestamps": [{"page": rel, "timestamp": ts} for ts, rel in stamped[:5]]}


def to_markdown(r):
    out = [f"# Vault lint scan — {r['page_count']} pages ({r['topic_mode']}-topic)\n"]

    def section(title, items, render, empty):
        out.append(f"## {title}")
        out.extend(render(i) for i in items) if items else out.append(f"_{empty}_")
        out.append("")

    section("Missing attachments (defects — the linked file does not exist)",
            r["missing_attachments"], lambda i: f"- `{i['page']}` → `{i['target']}`", "none")
    section("Links to unwritten pages (allowed — flag only ones that look like typos)",
            r["planned_links"], lambda i: f"- `{i['page']}` → `{i['target']}`", "none")
    section("Orphaned pages (no inbound links — index them or justify; outputs are exempt)",
            r["orphans"], lambda i: f"- `{i}`", "none")
    section("Outputs missing from their index (defects — readers arrive via the index)",
            r["unindexed_outputs"], lambda i: f"- `{i}`", "none")
    section("Outputs citing no wiki page or source (the knowledge never landed in the wiki)",
            r["uncited_outputs"], lambda i: f"- `{i}`", "none")
    section("Derived outputs that may have drifted (regenerate, don't hand-edit)",
            r["stale_derived"],
            lambda i: f"- `{i['page']}` ← `{i['source']}` — {i['reason']}", "none")
    section("Topics missing from an index (multi-topic only)",
            r["missing_topic_entries"],
            lambda i: f"- topic `{i['topic']}` not listed in `{i['index']}`", "none")
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
