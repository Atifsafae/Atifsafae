"""Turn the French unicorn coloring book into a KDP-ready English edition.

    python3 finalize.py      (needs: pip install pymupdf pillow numpy reportlab)

Input : source.pdf   (15 pages, 8.5 x 8.5 in, one 2125 px image per page)
Output: output/interior-KDP.pdf, output/cover-KDP.pdf, output/preview.pdf, output/*.png
"""
import io
import math
import os

import fitz  # pymupdf
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source.pdf")
OUT = os.path.join(HERE, "output")

TITLE = "My Super Unicorn Coloring Book"
SUBTITLE = "13 Magical Coloring Pages for Kids Ages 4-8"
AUTHOR = "Little Moon Crayons"
YEAR = 2026

TRIM = 8.5 * inch                  # 8.5 x 8.5 in square, a standard KDP trim size
MARGIN = 0.375 * inch              # KDP no-bleed minimum inside margin (24-150 pages); outside only needs 0.25
DPI = 300
PAPER = 0.002252                   # inch per page, white paper

# English banner for each colouring page (source page number -> text)
BANNERS = {
    3: "MAGIC BAKERY", 4: "SEASIDE HOLIDAY", 5: "WINTER WONDERLAND", 6: "RAINBOW SLIDE",
    7: "TREASURE CHEST", 8: "FLYING OVER CASTLES", 9: "CANDY LAND", 10: "FLOWER GARDEN",
    11: "SWEET DREAMS", 12: "THE ENCHANTED CASTLE", 13: "MUSHROOM FOREST", 14: "MERMAID UNICORN",
    15: "HAPPY BIRTHDAY, UNICORN!",
}

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DV", FONT_REG))
pdfmetrics.registerFont(TTFont("DVB", FONT_BOLD))


# ---------------------------------------------------------------- image fixes
def load_pages():
    doc = fitz.open(SRC)
    pages = []
    for p in doc:
        x = p.get_images(full=True)[0][0]
        pages.append(Image.open(io.BytesIO(doc.extract_image(x)["image"])).convert("L"))
    return pages


def whiten(im):
    """Remove the light-grey mock-up background: near-white greys become pure white."""
    return im.point(lambda v: 255 if v > 215 else v)


def text_image(text, height, max_w, stroke=0, squeeze=.78):
    """Render bold, slightly condensed capitals (like the original banner lettering)."""
    size = int(height * 1.35)
    while True:
        font = ImageFont.truetype(FONT_BOLD, size)
        l, t, r, b = font.getbbox(text, stroke_width=stroke)
        w = int((r - l) * squeeze)
        if w <= max_w or size < 10:
            break
        size -= 2
    img = Image.new("L", (r - l + 2 * stroke + 4, b - t + 2 * stroke + 4), 255)
    d = ImageDraw.Draw(img)
    if stroke:
        d.text((-l + stroke + 2, -t + stroke + 2), text, font=font, fill=255, stroke_width=stroke, stroke_fill=0)
    else:
        d.text((-l + 2, -t + 2), text, font=font, fill=0)
    return img.resize((max(1, int(img.width * squeeze)), img.height), Image.LANCZOS)


def paste_dark(base, img, cx, cy):
    """Paste text centred on (cx, cy), keeping the darker pixel (like multiply)."""
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    region = base.crop((x, y, x + img.width, y + img.height))
    base.paste(Image.fromarray(np.minimum(np.array(region), np.array(img))), (x, y))


def replace_banner(im, text):
    a = np.array(im)
    h, w = a.shape
    # the banner's top and bottom edges are the lowest two long horizontal lines
    def longest(r):
        d = np.diff(np.concatenate([[0], r.astype(int), [0]]))
        s, e = np.where(d == 1)[0], np.where(d == -1)[0]
        return (e - s).max() if len(s) else 0
    rows = [y for y in range(int(h * .86), h) if longest(a[y, int(w * .14):int(w * .86)] < 110) > w * .12]
    groups = []
    for y in rows:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    # banner = the lowest pair of lines 60-120 px apart (skips decorative lines inside)
    pairs = [(g1, g2) for i, g1 in enumerate(groups) for g2 in groups[i + 1:] if 60 <= g2[0] - g1[-1] <= 120]
    g1, g2 = max(pairs, key=lambda p: p[1][0])
    top, bot = g1[-1] + 1, g2[0] - 1
    # inner horizontal extent: follow the white run through the centre just under the top edge
    ys = top + 6
    row = a[ys] > 150
    cx = w // 2
    x0 = cx
    while x0 > 0 and row[x0 - 1]:
        x0 -= 1
    x1 = cx
    while x1 < w - 1 and row[x1 + 1]:
        x1 += 1
    pad = 6
    a[top + pad: bot - pad + 1, x0 + pad: x1 - pad] = 255
    out = Image.fromarray(a)
    t = text_image(text, (bot - top) * .55, (x1 - x0) - 40)
    paste_dark(out, t, (x0 + x1) / 2, (top + bot) / 2 + 1)
    return out


