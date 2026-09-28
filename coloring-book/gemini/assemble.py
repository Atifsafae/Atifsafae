"""Assemble Gemini coloring pages into a KDP-ready book.

"My Magical Winged Unicorn: A Colouring Storybook" - 8.5 x 11 in, no bleed.

1. Put ONE image per page in  gemini/images/  named with its number first,
   e.g.  01-magical-garden.png, 02-magic-bakery.jpg ... 39-trampoline-jump.png
   (number = position in THEMES below; the rest of the name does not matter).
   Optional: gemini/images/cover.png  = the colour front cover (portrait).
2. python3 assemble.py            -> gemini/output/*.pdf + a quality report
   python3 assemble.py --draft    -> allow missing / low-resolution pages (preview only)

Page order: 1 "This book belongs to" | 2 copyright | then each design followed by
a blank back (so markers don't bleed through) | last: the colouring certificate.
"""
import io
import os
import re
import sys

from PIL import Image, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
OUT_DIR = os.path.join(HERE, "output")

TITLE = "MY MAGICAL WINGED UNICORN"
SUBTITLE = "A Colouring Storybook for Kids Ages 4+"
AUTHOR = "Rainbow Pencil Press"        # <- your pen name / brand
YEAR = 2026

PAGE_W, PAGE_H = letter                # 612 x 792 pt = 8.5 x 11 in
MARGIN = 0.5 * inch                    # KDP no-bleed: >= 0.375 in inside, 0.25 in outside
TARGET_DPI = 300                       # KDP recommends 300 dpi
MIN_DPI = 200                          # below this we refuse (unless --draft)
PAPER = 0.002252                       # in per page, white paper (spine width)

THEMES = [
    "Magical Garden", "Magic Bakery", "Seaside Holiday", "Rainbow Slide", "Castle Overflight",
    "Starry Night", "Underwater Adventure", "Space Exploration", "Country Picnic", "Magic Circus",
    "Art Studio", "Roller Skating Fun", "Gardening Time", "Musical Melodies", "Story Time",
    "Birthday Party", "Magic Potions", "The Rainbow Express", "Dragon Friends", "Winter Snow Fun",
    "Sky Explorer", "Nature's Band", "Stargazing Adventure", "Pottery Studio", "Flower Market",
    "Friendly Bridge", "River Fishing Trip", "Coral Reef Discovery", "Scooter Ride", "Flying Over Castles",
    "Road Trip Adventure", "Observatory Star Gazing", "Painting a Rainbow", "Geology Explorer",
    "Reading in a Cozy Fort", "Sandcastle Creator", "Tightrope Acrobat", "Singing Birds Concert",
    "Trampoline Jump", "Colouring Completed Certificate",
]
CERTIFICATE = len(THEMES)              # page 40 is drawn by this script (crisp, editable text)


# ---------------------------------------------------------------- images
def find_images():
    found = {}
    if not os.path.isdir(IMG_DIR):
        return found
    for name in sorted(os.listdir(IMG_DIR)):
        m = re.match(r"^(\d{1,2})\D", name)
        if m and name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            found.setdefault(int(m.group(1)), os.path.join(IMG_DIR, name))
    return found


