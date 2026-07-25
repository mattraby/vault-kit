#!/usr/bin/env python3
"""Extract text, speaker notes, metadata, and a media inventory from a .pptx.

Standard library only -- no python-pptx, no LibreOffice. A .pptx is a zip of
OpenXML parts; we read slide and notes XML directly.

Usage:
    python3 extract_pptx.py DECK.pptx [--media-dir DIR] [--json]

Default output is Markdown on stdout: a metadata header, then one section per
slide (in true slide order) with the slide's text and any speaker notes.

Why this shape: the deck's charts/diagrams are usually vector (.emf/.svg) that
don't render well as extracted images -- so for visual fidelity, read the
companion PDF instead. This script's job is the text + notes the PDF can't give
you (notes never appear in an exported PDF).
"""
import argparse
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"          # DrawingML text
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"  # part rels
DC = "{http://purl.org/dc/elements/1.1/}"
DCTERMS = "{http://purl.org/dc/terms/}"

RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}


def slide_num(name):
    m = re.search(r"(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def paragraph_lines(xml_bytes):
    """Return non-empty text lines, one per DrawingML paragraph (preserves bullets)."""
    root = ET.fromstring(xml_bytes)
    lines = []
    for p in root.iter(A + "p"):
        txt = "".join(t.text or "" for t in p.iter(A + "t")).strip()
        if txt:
            lines.append(txt)
    return lines


def notes_part_for_slide(z, slide_name):
    """Resolve the notesSlide part referenced by a slide's .rels, if any."""
    rels = "ppt/slides/_rels/" + os.path.basename(slide_name) + ".rels"
    try:
        root = ET.fromstring(z.read(rels))
    except KeyError:
        return None
    for r in root.iter(REL + "Relationship"):
        if r.get("Type", "").endswith("/notesSlide"):
            target = r.get("Target", "")
            return os.path.normpath(os.path.join("ppt/slides", target)).replace("\\", "/")
    return None


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
        names = z.namelist()
        slides = sorted((n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                        key=slide_num)
        media = sorted(n for n in names if n.startswith("ppt/media/"))

        deck = {"file": os.path.basename(path), "meta": core_props(z),
                "slide_count": len(slides), "slides": [], "media": {}}

        for s in slides:
            entry = {"number": slide_num(s), "lines": paragraph_lines(z.read(s)), "notes": []}
            notes = notes_part_for_slide(z, s)
            if notes:
                try:
                    entry["notes"] = paragraph_lines(z.read(notes))
                except KeyError:
                    pass
            deck["slides"].append(entry)

        # media inventory by extension; optionally extract raster images for visual review
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
        deck["media"] = {"total": len(media), "by_ext": by_ext, "extracted_rasters": saved}
        return deck


def to_markdown(deck):
    out = []
    meta = deck["meta"]
    title = meta.get("title") or os.path.splitext(deck["file"])[0]
    out.append(f"# {title}\n")
    bits = [f"**Source file:** `{deck['file']}`", f"**Slides:** {deck['slide_count']}"]
    if meta.get("creator"):
        bits.append(f"**Author:** {meta['creator']}")
    if meta.get("created"):
        bits.append(f"**Created:** {meta['created']}")
    if meta.get("modified"):
        bits.append(f"**Modified:** {meta['modified']}")
    out.append("  \n".join(bits) + "\n")

    m = deck["media"]
    if m["total"]:
        exts = ", ".join(f"{k} ×{v}" for k, v in sorted(m["by_ext"].items()))
        out.append(f"_Media: {m['total']} files ({exts}). "
                   f"Vector (.emf/.svg) renders poorly as images — read the companion PDF for visuals._\n")

    for s in deck["slides"]:
        out.append(f"## Slide {s['number']}")
        if s["lines"]:
            out.extend(s["lines"])
        else:
            out.append("_(no extractable text — likely an image/diagram slide; see PDF)_")
        if s["notes"]:
            out.append("\n**Speaker notes:**")
            out.extend(s["notes"])
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Extract text/notes/media from a .pptx (stdlib only).")
    ap.add_argument("pptx")
    ap.add_argument("--media-dir", help="extract raster images (png/jpg/...) to this dir for visual review")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = ap.parse_args()

    if not os.path.isfile(args.pptx):
        sys.exit(f"not found: {args.pptx}")
    deck = build(args.pptx, args.media_dir)
    print(json.dumps(deck, indent=2, ensure_ascii=False) if args.json else to_markdown(deck))


if __name__ == "__main__":
    main()