# ---------------------------------------------------------------- birthday page (page 15)
def clear_region(a, seed, shrink=4):
    """Flood the white area around `seed`, take its convex hull (which also covers any
    lettering inside it) and paint it white, keeping `shrink` px of the outline."""
    im = Image.fromarray(a)
    mask = Image.new("L", im.size, 0)
    bw = im.point(lambda v: 255 if v > 150 else 0)
    ImageDraw.floodfill(bw, seed, 128)
    m = np.array(bw) == 128
    ys, xs = np.nonzero(m)
    pts = np.stack([xs, ys], 1)
    hull = convex_hull(pts[:: max(1, len(pts) // 4000)])
    d = ImageDraw.Draw(mask)
    d.polygon([tuple(p) for p in hull], fill=255)
    mask = mask.filter(ImageFilter.MinFilter(2 * shrink + 1))
    a[np.array(mask) > 0] = 255
    return hull


def convex_hull(pts):
    pts = sorted(set(map(tuple, pts)))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def fix_birthday(im, flags_row1, flags_row2, plaque_seed):
    a = np.array(im)
    rows = [(flags_row1, list("HAPPY!")), (flags_row2, ["*", "♥", "B", "I", "R", "T", "H", "D", "A", "Y", "♥", "*", "!"])]
    out = []
    for seeds, letters in rows:
        for seed, ch in zip(seeds, letters):
            hull = clear_region(a, seed)
            xs = [p[0] for p in hull]
            ys = [p[1] for p in hull]
            out.append((ch, (min(xs) + max(xs)) / 2, min(ys) + (max(ys) - min(ys)) * .42, max(ys) - min(ys)))
    hull = clear_region(a, plaque_seed, 6)
    xs = [p[0] for p in hull]
    ys = [p[1] for p in hull]
    plaque = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys))
    img = Image.fromarray(a)
    for ch, cx, cy, fh in out:
        if ch == "*":
            t = star_img(int(fh * .2))
        elif ch == "♥":
            t = heart_img(int(fh * .17))
        else:
            t = text_image(ch, fh * .42, 999, stroke=5, squeeze=1.0)
        paste_dark(img, t, cx, cy)
    cx, cy, pw, ph = plaque
    ref = text_image("BIRTHDAY", ph * .22, pw * .72)
    for k, line in enumerate(["HAPPY", "BIRTHDAY"]):
        t = text_image(line, ref.height / 1.35 * .98, pw * .72)
        paste_dark(img, t, cx, cy + (k - .5) * ph * .3)
    return img


def star_img(r):
    img = Image.new("L", (2 * r + 8, 2 * r + 8), 255)
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * .45
        ang = math.radians(-90 + i * 36)
        pts.append((r + 4 + rr * math.cos(ang), r + 4 + rr * math.sin(ang)))
    ImageDraw.Draw(img).polygon(pts, outline=0, width=5)
    return img


def heart_img(s):
    img = Image.new("L", (int(2.6 * s) + 10, int(2.2 * s) + 10), 255)
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(80):
        t = i / 80 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((img.width / 2 + x * s / 13, img.height / 2 + y * s / 13))
    d.polygon(pts, outline=0, width=5)
    return img


def to_print(im):
    """Fit inside the margins and resample to 300 dpi (line art stays crisp)."""
    side = int(round((TRIM - 2 * MARGIN) / inch * DPI))
    im = im.resize((side, side), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=60, threshold=2))


# letter centres on the birthday page (source page 15), measured on the 2125 px image
ROW1 = [(745, 385), (865, 400), (990, 410), (1115, 410), (1235, 405), (1355, 385)]            # J O Y E U X
ROW2 = [(585, 565), (680, 570), (785, 580), (875, 585), (970, 600), (1090, 605), (1205, 600),
        (1320, 590), (1430, 585), (1540, 570), (1650, 550), (1775, 520), (1905, 480)]         # ANNIVERSAIRE!
PLAQUE = (1310, 1310)


