"""Build the print-ready unicorn coloring book.

    python3 generate.py

Outputs (in ./output):
  interior.pdf   - 8.5 x 11 in interior, single-sided designs, no bleed
  cover.pdf      - full wrap-around paperback cover with bleed (KDP spec)
  cover-front.png, preview-*.png - images for your listing / mock-ups
"""
import io
import math
import os
import random

import cairosvg
from pypdf import PdfReader, PdfWriter

import art
from art import (INK, balloon, butterfly, castle, circle, cloud, cupcake, flower, g, gem,
                 grass_tuft, heart, hills, line, moon, mushroom_house, rainbow, shape,
                 sparkle, star, sun, tree, tulip, unicorn)

# ---------------------------------------------------------------- settings
BOOK_TITLE = "Unicorn Coloring Book"
BOOK_SUBTITLE = "For Kids Ages 4-8"
AUTHOR = "Rainbow Pencil Press"      # <- put your own author / brand name here
N_DESIGNS = 40
PAPER_THICKNESS = 0.002252           # inches per page, KDP white paper
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

PW, PH = 850, 1100                   # page in 1/100 inch

# palette used for the coloured cover and colour previews
PAL = dict(pink="#ff8fc7", purple="#b58cff", blue="#7cc8ff", mint="#7ee0b5",
           yellow="#ffe066", orange="#ffb35c", red="#ff6b7a", sky="#d9f1ff",
           grass="#a6e36b", cream="#fff7fb", brown="#c98b5a")
RAINBOW = [PAL["red"], PAL["orange"], PAL["yellow"], PAL["mint"], PAL["blue"], PAL["purple"]]


class Colors:
    """Returns white for everything in line-art mode, real colours for the cover."""

    def __init__(self, on):
        self.on = on

    def __call__(self, name):
        return PAL[name] if self.on else "#fff"

    def list(self, names):
        return [self(n) for n in names]


# ---------------------------------------------------------------- layout
class Space:
    """Very small collision helper so decorations don't overlap each other."""

    def __init__(self):
        self.taken = []

    def block(self, x, y, r):
        self.taken.append((x, y, r))

    def free(self, x, y, r):
        return all(math.hypot(x - a, y - b) > r + c for a, b, c in self.taken)

    def place(self, rnd, box, r, tries=200):
        x0, y0, x1, y1 = box
        for _ in range(tries):
            x, y = rnd.uniform(x0 + r, x1 - r), rnd.uniform(y0 + r, y1 - r)
            if self.free(x, y, r):
                self.block(x, y, r)
                return x, y
        return None


def block_unicorn(space, x, y, s, flip, pose="stand", wings=False):
    d = -1 if flip else 1
    parts = [(0, 0, 125), (120, -165, 100), (80, -80, 70), (150, -300, 40), (-160, 40, 80),
             (60, -240, 60)]
    parts += [(0, 110, 90), (-80, 120, 50), (80, 120, 50)] if pose == "stand" else [(40, 80, 90)]
    if wings:
        parts += [(-90, -120, 80)]
    for px, py, r in parts:
        space.block(x + d * px * s, y + py * s, r * s)


def scatter(space, rnd, box, n, r, draw):
    out = []
    for _ in range(n):
        p = space.place(rnd, box, r)
        if p:
            out.append(draw(*p))
    return "".join(out)


def ground_line(y):
    return line(f"M40,{y} Q220,{y - 18} 425,{y} T810,{y}", art.W)


# ---------------------------------------------------------------- scenes
def unicorn_kw(spec, C):
    return dict(eyes=spec.get("eyes", "open"), wings=spec.get("wings", False),
                mark=spec.get("mark", "star"), bow=spec.get("bow", False),
                crown=spec.get("crown", False), pose=spec.get("pose", "stand"),
                body=C("cream"), horn=C("yellow"), hoof=C("purple"), wing_fill=C("blue"),
                accent=C("pink"),
                mane_fills=C.list(["pink", "purple", "blue", "mint", "yellow", "orange"]))


