"""Build "Mon Super Coloriage Licorne": 60 designs, KDP-ready interior + cover.

    python3 build.py            -> ../output/livre-licorne/...
    python3 build.py sheet      -> contact sheets only (quick review)
"""
import io
import os
import random
import sys

import cairosvg
from pypdf import PdfReader, PdfWriter

from themes import X0, X1, Y0, Y1, Space, U, design_list, portrait, scatter
from scenery import *
from unicorn2 import unicorn

TITLE = "Mon Super Coloriage Licorne"
SUBTITLE = "60 dessins magiques - 4 à 8 ans"
AUTHOR = "Rainbow Pencil Press"          # <- ton nom d'auteur / ta marque
PAPER = 0.002252                         # inch per page, white paper
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "livre-licorne")
PW, PH = 850, 1100
FONT = "DejaVu Sans"


def esc(s):
    return s.replace("&", "&amp;").replace("'", "&#39;")


def svg(body, w=PW, h=PH, bg="#fff"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / 100}in" height="{h / 100}in" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


def banner(text, y=1022, size=24):
    w = max(300, len(text) * size * .66 + 90)
    x0, x1 = 425 - w / 2, 425 + w / 2
    o = (fill_path(f"M{f(x0 - 40)},{f(y - 14)} h54 v44 h-54 l18,-22 Z", OW - 1)
         + fill_path(f"M{f(x1 + 40)},{f(y - 14)} h-54 v44 h54 l-18,-22 Z", OW - 1)
         + fill_path(f"M{f(x0)},{f(y - 26)} H{f(x1)} V{f(y + 22)} H{f(x0)} Z", OW))
    o += (f'<text x="425" y="{f(y + size * .36)}" font-family="{FONT}" font-weight="bold" font-size="{size}" '
          f'fill="{INK}" text-anchor="middle" letter-spacing="1">{esc(text.upper())}</text>')
    return o


def framed(scene, caption):
    clip = f'<defs><clipPath id="in"><rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="14"/></clipPath></defs>'
    outer = (f'<rect x="38" y="38" width="774" height="1024" rx="26" fill="none" stroke="{INK}" '
             f'stroke-width="3" stroke-dasharray="0.1 9" stroke-linecap="round"/>')
    inner = f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="14" fill="none" stroke="{INK}" stroke-width="{OW}"/>'
    return svg(clip + outer + f'<g clip-path="url(#in)">{scene}</g>' + inner + banner(caption))


def design_pages():
    pages = []
    for t, v, seed in design_list():
        b, cap = t(v, random.Random(seed))
        pages.append((framed("".join(b), cap), cap))
    return pages


# ---------------------------------------------------------------- extra pages
def text(x, y, s, size, weight="bold", anchor="middle", fill=INK, stroke_w=0, stroke_c=INK):
    st = f' stroke="{stroke_c}" stroke-width="{stroke_w}" paint-order="stroke" stroke-linejoin="round"' if stroke_w else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{st}>{esc(s)}</text>')


def belongs_page():
    sp = Space()
    b = [text(425, 150, "Ce livre appartient à", 52),
         g(unicorn(pose="lie", eyes="closed", accessory="roses"), 430, 560, .85),
         flower_bed(640, 3, dense=.9),
         fill_path("M170,860 H680 V930 H170 Z", OW),
         text(425, 1000, f"{TITLE} - © {AUTHOR}", 20, "normal")]
    rnd = random.Random(5)
    for x, y in [(130, 300), (730, 300)]:
        b.append(butterfly(x, y, .45, rnd.uniform(-20, 20)))
    return svg("".join(b))


def test_colors_page():
    b = [text(425, 130, "Teste tes couleurs ici !", 46)]
    for r in range(4):
        for c in range(4):
            x, y = 170 + c * 170, 280 + r * 170
            k = (r + c) % 4
            b.append(heart(x, y, 55, w=OW) if k == 0 else star(x, y, 64, w=OW) if k == 1 else
                     circ(x, y, 58, OW) if k == 2 else rose(x, y, 58))
    b.append(text(425, 1000, "Essaie tes crayons et feutres avant de commencer.", 24, "normal"))
    return svg("".join(b))


def thanks_page():
    b = [text(425, 180, "Bravo, petite artiste !", 50),
         g(unicorn(pose="prance", wings="fairy", accessory="crown"), 420, 620, .8),
         flower_bed(840, 9, dense=.9),
         text(425, 1000, "Si ce livre t'a plu, un petit avis nous aide beaucoup !", 22, "normal")]
    return svg("".join(b))


def blank():
    return svg("")


