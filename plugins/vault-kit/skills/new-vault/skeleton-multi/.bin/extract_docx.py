#!/usr/bin/env python3
"""Extract text, tables, metadata, and a media inventory from a .docx.

Standard library only -- no python-docx, no LibreOffice. A .docx is a zip of
OpenXML parts; we read the document XML directly.

Usage:
    python3 extract_docx.py FILE.docx [--media-dir DIR] [--json]

Default output is Markdown on stdout: a metadata header, then the document body
in order -- headings become #-headings, list paragraphs become bullets, tables
become Markdown tables. Embedded vector media (.emf/.wmf/.svg) doesn't extract
as images; ask for a PDF export when the visuals matter.
"""
import argparse
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/elements/1.1/}"
DCTERMS = "{http://purl.org/dc/terms/}"

RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}


def para_style(p):
    el = p.find(f"{W}pPr/{W}pStyle")
    return (el.get(f"{W}val") or "") if el is not None else ""


def para_text(p):
    parts = []
    for node in p.iter():
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag in (f"{W}tab", f"{W}br"):
            parts.append(" ")
    return "".join(parts).strip()


def block_for_paragraph(p):
    txt = para_text(p)
    if not txt:
        return None
    style = para_style(p)
    m = re.fullmatch(r"[Hh]eading(\d)", style)
    if m:
        return {"kind": "heading", "level": int(m.group(1)), "text": txt}
    if style in ("Title", "Subtitle"):
        return {"kind": "heading", "level": 1 if style == "Title" else 2, "text": txt}
    if p.find(f"{W}pPr/{W}numPr") is not None:
        return {"kind": "list_item", "text": txt}
    return {"kind": "para", "text": txt}


def block_for_table(tbl):
    rows = []
    for tr in tbl.findall(f"{W}tr"):
        cells = []
        for tc in tr.findall(f"{W}tc"):
            cells.append(" ".join(filter(None, (para_text(p) for p in tc.iter(f"{W}p")))))
        rows.append(cells)
    return {"kind": "table", "rows": rows} if rows else None


def core_props(z):
    out = {}
    try:
        root = ET.fromstring(z.read("docProps/core.xml"))
    except KeyError:
        return out
    for tag, key in [(DC + "title", "title"), (DC + "creator", "creator"),
                     (DCTERMS + "created", "created"), (DCTERMS + "modified", "modified")]:
        el = root.find(tag)
        if el is not None and el.text:
            out[key] = el.text
    return out


def build(path, media_dir=None):
    with zipfile.ZipFile(path) as z:
        body = ET.fromstring(z.read("word/document.xml")).find(f"{W}body")
        blocks = []
        for child in body if body is not None else []:
            if child.tag == f"{W}p":
                b = block_for_paragraph(child)
            elif child.tag == f"{W}tbl":
                b = block_for_table(child)
            else:
                b = None
            if b:
                blocks.append(b)

        media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
        by_ext, saved = {}, []
        for m in media:
            ext = os.path.splitext(m)[1].lower()
            by_ext[ext] = by_ext.get(ext, 0) + 1
            if media_dir and ext in RASTER:
                os.makedirs(media_dir, exist_ok=True)
                dest = os.path.join(media_dir, os.path.basename(m))
                with open(dest, "wb") as fh:
                    fh.write(z.read(m))
                saved.append(dest)

        return {"file": os.path.basename(path), "meta": core_props(z), "blocks": blocks,
                "media": {"total": len(media), "by_ext": by_ext, "extracted_rasters": saved}}


def table_markdown(rows):
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    def line(cells):
        return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"
    out = [line(rows[0]), "| " + " | ".join("---" for _ in range(width)) + " |"]
    out.extend(line(r) for r in rows[1:])
    return "\n".join(out)


def to_markdown(doc):
    out = []
    meta = doc["meta"]
    title = meta.get("title") or os.path.splitext(doc["file"])[0]
    out.append(f"# {title}\n")
    bits = [f"**Source file:** `{doc['file']}`"]
    if meta.get("creator"):
        bits.append(f"**Author:** {meta['creator']}")
    if meta.get("created"):
        bits.append(f"**Created:** {meta['created']}")
    if meta.get("modified"):
        bits.append(f"**Modified:** {meta['modified']}")
    out.append("  \n".join(bits) + "\n")

    m = doc["media"]
    if m["total"]:
        exts = ", ".join(f"{k} ×{v}" for k, v in sorted(m["by_ext"].items()))
        out.append(f"_Media: {m['total']} files ({exts}). "
                   f"Vector (.emf/.wmf/.svg) doesn't extract as images — ask for a PDF export for visuals._\n")

    for b in doc["blocks"]:
        if b["kind"] == "heading":
            out.append("#" * min(b["level"] + 1, 6) + " " + b["text"])
        elif b["kind"] == "list_item":
            out.append("- " + b["text"])
        elif b["kind"] == "table":
            out.append(table_markdown(b["rows"]))
        else:
            out.append(b["text"])
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Extract text/tables/media from a .docx (stdlib only).")
    ap.add_argument("docx")
    ap.add_argument("--media-dir", help="extract raster images (png/jpg/...) to this dir for visual review")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = ap.parse_args()

    if not os.path.isfile(args.docx):
        sys.exit(f"not found: {args.docx}")
    doc = build(args.docx, args.media_dir)
    print(json.dumps(doc, indent=2, ensure_ascii=False) if args.json else to_markdown(doc))


if __name__ == "__main__":
    main()