def scene(spec, colored=False):
    C = Colors(colored)
    rnd = random.Random(spec["seed"])
    sp = Space()
    kind = spec["kind"]
    flip = spec.get("flip", False)
    ux, uy, us = spec.get("pos", (425, 640, 1.3))
    pose = spec.get("pose", "stand")
    back, front = [], []
    ground = 900

    # sky / background -------------------------------------------------
    if kind == "rainbow":
        back.append(rainbow(425, ground - 20, 400, bands=6, bw=34, fills=RAINBOW if colored else None))
        back.append(cloud(115, ground - 45, 1.3, C("sky")) + cloud(735, ground - 45, 1.3, C("sky")))
        sp.block(115, ground - 50, 90); sp.block(735, ground - 50, 90)
    elif kind == "castle":
        back.append(castle(620 if not flip else 230, ground - 5, 1.05, C("purple")))
        back.append(hills(ground - 60, fill=C("grass"), seed=spec["seed"]))
    elif kind == "mushroom":
        back.append(hills(ground - 90, fill=C("grass"), seed=spec["seed"]))
        for x, s in ([(130, .9), (720, 1.05)] if not flip else [(720, .9), (130, 1.05)]):
            back.append(mushroom_house(x, ground + 20, s, C("cream"), C("red")))
            sp.block(x, ground - 100 * s, 110 * s)
    elif kind == "night":
        back.append(moon(700 if not flip else 150, 170, 80, C("yellow")))
        sp.block(700 if not flip else 150, 170, 100)
        back.append(scatter(sp, rnd, (40, 40, 810, 480), 14, 30,
                            lambda x, y: star(x, y, rnd.uniform(16, 28), C("yellow"), rot=rnd.uniform(-110, -70))))
    elif kind == "sky":
        back.append(rainbow(ux, uy + 330, 360, bands=6, bw=30, fills=RAINBOW if colored else None))
        for x, y, s in [(140, 900, 1.5), (430, 960, 1.9), (720, 900, 1.5), (150, 200, 1.0), (700, 150, 0.9)]:
            back.append(cloud(x, y, s, C("sky")))
            sp.block(x, y, 110 * s)
    elif kind == "party":
        for x, y, n in [(110, 200, "pink"), (200, 150, "blue"), (660, 170, "yellow"), (750, 230, "mint")]:
            back.append(balloon(x, y, 55, C(n)))
            sp.block(x, y + 60, 90)
    elif kind == "sunny":
        back.append(sun(150 if not flip else 700, 170, 70, C("yellow")))
        sp.block(150 if not flip else 700, 170, 120)
        back.append(hills(ground - 70, fill=C("grass"), seed=spec["seed"]))
        for x in ([640, 760] if not flip else [90, 210]):
            back.append(tree(x, ground - 30, 1.0, C("mint")))
            sp.block(x, ground - 120, 80)
    elif kind == "garden":
        back.append(hills(ground - 40, fill=C("grass"), seed=spec["seed"]))
    elif kind == "family":
        back.append(rainbow(425, ground - 60, 330, bands=5, bw=28, fills=RAINBOW if colored else None))
        back.append(hills(ground - 50, fill=C("grass"), seed=spec["seed"]))

    if kind == "portrait":
        return portrait(spec, C, rnd)

    # the star(s) of the page --------------------------------------------
    kw = unicorn_kw(spec, C)
    main = g(unicorn(**kw), ux, uy, us, flip=flip, rot=spec.get("rot", 0))
    block_unicorn(sp, ux, uy, us, flip, pose, kw["wings"])
    if kind == "family":
        bx = ux + (-270 if not flip else 270)
        by = uy + 115
        bkw = dict(kw, wings=False, crown=False, bow=True, mark="heart", eyes="open", pose="stand")
        main += g(unicorn(**bkw), bx, by, us * .55, flip=not flip if spec.get("face_mom", True) else flip)
        block_unicorn(sp, bx, by, us * .55, flip, "stand")
    if kind == "night" and pose == "lie":
        back.append(cloud(ux, uy + 150, 3.2, C("sky")))

    # sky decorations ---------------------------------------------------------
    top = (40, 40, 810, 520)
    if kind in ("rainbow", "castle", "garden", "mushroom", "family"):
        back.insert(0, scatter(sp, rnd, top, 3, 70, lambda x, y: cloud(x, y, .8, C("sky"))))
    deco = spec.get("deco", "stars")
    fillers = {
        "stars": lambda x, y: star(x, y, rnd.uniform(18, 30), C("yellow"), rot=rnd.uniform(-110, -70)),
        "hearts": lambda x, y: heart(x, y, rnd.uniform(18, 28), C("pink")),
        "sparkles": lambda x, y: sparkle(x, y, rnd.uniform(18, 28), C("yellow")),
        "butterflies": lambda x, y: butterfly(x, y, rnd.uniform(.8, 1.1), C("blue")),
        "gems": lambda x, y: gem(x, y, rnd.uniform(.9, 1.2), C("blue")),
    }
    mix = [fillers[d] for d in deco.split("+")]
    front.append(scatter(sp, rnd, top, spec.get("n_deco", 8), 32,
                         lambda x, y: rnd.choice(mix)(x, y)))

    # ground -----------------------------------------------------------------------------
    if kind in ("rainbow", "party", "garden", "night") and pose != "lie":
        front.insert(0, ground_line(ground + 10))
    if kind != "sky" and not (kind == "night" and pose == "lie"):
        gbox = (40, ground - 30, 810, 1050)
        items = {
            "garden": lambda x, y: rnd.choice([lambda: tulip(x, y + 40, 90, C("red")),
                                               lambda: flower(x, y, 30, fill=C("pink"), center=C("yellow"))])(),
            "party": lambda x, y: rnd.choice([lambda: cupcake(x, y + 45, 1.0, C("pink")),
                                              lambda: gem(x, y, 1.1, C("blue")),
                                              lambda: heart(x, y, 26, C("red"))])(),
        }.get(kind, lambda x, y: rnd.choice([lambda: flower(x, y, 28, fill=C("pink"), center=C("yellow")),
                                             lambda: grass_tuft(x, y + 20, 1.3),
                                             lambda: tulip(x, y + 40, 80, C("red"))])())
        front.append(scatter(sp, rnd, gbox, spec.get("n_ground", 7), 45, items))
        if kind == "garden":
            front.append(scatter(sp, rnd, (40, 300, 810, 800), 3, 45,
                                 lambda x, y: butterfly(x, y, 1.1, C("blue"))))
    return "\n".join(back) + "\n" + main + "\n" + "\n".join(front)