def to_pdf(svgs, path):
    w = PdfWriter()
    for s in svgs:
        w.append(PdfReader(io.BytesIO(cairosvg.svg2pdf(bytestring=s.encode()))))
    with open(path, "wb") as fh:
        w.write(fh)


# ---------------------------------------------------------------- colour cover
PAL = dict(pink="#ff9fd0", rose="#ff6fae", lilac="#c9a7ff", purple="#9b6bff", blue="#8fd3ff", mint="#8ee8c4",
           yellow="#ffe27a", peach="#ffc49a", sky="#e6f4ff", grass="#b6eb8f", cream="#fffafd")


def colorize(art, rnd):
    """Turn white fills of line art into a pastel palette (for the cover)."""
    out, i = [], 0
    colors = [PAL[k] for k in ("pink", "lilac", "blue", "mint", "yellow", "peach", "rose")]
    parts = art.split('fill="#fff"')
    for k, p in enumerate(parts[:-1]):
        out.append(p)
        out.append(f'fill="{colors[rnd.randrange(len(colors))]}"')
    out.append(parts[-1])
    return "".join(out)


def tint(art, color):
    return art.replace('fill="#fff"', f'fill="{color}"')


UNI_COLORS = dict(body=PAL["cream"], hair=[PAL[k] for k in ("pink", "lilac", "blue", "mint", "yellow", "peach")],
                  horn=PAL["yellow"], hoof=PAL["lilac"], wing=PAL["blue"])


def colour_unicorn(**kw):
    from unicorn2 import colored
    with colored(**UNI_COLORS):
        art = unicorn(**kw)
    # accessories (roses, crown...) are still white: tint what is left
    return art.replace('fill="#fff"', f'fill="{PAL["rose"]}"')


def colour_flowers(y0, seed):
    rnd = random.Random(seed)
    cols = [PAL[k] for k in ("rose", "pink", "lilac", "yellow", "peach", "blue")]
    out = []
    for i in range(10):
        x = 60 + i * 80 + rnd.uniform(-10, 10)
        out.append(tint(tall_grass(x, y0 + 90, rnd.uniform(70, 110), 4, i), "#7fd36b"))
    for i in range(9):
        x = 80 + i * 86 + rnd.uniform(-15, 15)
        y = y0 + rnd.uniform(0, 40)
        k = i % 3
        art = (tulip(x, y + 90, rnd.uniform(90, 120)) if k == 0 else
               stem_flower(x, y + 90, rnd.uniform(60, 90), 30, "daisy") if k == 1 else
               stem_flower(x, y + 90, rnd.uniform(50, 80), 28, "blossom"))
        out.append(tint(art, cols[i % len(cols)]))
    for i in range(6):
        out.append(tint(rose(100 + i * 130 + rnd.uniform(-20, 20), y0 + 110 + rnd.uniform(-10, 20), rnd.uniform(30, 38)),
                        cols[(i * 2) % len(cols)]))
    return "".join(out)


def cover_front():
    rb = rainbow(425, 820, 390)
    bands = [PAL[k] for k in ("rose", "peach", "yellow", "mint", "blue", "lilac")]
    parts = rb.split('fill="#fff"')
    rb_c = "".join(p + (f'fill="{bands[i % 6]}"' if i < len(parts) - 1 else "") for i, p in enumerate(parts))
    sp = Space()
    stars = []
    rnd = random.Random(9)
    for x, y in [(90, 330), (760, 330), (190, 420), (660, 440), (120, 560), (740, 590), (420, 300)]:
        stars.append(star(x, y, rnd.uniform(14, 22), PAL["yellow"], w=DW + .6) if rnd.random() < .6
                     else heart(x, y, 14, PAL["rose"], w=DW + .6))
    body = [f'<rect x="-20" y="-20" width="{PW + 40}" height="{PH + 40}" fill="{PAL["sky"]}"/>', rb_c,
            tint(cloud(110, 800, 1.6), "#ffffff"), tint(cloud(745, 800, 1.6), "#ffffff"),
            fill_path("M-20,880 C200,830 360,910 520,880 S760,835 870,880 L870,1200 L-20,1200 Z", OW, PAL["grass"]),
            "".join(stars),
            tint(butterfly(705, 480, .55, 18), PAL["lilac"]), tint(butterfly(145, 470, .5, -15), PAL["peach"]),
            g(colour_unicorn(pose="prance", accessory="roses"), 400, 700, .9),
            colour_flowers(880, 2),
            fill_path("M50,40 Q425,0 800,40 L780,260 Q425,225 70,260 Z", 8, "#fff"),
            text(425, 125, "MON SUPER", 62, fill=PAL["purple"], stroke_w=5),
            text(425, 212, "COLORIAGE LICORNE", 56, fill=PAL["rose"], stroke_w=5),
            f'<rect x="130" y="995" width="590" height="62" rx="31" fill="#fff" stroke="{INK}" stroke-width="5"/>',
            text(425, 1037, SUBTITLE, 30, fill=PAL["purple"])]
    return "".join(body)


