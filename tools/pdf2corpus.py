#!/usr/bin/env python3
"""
pdf2corpus.py — PDF to clean text for RAG corpora.

Handles single- and two-column layouts, strips repeated headers/footers,
de-hyphenates line breaks, and leaves figure placeholders where images sat.

Usage:
    python3 pdf2corpus.py input.pdf -o out/
    python3 pdf2corpus.py input.pdf -o out/ --columns 2      # force 2 columns
    python3 pdf2corpus.py input.pdf -o out/ --extract-images # dump figures too
    python3 pdf2corpus.py input.pdf -o out/ --page-markers   # keep [[page N]]

Outputs:
    <stem>.txt    one continuous cleaned text file
    <stem>.jsonl  one JSON record per page: {page, text, n_figures}

Requires: pymupdf  (pip install pymupdf)
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

import pymupdf


# ----------------------------------------------------------------- layout

def page_blocks(page):
    """Text blocks as (x0, y0, x1, y1, text), image-free, in raw order."""
    out = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text, _no, btype = b
        if btype != 0:
            continue
        text = text.strip()
        if text:
            out.append((x0, y0, x1, y1, text))
    return out


def detect_columns(blocks, page_width):
    """Return 2 if a clean vertical gutter splits the page, else 1."""
    if len(blocks) < 6:
        return 1
    centre = page_width / 2
    band = page_width * 0.04            # +/- 4% of width around the centre
    crossers = sum(1 for x0, _, _, x1, _ in
                   ((b[0], b[1], b[2], b[3], b[4]) for b in blocks)
                   if x0 < centre - band and x1 > centre + band)
    # blocks sitting wholly on one side of the centre line
    left = sum(1 for b in blocks if b[2] <= centre + band)
    right = sum(1 for b in blocks if b[0] >= centre - band)
    if left >= 3 and right >= 3 and crossers <= max(1, len(blocks) * 0.15):
        return 2
    return 1


def order_two_column(blocks, page_width):
    """
    Read order for a two-column page.

    Full-width blocks (headings, tables, banners) break the page into bands;
    within each band we read the left column top-to-bottom, then the right.
    """
    centre = page_width / 2
    full_width_min = page_width * 0.70

    blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
    ordered, left, right = [], [], []

    def flush():
        ordered.extend(sorted(left, key=lambda b: b[1]))
        ordered.extend(sorted(right, key=lambda b: b[1]))
        left.clear()
        right.clear()

    for b in blocks:
        x0, _y0, x1, _y1, _t = b
        if (x1 - x0) >= full_width_min:
            flush()
            ordered.append(b)
        elif (x0 + x1) / 2 < centre:
            left.append(b)
        else:
            right.append(b)
    flush()
    return ordered


# ----------------------------------------------------------------- cleaning

PAGE_NUM_RE = re.compile(r"^\s*(page\s*)?[ivxlcdm\d]{1,6}\s*(of\s*\d+)?\s*$", re.I)


EDGE = 2          # how many lines at each end count as "header/footer zone"


def find_running_lines(page_texts, threshold=0.7):
    """
    Lines that repeat near the top or bottom of most pages = header/footer.

    Digit-normalised so "Page 4 of 60" collapses with "Page 5 of 60", but a
    normalised match only counts when the line is short — otherwise numbered
    headings ("CHAPTER 3: ...") get eaten as running text.
    """
    if len(page_texts) < 4:
        return set()
    counts = Counter()
    for txt in page_texts:
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        for l in lines[:EDGE] + lines[-EDGE:]:
            counts[norm_line(l)] += 1
    cutoff = len(page_texts) * threshold
    return {k for k, v in counts.items() if v >= cutoff}


def norm_line(s):
    return re.sub(r"\d+", "#", s) if len(s) <= 60 else s


def strip_running(text, running):
    kept, dropped = [], []
    lines = [l.rstrip() for l in text.splitlines()]
    for i, line in enumerate(lines):
        s = line.strip()
        near_edge = i < EDGE or i >= len(lines) - EDGE
        if near_edge and s and (norm_line(s) in running or PAGE_NUM_RE.match(s)):
            dropped.append(s)
            continue
        kept.append(line)
    return "\n".join(kept), dropped


def dehyphenate(text):
    # join "compli-\nance" but leave "e-\nmail"-style false positives rare enough
    text = re.sub(r"(\w{2,})-\n(\w)", r"\1\2", text)
    # unwrap soft line breaks inside a sentence, keep paragraph breaks
    text = re.sub(r"(?<=[a-z,;:])\n(?=[a-z(])", " ", text)
    return text


def tidy(text):
    text = text.replace("\u00ad", "")                     # soft hyphen
    # Contents-page dot leaders. The glyph the Strategy uses for them has no
    # Unicode mapping, so it decodes to U+FFFD and arrives as runs like
    # ".<FFFD>.<FFFD>." \u2014 610 characters of pure noise that would otherwise be
    # indexed as chunk content. {4,} never matches a real ellipsis or a numbered
    # heading like "3.4.2.", where dots are separated by digits.
    text = re.sub("[.\ufffd]{4,}", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)   # stray control bytes
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ----------------------------------------------------------------- main

def convert(pdf_path, outdir, force_columns=None, extract_images=False,
            page_markers=False, keep_running=False):
    doc = pymupdf.open(pdf_path)
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs(outdir, exist_ok=True)
    img_dir = os.path.join(outdir, f"{stem}_images")

    raw_pages, fig_counts = [], []

    for pno, page in enumerate(doc, start=1):
        blocks = page_blocks(page)
        width = page.rect.width
        ncols = force_columns or detect_columns(blocks, width)
        if ncols == 2:
            blocks = order_two_column(blocks, width)
        else:
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

        body = "\n\n".join(b[4] for b in blocks)

        images = page.get_images(full=True)
        if images:
            body += f"\n\n[FIGURE: {len(images)} image(s) on page {pno}]"
        if extract_images and images:
            os.makedirs(img_dir, exist_ok=True)
            for xref, *_ in images:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n - pix.alpha > 3:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                pix.save(os.path.join(img_dir, f"p{pno:03d}_x{xref}.png"))

        raw_pages.append(body)
        fig_counts.append(len(images))

    running = set() if keep_running else find_running_lines(raw_pages)
    clean_pages, dropped_all = [], Counter()
    for p in raw_pages:
        body, dropped = strip_running(p, running)
        dropped_all.update(dropped)
        clean_pages.append(tidy(dehyphenate(body)))

    txt_path = os.path.join(outdir, f"{stem}.txt")
    jsonl_path = os.path.join(outdir, f"{stem}.jsonl")

    parts = []
    for i, p in enumerate(clean_pages, start=1):
        if page_markers:
            parts.append(f"[[page {i}]]\n{p}")
        else:
            parts.append(p)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts) + "\n")

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for i, p in enumerate(clean_pages, start=1):
            f.write(json.dumps({
                "source": os.path.basename(pdf_path),
                "page": i,
                "text": p,
                "n_figures": fig_counts[i - 1],
            }, ensure_ascii=False) + "\n")

    chars = sum(len(p) for p in clean_pages)
    print(f"{stem}: {len(doc)} pages, {chars:,} chars, {sum(fig_counts)} images")
    if dropped_all:
        print("  stripped as header/footer (check these are not real content):")
        for line, n in dropped_all.most_common(8):
            print(f"    {n:>4}x  {line[:70]}")
    print(f"  -> {txt_path}\n  -> {jsonl_path}")
    return txt_path, jsonl_path


def main():
    ap = argparse.ArgumentParser(description="PDF to clean text for RAG.")
    ap.add_argument("pdf", nargs="+")
    ap.add_argument("-o", "--outdir", default="corpus")
    ap.add_argument("--columns", type=int, choices=[1, 2], default=None,
                    help="force column count instead of auto-detecting")
    ap.add_argument("--extract-images", action="store_true")
    ap.add_argument("--page-markers", action="store_true",
                    help="keep [[page N]] markers for citation back to the PDF")
    ap.add_argument("--keep-running", action="store_true",
                    help="do not strip repeated headers/footers")
    a = ap.parse_args()
    for path in a.pdf:
        if not os.path.exists(path):
            print(f"skip (not found): {path}", file=sys.stderr)
            continue
        convert(path, a.outdir, a.columns, a.extract_images, a.page_markers,
                a.keep_running)


if __name__ == "__main__":
    main()