def trim_white(im, pad=20):
    """Crop the white border Gemini often leaves around the drawing."""
    bw = im.point(lambda v: 0 if v > 245 else 255)
    box = bw.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def prepare(path, box_w_in, box_h_in):
    """Grayscale, trim, and (if needed) upscale line art so it prints at 300 dpi.

    Returns (image, draw_w_pt, draw_h_pt, original_dpi)."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
        im = bg
    im = trim_white(im.convert("L"))
    ratio = min(box_w_in / im.width, box_h_in / im.height)
    w_in, h_in = im.width * ratio, im.height * ratio
    dpi = im.width / w_in
    if dpi < TARGET_DPI:
        # Line-art upscale: smooth enlargement, then re-sharpen the black lines.
        scale = TARGET_DPI / dpi
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
        im = im.point(lambda v: 0 if v < 90 else 255 if v > 200 else int((v - 90) * 255 / 110))
    return im, w_in * inch, h_in * inch, dpi


def draw_image_page(c, path):
    box_w, box_h = (PAGE_W - 2 * MARGIN) / inch, (PAGE_H - 2 * MARGIN) / inch
    im, dw, dh, dpi = prepare(path, box_w, box_h)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    buf.seek(0)
    x = (PAGE_W - dw) / 2
    y = (PAGE_H - dh) / 2
    c.drawImage(ImageReader(buf), x, y, width=dw, height=dh)
    return dpi


# ---------------------------------------------------------------- text pages
def belongs_page(c):
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.6 * inch, TITLE)
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.1 * inch, SUBTITLE)
    c.setLineWidth(2.5)
    c.roundRect(PAGE_W / 2 - 2.8 * inch, PAGE_H / 2 - 0.9 * inch, 5.6 * inch, 1.8 * inch, 18)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 0.35 * inch, "THIS BOOK BELONGS TO:")
    c.setLineWidth(1.2)
    c.setDash(2, 4)
    c.line(PAGE_W / 2 - 2.2 * inch, PAGE_H / 2 - 0.35 * inch, PAGE_W / 2 + 2.2 * inch, PAGE_H / 2 - 0.35 * inch)
    c.setDash()
    _stars(c)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(PAGE_W / 2, 1.5 * inch, "Grab your crayons, pencils and sparkles!")
    c.showPage()


def copyright_page(c):
    c.setFont("Helvetica", 9)
    lines = [f"{TITLE.title()}: A Colouring Storybook",
             f"Copyright © {YEAR} {AUTHOR}. All rights reserved.",
             f"First Edition: {YEAR}", "",
             "No part of this publication may be reproduced, stored or transmitted",
             "in any form without prior written permission from the publisher.",
             "Independently published."]
    y = 2.5 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 14
    c.showPage()


def certificate_page(c):
    c.setLineWidth(3)
    c.setDash(1, 6)
    c.roundRect(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, 22)
    c.setDash()
    c.setLineWidth(3)
    c.roundRect(MARGIN + 18, MARGIN + 18, PAGE_W - 2 * MARGIN - 36, PAGE_H - 2 * MARGIN - 36, 16)
    _stars(c, big=True)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.2 * inch, "COLOURING")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.75 * inch, "COMPLETED!")
    c.setFont("Helvetica", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 0.9 * inch, "This magical journey was coloured by:")
    c.setLineWidth(1.4)
    c.setDash(2, 4)
    c.line(PAGE_W / 2 - 2.5 * inch, PAGE_H / 2, PAGE_W / 2 + 2.5 * inch, PAGE_H / 2)
    c.setDash()
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 0.9 * inch, "Date:")
    c.setDash(2, 4)
    c.line(PAGE_W / 2 - 1.5 * inch, PAGE_H / 2 - 1.3 * inch, PAGE_W / 2 + 1.5 * inch, PAGE_H / 2 - 1.3 * inch)
    c.setDash()
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(PAGE_W / 2, 2.2 * inch, "Well done, little artist! You are a true unicorn star.")
    c.showPage()


def _star(c, x, y, r):
    import math
    p = c.beginPath()
    for i in range(10):
        rr = r if i % 2 == 0 else r * .45
        a = math.radians(-90 + i * 36)
        (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(a), y - rr * math.sin(a))
    p.close()
    c.setLineWidth(1.6)
    c.drawPath(p, stroke=1, fill=0)


def _stars(c, big=False):
    s = 1.4 if big else 1.0
    for x, y, r in [(1.3, 9.5, 14), (7.2, 9.6, 16), (1.1, 1.3, 12), (7.4, 1.2, 14), (4.25, 9.95, 10),
                    (2.0, 3.5, 9), (6.5, 3.4, 9)]:
        _star(c, x * inch, y * inch, r * s)


def placeholder(c, n, name):
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 12, f"{n:02d}. {name}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 14, "(image missing - add it to gemini/images/)")
    c.showPage()


# ---------------------------------------------------------------- book
def build(draft=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    images = find_images()
    report, problems = [], []
    for n, name in enumerate(THEMES, 1):
        if n == CERTIFICATE:
            continue
        if n not in images:
            problems.append(f"{n:02d} {name}: MISSING")
    interior = os.path.join(OUT_DIR, "interior-KDP.pdf" if not draft else "interior-DRAFT.pdf")
    preview = os.path.join(OUT_DIR, "preview-no-blank-pages.pdf" if not draft else "preview-DRAFT.pdf")

    for path, blanks in ((interior, True), (preview, False)):
        c = canvas.Canvas(path, pagesize=letter)
        c.setTitle(f"{TITLE.title()}: A Colouring Storybook")
        c.setAuthor(AUTHOR)
        belongs_page(c)
        if blanks:
            copyright_page(c)
        pages = 2 if blanks else 1
        for n, name in enumerate(THEMES, 1):
            if n == CERTIFICATE:
                certificate_page(c)
                pages += 1
                continue
            if n in images:
                dpi = draw_image_page(c, images[n])
                c.showPage()
                if blanks:
                    tag = "OK" if dpi >= TARGET_DPI else ("upscaled" if dpi >= MIN_DPI else "TOO SMALL")
                    report.append(f"{n:02d} {name:32s} {os.path.basename(images[n]):40s} {dpi:5.0f} dpi  {tag}")
                    if dpi < MIN_DPI:
                        problems.append(f"{n:02d} {name}: only {dpi:.0f} dpi - regenerate bigger")
            else:
                placeholder(c, n, name)
            pages += 1
            if blanks:
                c.showPage()                 # blank back
                pages += 1
        if blanks and pages % 2:
            c.showPage()
            pages += 1
        c.save()
        if blanks:
            n_pages = pages

    cover = build_cover(n_pages)
    print("\n".join(report))
    print(f"\ninterior: {n_pages} pages -> {interior}\ncover: {cover}")
    if problems:
        print("\nPROBLEMS:\n  " + "\n  ".join(problems))
        if not draft:
            print("\nNot ready for KDP yet. Fix the problems above (or run with --draft for a preview).")
            sys.exit(1)
    return n_pages


def build_cover(n_pages):
    """Full wrap cover: back | spine | front, with 0.125 in bleed."""
    bleed = 0.125 * inch
    spine = n_pages * PAPER * inch
    W, H = 2 * bleed + 2 * PAGE_W + spine, PAGE_H + 2 * bleed
    path = os.path.join(OUT_DIR, "cover-KDP.pdf")
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setFillColorRGB(1, .86, .94)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColorRGB(.72, .6, 1)
    c.rect(bleed + PAGE_W, 0, spine, H, stroke=0, fill=1)
    fx = bleed + PAGE_W + spine
    front = os.path.join(IMG_DIR, "cover.png")
    if not os.path.exists(front):
        front = next((os.path.join(IMG_DIR, f) for f in os.listdir(IMG_DIR) if f.lower().startswith("cover")), None) \
            if os.path.isdir(IMG_DIR) else None
    if front:
        im = Image.open(front).convert("RGB")
        fw, fh = PAGE_W + bleed, H
        r = max(fw / im.width, fh / im.height)                 # fill the front panel, crop the excess
        cw, ch = fw / r, fh / r
        im = im.crop(((im.width - cw) / 2, (im.height - ch) / 2, (im.width + cw) / 2, (im.height + ch) / 2))
        c.drawImage(ImageReader(im), fx, 0, width=fw, height=fh)
    else:
        c.setFillColorRGB(.2, .2, .2)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(fx + PAGE_W / 2, H / 2, "(put your front cover in images/cover.png)")
    # back cover text (lower right is left empty for the KDP barcode)
    c.setFillColorRGB(.25, .15, .45)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(bleed + PAGE_W / 2, H - 1.6 * inch, "A magical adventure to colour!")
    c.setFont("Helvetica", 16)
    lines = ["39 adorable winged-unicorn adventures:", "baking, painting, space, the seaside,",
             "castles, circus, dragons and much more!", "",
             "- Single-sided pages: no bleed-through", "- Large 8.5 x 11 in pages",
             "- Bold, clear lines for little hands", "- A colouring certificate to sign at the end",
             "", "Perfect for children aged 4 and up."]
    y = H - 2.4 * inch
    for line in lines:
        c.drawString(bleed + 1.0 * inch, y, line)
        y -= 24
    if spine >= 0.25 * inch:
        c.saveState()
        c.translate(bleed + PAGE_W + spine / 2, H / 2)
        c.rotate(-90)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", min(14, spine * .55))
        c.drawCentredString(0, -4, TITLE)
        c.restoreState()
    c.save()
    return f"{path}  ({W / inch:.3f} x {H / inch:.3f} in, spine {spine / inch:.3f} in)"


if __name__ == "__main__":
    build(draft="--draft" in sys.argv)