def cover(n_pages):
    bleed = 12.5
    spine = n_pages * PAPER * 100
    W, H = bleed * 2 + PW * 2 + spine, PH + bleed * 2
    fx = bleed + PW + spine
    back = [f'<rect x="-20" y="-20" width="{PW + 40}" height="{PH + 40}" fill="{PAL["pink"]}"/>',
            f'<rect x="70" y="80" width="{PW - 140}" height="520" rx="40" fill="#fff" stroke="{INK}" stroke-width="6"/>',
            text(425, 170, "Des heures de magie !", 46, fill=PAL["purple"])]
    for i, line in enumerate(["60 dessins de licornes tous différents",
                              "Châteaux, fées, bonbons, mer, neige...",
                              "Pages imprimées d'un seul côté",
                              "Grand format 21,6 x 27,9 cm",
                              "Idéal pour les filles de 4 à 8 ans",
                              "Un super cadeau d'anniversaire !"]):
        back.append(heart(125, 242 + i * 58, 12, PAL["rose"], w=3))
        back.append(text(150, 252 + i * 58, line, 28, "normal", "start"))
    back.append(g(colour_unicorn(pose="stand", wings="fairy", accessory="crown"), 300, 860, .6))
    # bottom-right stays empty for the KDP barcode
    spine_txt = ""
    if spine > 40:
        spine_txt = (f'<text transform="translate({bleed + PW + spine / 2 + 7} {H / 2}) rotate(90)" font-family="{FONT}" '
                     f'font-weight="bold" font-size="20" fill="#fff" text-anchor="middle">{esc(TITLE.upper())}</text>')
    body = (f'<rect width="{W}" height="{H}" fill="{PAL["pink"]}"/>'
            f'<g transform="translate({bleed} {bleed})">{"".join(back)}</g>'
            f'<rect x="{bleed + PW}" y="0" width="{spine}" height="{H}" fill="{PAL["purple"]}"/>{spine_txt}'
            f'<rect x="{fx}" y="0" width="{PW + bleed}" height="{H}" fill="{PAL["sky"]}"/>'
            f'<g transform="translate({fx} {bleed})">{cover_front()}</g>')
    return svg(body, W, H), W / 100, H / 100, spine / 100


# ---------------------------------------------------------------- main
def sheet(pages, path, cols=6, w=300):
    from PIL import Image
    ims = [Image.open(io.BytesIO(cairosvg.svg2png(bytestring=p.encode(), output_width=w))) for p in pages]
    h = ims[0].height
    rows = (len(ims) + cols - 1) // cols
    im = Image.new("RGB", (cols * (w + 8), rows * (h + 8)), "#999")
    for i, x in enumerate(ims):
        im.paste(x, ((i % cols) * (w + 8), (i // cols) * (h + 8)))
    im.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    designs = design_pages()
    if len(sys.argv) > 1 and sys.argv[1] == "sheet":
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        sheet([p for p, _ in designs[start:start + 12]], os.path.join(OUT, f"sheet-{start:02d}.png"))
        return
    interior = [belongs_page(), test_colors_page()]
    for p, _ in designs:
        interior += [p, blank()]
    interior += [thanks_page(), blank()]
    to_pdf(interior, os.path.join(OUT, "interieur-KDP.pdf"))
    # a version without blank pages (for printing at home / Etsy / Canva)
    to_pdf([belongs_page(), test_colors_page()] + [p for p, _ in designs] + [thanks_page()],
           os.path.join(OUT, "livre-sans-pages-blanches.pdf"))
    cov, w, h, sp = cover(len(interior))
    to_pdf([cov], os.path.join(OUT, "couverture-KDP.pdf"))
    front = svg(cover_front())
    cairosvg.svg2png(bytestring=front.encode(), write_to=os.path.join(OUT, "couverture-avant.png"), output_width=1700)
    for i in (0, 2, 3, 6, 10, 13):
        cairosvg.svg2png(bytestring=designs[i][0].encode(), write_to=os.path.join(OUT, f"apercu-{i + 1:02d}.png"),
                         output_width=1275)
    print(f"interior: {len(interior)} pages, {len(designs)} designs; cover {w:.3f} x {h:.3f} in, spine {sp:.3f} in")


if __name__ == "__main__":
    main()