def portrait(spec, C, rnd):
    """Big close-up of the head inside a rounded frame, with a starry border."""
    flip = spec.get("flip", False)
    kw = unicorn_kw(spec, C)
    kw.update(crown=True, wings=False)
    s = 2.35
    hx = 470 if not flip else 380
    ux = hx - (130 * s if not flip else -130 * s)
    uy = 520 + 175 * s
    sp = Space()
    inner = (f'<rect x="90" y="90" width="670" height="920" rx="60" fill="{C("sky")}"/>' +
             scatter(sp_block(sp, hx, 520, 330), rnd, (100, 100, 750, 1000), 6, 34,
                     lambda x, y: rnd.choice([heart, lambda a, b, r, fl: star(a, b, r, fl)])(x, y, 24, C("pink"))) +
             g(unicorn(**kw), ux, uy, s, flip=flip))
    out = ['<defs><clipPath id="pf"><rect x="90" y="90" width="670" height="920" rx="60"/></clipPath></defs>',
           f'<g clip-path="url(#pf)">{inner}</g>',
           f'<rect x="90" y="90" width="670" height="920" rx="60" fill="none" stroke="{INK}" stroke-width="{art.W * 1.5}"/>']
    per = [(90 + i * 670 / 7, 90) for i in range(8)] + [(90 + i * 670 / 7, 1010) for i in range(8)]
    per += [(90, 90 + i * 920 / 9) for i in range(1, 9)] + [(760, 90 + i * 920 / 9) for i in range(1, 9)]
    for i, (x, y) in enumerate(per):
        out.append(star(x, y, 26, C("yellow")) if i % 2 == 0 else heart(x, y, 20, C("pink")))
    return "".join(out)


def sp_block(sp, x, y, r):
    sp.block(x, y, r)
    return sp


# 40 design specs: every page gets a different combination.
KINDS = ["rainbow", "castle", "mushroom", "night", "sky", "party", "sunny", "garden", "family", "portrait"]