def find_seed(a, c, wmin, wmax, hmin, hmax):
    """Find a white pixel whose white region encloses centre c with a plausible size."""
    cx, cy = c
    bw = Image.fromarray(np.where(a > 150, 255, 0).astype(np.uint8))
    tried = set()
    for r in range(20, 110, 6):
        for k in range(16):
            ang = 2 * math.pi * k / 16
            x, y = int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))
            if a[y, x] <= 150 or (x // 4, y // 4) in tried:
                continue
            tried.add((x // 4, y // 4))
            t = bw.copy()
            ImageDraw.floodfill(t, (x, y), 128)
            m = np.array(t) == 128
            ys, xs = np.nonzero(m)
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            if wmin <= x1 - x0 <= wmax and hmin <= y1 - y0 <= hmax and x0 < cx < x1 and y0 < cy < y1:
                return (x, y)
    raise RuntimeError(f"no seed found around {c}")


def birthday_page(im):
    a = np.array(im)
    s1 = [find_seed(a, c, 60, 170, 90, 230) for c in ROW1]
    s2 = [find_seed(a, c, 60, 170, 90, 230) for c in ROW2]
    sp = find_seed(a, PLAQUE, 220, 480, 120, 320)
    return fix_birthday(im, s1, s2, sp)


# ---------------------------------------------------------------- colour version for the cover
PASTEL = [(255, 179, 217), (205, 180, 255), (170, 220, 255), (170, 238, 205), (255, 236, 150),
          (255, 205, 170), (255, 150, 190), (190, 230, 160)]


def colorize(im, seed=1, sky=(222, 240, 255)):
    """Fill every closed white area of the line art with a pastel colour."""
    from scipy import ndimage
    rnd = np.random.default_rng(seed)
    a = np.array(im)
    white = a > 170
    lab, n = ndimage.label(white)
    sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    rgb = np.stack([a, a, a], -1).astype(np.float32)
    colours = np.zeros((n + 1, 3), np.float32)
    big = sizes.max()
    for i in range(1, n + 1):
        s = sizes[i - 1]
        if s == big or s > a.size * .08:
            colours[i] = sky
        elif s < 60:
            colours[i] = (255, 255, 255)
        else:
            colours[i] = PASTEL[rnd.integers(len(PASTEL))]
    fill = colours[lab]
    shade = (a.astype(np.float32) / 255.0)[..., None]
    out = np.where(white[..., None], fill, rgb * shade / np.maximum(shade, 1e-3) * 0 + a[..., None])
    # anti-aliased edge pixels: blend the line colour towards the fill
    out = np.where(white[..., None], fill * shade + 0 * (1 - shade), out)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- PDF building
def fixed_pages():
    """The 13 coloring pages, cleaned, translated and ready to print (300 dpi)."""
    pages = load_pages()
    out = []
    for n in range(3, 16):
        im = whiten(pages[n - 1])
        if n == 15:
            im = birthday_page(im)
        im = replace_banner(im, BANNERS[n])
        out.append((n, im))
    return out


def star(c, x, y, r, fill=None):
    p = c.beginPath()
    for i in range(10):
        rr = r if i % 2 == 0 else r * .45
        a = math.radians(90 + i * 36)
        (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close()
    if fill:
        c.setFillColorRGB(*fill)
    c.drawPath(p, stroke=1, fill=1 if fill else 0)


def heart(c, x, y, s, fill=None):
    p = c.beginPath()
    for i in range(60):
        t = i / 60 * 2 * math.pi
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        (p.moveTo if i == 0 else p.lineTo)(x + hx * s / 16, y + hy * s / 16)
    p.close()
    if fill:
        c.setFillColorRGB(*fill)
    c.drawPath(p, stroke=1, fill=1 if fill else 0)


def title_page(c):
    W = TRIM
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1.6)
    for x, y, r in [(1.0, 7.4, 14), (7.5, 7.5, 16), (1.3, 1.2, 12), (7.2, 1.1, 13), (4.25, 7.8, 9),
                    (0.9, 4.2, 9), (7.6, 4.3, 9)]:
        star(c, x * inch, y * inch, r)
    for x, y in [(2.2, 7.7), (6.3, 7.7)]:
        heart(c, x * inch, y * inch, 12)
    c.setFillColorRGB(0.45, 0.25, 0.65)
    c.setFont("DVB", 30)
    c.drawCentredString(W / 2, 6.55 * inch, "My Super Unicorn")
    c.drawCentredString(W / 2, 6.0 * inch, "Coloring Book")
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.setFont("DV", 14)
    c.drawCentredString(W / 2, 5.5 * inch, SUBTITLE)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(2.5)
    c.roundRect(1.5 * inch, 2.7 * inch, 5.5 * inch, 1.9 * inch, 18)
    c.setFont("DVB", 18)
    c.drawCentredString(W / 2, 4.05 * inch, "THIS BOOK BELONGS TO:")
    c.setLineWidth(1.2)
    c.setDash(2, 4)
    c.line(2.1 * inch, 3.25 * inch, 6.4 * inch, 3.25 * inch)
    c.setDash()
    c.setFont("DV", 12)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(W / 2, 1.75 * inch, f"by {AUTHOR}")
    c.showPage()


def copyright_page(c):
    W = TRIM
    c.setFont("DV", 9.5)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    lines = [f"{TITLE}", f"Copyright © {YEAR} {AUTHOR}. All rights reserved.", "",
             "No part of this book, including its illustrations, may be reproduced,",
             "distributed or resold, in whole or in part, without prior written",
             "permission from the publisher, except for personal and family use.", "",
             "Illustrations created with the assistance of artificial intelligence tools,",
             "then selected, edited and arranged by the author.", "",
             "Independently published."]
    y = 3.4 * inch
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= 14
    c.showPage()


def certificate_page(c):
    W = TRIM
    c.setLineWidth(2.5)
    c.setDash(1, 6)
    c.roundRect(0.5 * inch, 0.5 * inch, W - inch, W - inch, 22)
    c.setDash()
    c.setLineWidth(3.5)
    c.roundRect(0.7 * inch, 0.7 * inch, W - 1.4 * inch, W - 1.4 * inch, 16)
    c.setLineWidth(1.8)
    for x, y, r in [(1.3, 7.2, 16), (7.2, 7.2, 16), (1.3, 1.3, 14), (7.2, 1.3, 14), (4.25, 7.55, 11)]:
        star(c, x * inch, y * inch, r)
    c.setFont("DVB", 32)
    c.drawCentredString(W / 2, 6.35 * inch, "WELL DONE,")
    c.drawCentredString(W / 2, 5.8 * inch, "LITTLE ARTIST!")
    c.setFont("DV", 16)
    c.drawCentredString(W / 2, 4.85 * inch, "This magical coloring book was completed by:")
    c.setLineWidth(1.3)
    c.setDash(2, 4)
    c.line(1.9 * inch, 4.05 * inch, 6.6 * inch, 4.05 * inch)
    c.setDash()
    c.setFont("DV", 14)
    c.drawString(2.4 * inch, 3.25 * inch, "Date:")
    c.setDash(2, 4)
    c.line(3.05 * inch, 3.22 * inch, 6.1 * inch, 3.22 * inch)
    c.setDash()
    c.setLineWidth(1.8)
    for x in (3.35, 4.25, 5.15):
        heart(c, x * inch, 2.35 * inch, 18)
    c.setFont("DV", 10)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(W / 2, 1.32 * inch, "Grown-ups: if your little one enjoyed this book,")
    c.drawCentredString(W / 2, 1.15 * inch, "a review on Amazon helps us a lot!")
    c.showPage()


def img_reader(im, fmt="PNG"):
    b = io.BytesIO()
    im.save(b, fmt, optimize=True) if fmt == "PNG" else im.save(b, fmt, quality=95)
    b.seek(0)
    return ImageReader(b)


def build_interior(pages, path, blanks=True):
    c = canvas.Canvas(path, pagesize=(TRIM, TRIM), initialFontName="DV")
    c.setTitle(TITLE)
    c.setAuthor(AUTHOR)
    title_page(c)
    copyright_page(c)
    n = 2
    side = TRIM - 2 * MARGIN
    for _, im in pages:
        c.drawImage(img_reader(to_print(im)), MARGIN, MARGIN, width=side, height=side)
        c.showPage()
        n += 1
        if blanks:
            c.showPage()                      # blank back: markers won't bleed through
            n += 1
    certificate_page(c)
    n += 1
    if n % 2:
        c.showPage()
        n += 1
    c.save()
    return n


def build_cover(n_pages, pages):
    bleed = 0.125 * inch
    spine = n_pages * PAPER * inch
    W, H = 2 * bleed + 2 * TRIM + spine, TRIM + 2 * bleed
    path = os.path.join(OUT, "cover-KDP.pdf")
    c = canvas.Canvas(path, pagesize=(W, H), initialFontName="DV")
    pink, lilac, purple = (1, .88, .94), (.86, .8, 1), (.45, .25, .68)
    c.setFillColorRGB(*pink)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColorRGB(*lilac)
    c.rect(bleed + TRIM, 0, spine, H, stroke=0, fill=1)
    fx = bleed + TRIM + spine                               # left edge of the front cover (trim)

    # ---- front: coloured illustration + title
    art = colorize(dict(pages)[8], seed=8).crop((70, 70, 2055, 1965))
    size = 6.1 * inch
    ax, ay = fx + (TRIM - size) / 2, bleed + 0.45 * inch
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*purple)
    c.setLineWidth(5)
    c.roundRect(ax - 8, ay - 8, size + 16, size * art.height / art.width + 16, 22, stroke=1, fill=1)
    c.drawImage(img_reader(art, "JPEG"), ax, ay, width=size, height=size * art.height / art.width)
    ty = ay + size * art.height / art.width + 0.12 * inch
    c.setFillColorRGB(*purple)
    c.setFont("DVB", 34)
    c.drawCentredString(fx + TRIM / 2, ty + 0.95 * inch, "My Super Unicorn")
    c.setFillColorRGB(.95, .35, .62)
    c.setFont("DVB", 30)
    c.drawCentredString(fx + TRIM / 2, ty + 0.5 * inch, "COLORING BOOK")
    c.setFillColorRGB(*purple)
    c.setFont("DV", 14)
    c.drawCentredString(fx + TRIM / 2, ty + 0.16 * inch, f"for Kids Ages 4-8   •   by {AUTHOR}")
    # age badge
    bx, by = fx + TRIM - 1.0 * inch, bleed + TRIM - 0.95 * inch
    c.setFillColorRGB(1, .93, .55)
    c.setStrokeColorRGB(*purple)
    c.setLineWidth(3)
    c.circle(bx, by, 0.5 * inch, stroke=1, fill=1)
    c.setFillColorRGB(*purple)
    c.setFont("DVB", 13)
    c.drawCentredString(bx, by + 4, "AGES")
    c.drawCentredString(bx, by - 13, "4-8")
    c.setStrokeColorRGB(*purple)
    c.setLineWidth(1.5)
    for x, y, r in [(0.7, 7.9, 12), (1.4, 7.3, 8), (7.0, 6.9, 8)]:
        star(c, fx + x * inch, bleed + y * inch, r, fill=(1, .93, .55))

    # ---- back: blurb + 4 page previews (lower-right corner left free for the barcode)
    bx0 = bleed
    c.setFillColorRGB(*purple)
    c.setFont("DVB", 22)
    c.drawCentredString(bx0 + TRIM / 2, bleed + TRIM - 0.9 * inch, "A World of Magical Unicorns to Color!")
    c.setFillColorRGB(.2, .2, .2)
    c.setFont("DV", 12.5)
    blurb = ["13 adorable unicorn scenes: a magic bakery, the seaside, candy land,",
             "castles, a mermaid unicorn, a birthday party and much more.",
             "Single-sided pages (no bleed-through) • Big, bold lines for little hands",
             "A \"Well done, little artist!\" certificate at the end"]
    y = bleed + TRIM - 1.35 * inch
    for line in blurb:
        c.drawCentredString(bx0 + TRIM / 2, y, line)
        y -= 18
    thumbs = [dict(pages)[k] for k in (4, 9, 14, 15)]
    ts = 2.35 * inch
    pos = [(0.75, 3.0), (3.2, 3.0), (0.75, 0.5), (3.2, 0.5)]
    for im, (x, y) in zip(thumbs, pos):
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(*purple)
        c.setLineWidth(2)
        c.roundRect(bx0 + x * inch - 5, bleed + y * inch - 5, ts + 10, ts + 10, 10, stroke=1, fill=1)
        c.drawImage(img_reader(im.resize((800, 800), Image.LANCZOS)), bx0 + x * inch, bleed + y * inch, width=ts, height=ts)
    c.save()
    return path, W / inch, H / inch, spine / inch


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = fixed_pages()
    n = build_interior(pages, os.path.join(OUT, "interior-KDP.pdf"))
    build_interior(pages, os.path.join(OUT, "preview-no-blank-pages.pdf"), blanks=False)
    cover, w, h, sp = build_cover(n, pages)
    colorize(dict(pages)[8], seed=8).resize((1200, 1200)).save(os.path.join(OUT, "cover-art-colour.jpg"), quality=92)
    for k in (3, 8, 15):
        dict(pages)[k].resize((1200, 1200)).save(os.path.join(OUT, f"page-{k:02d}-english.png"))
    print(f"interior: {n} pages (8.5 x 8.5 in)\ncover: {w:.4f} x {h:.4f} in, spine {sp:.4f} in")


if __name__ == "__main__":
    main()