def design_specs(n=N_DESIGNS):
    rnd = random.Random(2026)
    specs = []
    decos = ["stars", "hearts", "sparkles", "stars+hearts", "sparkles+stars", "hearts+sparkles",
             "butterflies+hearts", "gems+sparkles"]
    marks = ["star", "heart", "moon", "rainbow"]
    for i in range(n):
        kind = KINDS[i % len(KINDS)]
        spec = dict(seed=1000 + i, kind=kind, flip=(i // len(KINDS)) % 2 == 1,
                    eyes=["open", "closed", "wink", "open"][(i * 3) % 4],
                    mark=marks[i % 4], deco=decos[(i * 5) % len(decos)],
                    bow=(i % 3 == 0), crown=(i % 4 == 1),
                    wings=(i % 5 in (2, 4)))
        if kind == "sky":
            spec.update(wings=True, pos=(425, 560, 1.3), rot=-8, n_deco=7)
        if kind == "night":
            spec.update(eyes="closed" if i % 2 else "open", pose="lie" if (i // len(KINDS)) % 2 == 0 else "stand",
                        deco="sparkles", n_deco=4)
            if spec["pose"] == "lie":
                spec["pos"] = (425, 640, 1.35)
        if kind == "mushroom" and (i // len(KINDS)) % 2 == 1:
            spec.update(pose="lie", pos=(425, 760, 1.25))
        if kind == "family":
            spec.update(pos=(520 if not spec["flip"] else 330, 600, 1.1), crown=True)
        if kind == "castle":
            spec.update(pos=(330 if not spec["flip"] else 520, 640, 1.2), crown=True)
        specs.append(spec)
    return specs


# ---------------------------------------------------------------- pages
def svg_page(body, w=PW, h=PH, bg="#fff"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / 100}in" height="{h / 100}in" '
            f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


FONT = "DejaVu Sans"


def text(x, y, s, size, weight="bold", fill=INK, anchor="middle", stroke=None, sw=0, family=FONT):
    st = f' stroke="{stroke}" stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round"' if stroke else ""
    s = s.replace("&", "&amp;")
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{st}>{s}</text>')


def belongs_page():
    body = [g(unicorn(eyes="closed", crown=True, pose="lie"), 410, 620, 1.15),
            text(425, 150, "This Book Belongs To", 50),
            line("M170,860 H680", 5),
            star(80, 135, 26) + star(770, 135, 26) + heart(120, 820, 26) + heart(730, 820, 26),
            text(425, 960, f"{BOOK_TITLE} - {BOOK_SUBTITLE}", 24, weight="normal"),
            text(425, 995, f"(c) {AUTHOR}. All rights reserved.", 18, weight="normal")]
    return svg_page("".join(body))


def colors_page():
    """'Test your colours' page, printed on the back of the first sheet."""
    body = [text(425, 150, "Test Your Colors Here!", 48)]
    for r in range(6):
        for c in range(5):
            x, y = 120 + c * 130, 240 + r * 125
            body.append(shape(art.circle(x + 40, y + 40, 45), width=4) if (r + c) % 2 else
                        shape(art.path(art.heart_path(x + 40, y + 45, 42)), width=4))
    body.append(text(425, 1010, "Try your crayons, pencils and markers before you start.", 22, weight="normal"))
    return svg_page("".join(body))


def thanks_page():
    body = [text(425, 250, "Well Done, Artist!", 60),
            g(unicorn(eyes="wink", wings=True, bow=True, mark="heart"), 440, 620, 1.1),
            text(425, 930, "We hope you had fun coloring these unicorns.", 26, weight="normal"),
            text(425, 975, "Grown-ups: if you enjoyed this book, a review helps us a lot!", 22, weight="normal")]
    body.append(star(130, 250, 30) + star(720, 250, 30) + sparkle(200, 380, 24) + sparkle(680, 400, 24))
    return svg_page("".join(body))


def blank_page():
    return svg_page("")


def to_pdf(svgs, path):
    w = PdfWriter()
    for s in svgs:
        w.append(PdfReader(io.BytesIO(cairosvg.svg2pdf(bytestring=s.encode()))))
    with open(path, "wb") as fh:
        w.write(fh)


def interior_pages():
    pages = [belongs_page(), colors_page()]
    for spec in design_specs():
        pages += [svg_page(scene(spec)), blank_page()]   # single-sided: blank back
    pages += [thanks_page(), blank_page()]
    return pages


# ---------------------------------------------------------------- cover
def cover_svg(n_pages):
    bleed = 12.5
    spine = n_pages * PAPER_THICKNESS * 100
    W = bleed * 2 + PW * 2 + spine
    H = PH + bleed * 2
    fx = bleed + PW + spine          # left edge of front cover
    C = Colors(True)

    # front cover art
    spec = dict(seed=7, kind="rainbow", eyes="closed", crown=True, bow=False, mark="star",
                deco="stars+hearts", n_deco=6, n_ground=0, pos=(425, 480, 1.12))
    art_svg = scene(spec, colored=True)
    front = [f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="{PAL["sky"]}"/>',
             f'<g transform="translate(0 30)">{art_svg}</g>',
             f'<path d="M-10,930 Q200,880 425,915 T860,900 L860,1110 L-10,1110 Z" fill="{PAL["grass"]}" stroke="{INK}" stroke-width="6"/>',
             # title banner
             f'<path d="M60,760 Q425,700 790,760 L770,1000 Q425,950 80,1000 Z" fill="#fff" stroke="{INK}" stroke-width="8"/>',
             text(425, 845, "UNICORN", 110, fill=PAL["purple"], stroke=INK, sw=6),
             text(425, 918, "COLORING BOOK", 66, fill=PAL["pink"], stroke=INK, sw=5),
             text(425, 968, BOOK_SUBTITLE, 38, fill="#3b6fd4"),
             f'<rect x="110" y="1028" width="630" height="46" rx="23" fill="#fff" stroke="{INK}" stroke-width="4"/>',
             text(425, 1060, f"{N_DESIGNS} cute designs  -  single-sided pages  -  8.5 x 11 in", 24,
                  fill=INK, weight="normal")]

    back = [f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="{PAL["pink"]}"/>',
            f'<rect x="60" y="80" width="{PW - 120}" height="560" rx="40" fill="#fff" stroke="{INK}" stroke-width="6"/>',
            text(425, 170, "Hours of Magical Fun!", 50, fill=PAL["purple"]),
            text(110, 250, f"- {N_DESIGNS} adorable unicorn designs", 27, anchor="start", weight="normal"),
            text(110, 305, "- Rainbows, castles, stars & mushroom houses", 27, anchor="start", weight="normal"),
            text(110, 360, "- Single-sided pages: no bleed-through", 27, anchor="start", weight="normal"),
            text(110, 415, "- Big, bold lines for little hands", 27, anchor="start", weight="normal"),
            text(110, 470, "- Large 8.5 x 11 inch format", 27, anchor="start", weight="normal"),
            text(110, 525, "- Perfect gift for ages 4 to 8", 27, anchor="start", weight="normal"),
            g(unicorn(eyes="wink", wings=True, mark="heart", **{k: v for k, v in unicorn_kw({}, C).items()
                                                                if k not in ("eyes", "wings", "mark")}),
              300, 870, 0.75),
            ]  # lower-right corner stays empty: KDP prints the barcode there (2 x 1.2 in)
    for x, y in [(90, 700), (520, 720), (760, 690), (560, 820)]:
        back.append(star(x, y, 26, PAL["yellow"]))

    spine_svg = f'<rect x="{bleed + PW}" y="0" width="{spine}" height="{H}" fill="{PAL["purple"]}"/>'
    body = (f'<g transform="translate({bleed} {bleed})">{"".join(back)}</g>'
            f'<rect x="0" y="0" width="{bleed + PW}" height="{bleed}" fill="{PAL["pink"]}"/>'
            f'<rect x="0" y="0" width="{bleed}" height="{H}" fill="{PAL["pink"]}"/>'
            f'<rect x="0" y="{H - bleed}" width="{bleed + PW}" height="{bleed}" fill="{PAL["pink"]}"/>'
            f'<rect x="{fx}" y="0" width="{PW + bleed}" height="{H}" fill="{PAL["sky"]}"/>'
            f'<g transform="translate({fx} {bleed})">{"".join(front)}</g>'
            + spine_svg)
    front_only = svg_page("".join(front), bg=PAL["sky"])
    return svg_page(body, W, H), front_only, W / 100, H / 100, spine / 100


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = interior_pages()
    to_pdf(pages, os.path.join(OUT, "interior.pdf"))
    cover, front, w, h, spine = cover_svg(len(pages))
    to_pdf([cover], os.path.join(OUT, "cover.pdf"))
    cairosvg.svg2png(bytestring=front.encode(), write_to=os.path.join(OUT, "cover-front.png"), output_width=1700)
    specs = design_specs()
    for i in (0, 1, 3, 4, 7, 8):
        cairosvg.svg2png(bytestring=svg_page(scene(specs[i])).encode(),
                         write_to=os.path.join(OUT, f"preview-{i + 1:02d}.png"), output_width=850)
    print(f"interior: {len(pages)} pages, {N_DESIGNS} designs")
    print(f"cover: {w:.3f} x {h:.3f} in (spine {spine:.3f} in)")


if __name__ == "__main__":
    main()
