"""Five sample pages, one per drawing style, so a style can be chosen for the book.

    python3 samples.py      -> ../output/styles/style-A.png ... style-E.png + styles.pdf
"""
import io
import os
import random

import cairosvg
from pypdf import PdfReader, PdfWriter

from art2 import *
from kawaii import unicorn_front

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "styles")
PW, PH = 850, 1100


def page(body, label=None):
    lab = ""
    if label:
        lab = (f'<text x="425" y="1075" font-family="DejaVu Sans" font-size="20" fill="#888" '
               f'text-anchor="middle">{label}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 {PW} {PH}">'
            f'<rect width="{PW}" height="{PH}" fill="#fff"/>{body}{lab}</svg>')


# ---------------------------------------------------------------- extra scenery
def castle(x, y, s=1.0, w=6):
    out = []

    def tower(cx, top, tw, h, roof=1.4):
        b = fill_path(f"M{f(cx - tw / 2)},{f(top)} h{f(tw)} v{f(h)} h{f(-tw)} Z", w)
        r = fill_path(f"M{f(cx - tw / 2 - 12 * s)},{f(top)} Q{f(cx)},{f(top - tw * .3)} {f(cx)},{f(top - tw * roof)} "
                      f"Q{f(cx)},{f(top - tw * .3)} {f(cx + tw / 2 + 12 * s)},{f(top)} Z", w)
        fl = (stroke(f"M{f(cx)},{f(top - tw * roof)} v{f(-30 * s)}", 4) +
              fill_path(f"M{f(cx)},{f(top - tw * roof - 30 * s)} q{f(18 * s)},{f(-6 * s)} {f(30 * s)},{f(6 * s)} "
                        f"q{f(-12 * s)},{f(8 * s)} {f(-30 * s)},{f(10 * s)} Z", 4))
        win = fill_path(f"M{f(cx - 10 * s)},{f(top + 60 * s)} v{f(-18 * s)} a{f(10 * s)},{f(10 * s)} 0 0 1 {f(20 * s)},0 "
                        f"v{f(18 * s)} Z", 4)
        return fl + b + r + win

    out.append(fill_path(f"M{f(x - 130 * s)},{f(y - 160 * s)} h{f(260 * s)} V{f(y)} H{f(x - 130 * s)} Z", w))
    for i in range(7):
        out.append(fill_path(f"M{f(x - 130 * s + i * 40 * s)},{f(y - 160 * s)} v{f(-22 * s)} h{f(24 * s)} v{f(22 * s)} Z", 5))
    out.append(tower(x - 150 * s, y - 250 * s, 70 * s, 250 * s))
    out.append(tower(x + 150 * s, y - 250 * s, 70 * s, 250 * s))
    out.append(tower(x, y - 320 * s, 84 * s, 160 * s, 1.5))
    out.append(fill_path(f"M{f(x - 40 * s)},{f(y)} v{f(-70 * s)} a{f(40 * s)},{f(40 * s)} 0 0 1 {f(80 * s)},0 v{f(70 * s)} Z", 5))
    out.append(stroke(f"M{f(x)},{f(y)} v{f(-108 * s)}", 4))
    for dx, dy in [(-90, -120), (-35, -125), (35, -125), (90, -120)]:
        out.append(heart(x + dx * s, y + dy * s, 12 * s, w=4))
    return "".join(out)


def balloon(x, y, r, w=5):
    return (stroke(f"M{f(x)},{f(y + r + 12)} q-20,45 0,90 q18,40 -6,90", 3)
            + fill_path(f"M{f(x)},{f(y + r)} C{f(x - r * 1.25)},{f(y + r * .55)} {f(x - r)},{f(y - r)} {f(x)},{f(y - r)} "
                        f"C{f(x + r)},{f(y - r)} {f(x + r * 1.25)},{f(y + r * .55)} {f(x)},{f(y + r)} Z", w)
            + fill_path(f"M{f(x - 9)},{f(y + r + 12)} L{f(x)},{f(y + r - 2)} L{f(x + 9)},{f(y + r + 12)} Z", 4)
            + stroke(f"M{f(x - r * .5)},{f(y - r * .2)} q{f(r * .05)},{f(-r * .4)} {f(r * .4)},{f(-r * .55)}", 4))


def ice_cream(x, y, s=1.0):
    cone = fill_path(f"M{f(x - 38 * s)},{f(y - 90 * s)} L{f(x)},{f(y)} L{f(x + 38 * s)},{f(y - 90 * s)} Z", 5)
    grid = stroke(f"M{f(x - 26 * s)},{f(y - 90 * s)} L{f(x + 12 * s)},{f(y - 30 * s)} M{f(x)},{f(y - 90 * s)} "
                  f"L{f(x + 24 * s)},{f(y - 60 * s)} M{f(x + 26 * s)},{f(y - 90 * s)} L{f(x - 12 * s)},{f(y - 30 * s)} "
                  f"M{f(x)},{f(y - 90 * s)} L{f(x - 24 * s)},{f(y - 60 * s)}", 3)
    sc1 = union([ell_d(x, y - 115 * s, 44 * s, 36 * s)], 5)
    drip = fill_path(f"M{f(x - 46 * s)},{f(y - 100 * s)} q{f(10 * s)},{f(22 * s)} {f(20 * s)},0 q{f(10 * s)},{f(28 * s)} "
                     f"{f(22 * s)},0 q{f(12 * s)},{f(18 * s)} {f(24 * s)},0 q{f(10 * s)},{f(22 * s)} {f(22 * s)},0 Z", 5)
    sc2 = circ(x, y - 165 * s, 34 * s, 5)
    cherry = circ(x + 5 * s, y - 205 * s, 12 * s, 4) + stroke(f"M{f(x + 8 * s)},{f(y - 216 * s)} q4,-14 16,-18", 3)
    return cone + grid + sc2 + sc1 + drip + cherry


def lollipop(x, y, r):
    return (fill_path(f"M{f(x - 6)},{f(y)} h12 v{f(r * 3)} h-12 Z", 4) + circ(x, y, r, 5)
            + swirl(x, y, r * .85, turns=2.2, w=4))


def donut(x, y, r):
    return (circ(x, y, r, 5) + fill_path(
        f"M{f(x - r * .9)},{f(y)} C{f(x - r * .9)},{f(y - r * 1.1)} {f(x + r * .9)},{f(y - r * 1.1)} {f(x + r * .9)},{f(y)} "
        f"q{f(-r * .15)},{f(r * .3)} {f(-r * .3)},{f(r * .1)} q{f(-r * .3)},{f(r * .45)} {f(-r * .6)},{f(r * .2)} "
        f"q{f(-r * .3)},{f(r * .4)} {f(-r * .6)},0 q{f(-r * .2)},{f(r * .2)} {f(-r * .3)},{f(-r * .2)} Z", 4)
            + circ(x, y - r * .1, r * .28, 5)
            + "".join(stroke(f"M{f(x + dx * r)},{f(y + dy * r)} l{f(r * .12)},{f(-r * .08)}", 4)
                      for dx, dy in [(-.55, -.35), (-.2, -.62), (.3, -.55), (.55, -.2), (-.6, .05)]))


def mushroom(x, y, s=1.0):
    stem = fill_path(f"M{f(x - 50 * s)},{f(y)} Q{f(x - 58 * s)},{f(y - 70 * s)} {f(x - 42 * s)},{f(y - 115 * s)} "
                     f"L{f(x + 42 * s)},{f(y - 115 * s)} Q{f(x + 58 * s)},{f(y - 70 * s)} {f(x + 50 * s)},{f(y)} Z", 6)
    door = fill_path(f"M{f(x - 18 * s)},{f(y)} v{f(-40 * s)} a{f(18 * s)},{f(18 * s)} 0 0 1 {f(36 * s)},0 v{f(40 * s)} Z", 4)
    win = circ(x + 30 * s, y - 78 * s, 12 * s, 4) + stroke(
        f"M{f(x + 18 * s)},{f(y - 78 * s)} h{f(24 * s)} M{f(x + 30 * s)},{f(y - 90 * s)} v{f(24 * s)}", 3)
    cap = fill_path(f"M{f(x - 110 * s)},{f(y - 100 * s)} C{f(x - 115 * s)},{f(y - 215 * s)} {f(x + 115 * s)},{f(y - 215 * s)} "
                    f"{f(x + 110 * s)},{f(y - 100 * s)} Q{f(x)},{f(y - 78 * s)} {f(x - 110 * s)},{f(y - 100 * s)} Z", 6)
    spots = "".join(ell(x + dx * s, y + dy * s, r * s, r * .8 * s, 4)
                    for dx, dy, r in [(-60, -135, 16), (0, -165, 19), (58, -138, 15), (-22, -118, 9), (30, -115, 8)])
    return stem + door + dot(x + 10 * s, y - 20 * s, 3.5 * s) + win + cap + spots


def grass_line(y, x0=30, x1=820):
    return stroke(f"M{x0},{y} Q{(x0 + x1) / 4},{y - 20} {(x0 + x1) / 2},{y} T{x1},{y}", 6)


def tuft(x, y, s=1):
    return stroke(f"M{f(x - 14 * s)},{f(y)} q{f(2 * s)},{f(-14 * s)} {f(-6 * s)},{f(-24 * s)} M{f(x)},{f(y)} "
                  f"q{f(2 * s)},{f(-18 * s)} {f(-2 * s)},{f(-32 * s)} M{f(x + 14 * s)},{f(y)} "
                  f"q{f(0)},{f(-12 * s)} {f(6 * s)},{f(-22 * s)}", 4)


def tulip(x, y, h):
    top = y - h
    return (stroke(f"M{f(x)},{f(y)} Q{f(x - 6)},{f(y - h * .5)} {f(x)},{f(top + 30)}", 4)
            + fill_path(leaf_d(x, y - h * .2, h * .45, -140), 4)
            + fill_path(f"M{f(x - 22)},{f(top)} L{f(x - 11)},{f(top + 12)} L{f(x)},{f(top - 3)} L{f(x + 11)},{f(top + 12)} "
                        f"L{f(x + 22)},{f(top)} Q{f(x + 24)},{f(top + 36)} {f(x)},{f(top + 38)} "
                        f"Q{f(x - 24)},{f(top + 36)} {f(x - 22)},{f(top)} Z", 4))


# ---------------------------------------------------------------- side-view unicorn (style C)
def unicorn_side(fill="#fff"):
    """Cute unicorn in profile, facing right, leaping. Origin = body centre."""
    out = []
    # tail
    for i, p in enumerate([((-105, -25), (-200, -80), (-270, 0), (-235, 80)),
                           ((-110, -5), (-210, 20), (-240, 130), (-175, 160)),
                           ((-105, 10), (-160, 70), (-150, 150), (-100, 170))]):
        out.append(lock(p, 62 - i * 8, 4, fill, 6, True, root=.35))
    # far legs
    out.append(limb("M-70,30 Q-110,80 -170,70", 40) + limb("M-172,70 l-18,-4", 40, fill=fill))
    out.append(limb("M70,30 Q110,70 150,40", 40))
    out.append(wing(-10, -50, .8, -18))
    # body, neck, head
    out.append(union([ell_d(0, 0, 125, 74),
                      "M40,-40 C60,-120 110,-175 165,-190 L225,-130 C185,-100 140,-50 120,20 Z",
                      ell_d(195, -190, 88, 78),
                      ell_d(265, -150, 58, 48)], 6, fill))
    # near legs + hooves
    out.append(limb("M60,40 Q110,110 175,90", 44))
    out.append(fill_path("M170,66 q34,-2 40,26 q-20,20 -40,16 Z", 5))
    out.append(limb("M-60,40 Q-100,110 -200,110", 44))
    out.append(fill_path("M-196,86 q-36,-2 -42,26 q20,20 42,14 Z", 5))
    # ear + horn
    out.append(fill_path("M148,-248 C135,-300 145,-325 162,-338 C185,-312 188,-280 180,-256 Z", 6, fill))
    out.append(stroke("M160,-262 C154,-290 158,-310 164,-320", 3.5))
    out.append(fill_path("M190,-262 Q222,-330 262,-392 Q244,-330 232,-250 Q210,-248 190,-262 Z", 6))
    for t, L in ((.28, 30), (.52, 22), (.74, 14)):
        x0, y0 = 196 + (262 - 196) * t, -258 + (-392 + 258) * t
        out.append(stroke(f"M{f(x0 - 4)},{f(y0)} q{f(L * .6)},{f(-2)} {f(L)},{f(8)}", 4))
    # mane
    mane = [((180, -272), (150, -305), (95, -305), (75, -265)),
            ((170, -266), (110, -285), (55, -250), (25, -165)),
            ((150, -245), (95, -235), (50, -170), (15, -95)),
            ((130, -205), (90, -175), (62, -120), (32, -50))]
    for i, p in enumerate(mane):
        out.append(lock(p, [44, 72, 66, 58][i], 4, fill, 6, i > 0, root=.4))
    out.append(lock(((196, -262), (235, -250), (250, -225), (238, -196)), 42, 4, fill, 5, False, root=.4))
    # face
    out.append(ell(222, -178, 17, 22, 3, INK) + dot(228, -186, 6.5, "#fff") + dot(217, -168, 3, "#fff"))
    out.append(stroke("M232,-198 q10,-6 16,-14 M236,-190 q12,-2 20,-8", 3.5))
    out.append(ell(245, -135, 15, 10, 3))
    out.append(stroke("M300,-160 q6,-5 10,2", 4) + stroke("M270,-118 Q288,-106 304,-122", 4))
    out.append(wing(0, -40, 1.0, -6))
    return "".join(out)


def wing(x, y, s, rot):
    """Feathered wing, root at (0,0), sweeping up and back."""
    top = "M0,0 C-10,-80 -70,-150 -190,-170"
    sc = [(-190, -170), (-178, -120), (-165, -80), (-140, -45), (-100, -18), (-50, 0), (0, 0)]
    d = top
    for (x0, y0), (x1, y1) in zip(sc, sc[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = (y1 - y0), -(x1 - x0)
        d += f" Q{f(mx - nx * .45)},{f(my - ny * .45)} {x1},{y1}"
    art = fill_path(d + " Z", 6)
    inner = [(-150, -130), (-130, -95), (-105, -65), (-70, -40), (-30, -25)]
    for (x0, y0), (x1, y1) in zip(inner, inner[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = (y1 - y0), -(x1 - x0)
        art += stroke(f"M{x0},{y0} Q{f(mx - nx * .45)},{f(my - ny * .45)} {x1},{y1}", 4)
    art += stroke("M-20,-10 C-40,-70 -90,-120 -160,-140", 3.5)
    return g(art, x, y, s, rot=rot)


# ---------------------------------------------------------------- the five pages
def style_a():
    """Simple kawaii: big shapes, few details (ages 3-5)."""
    b = [rainbow(425, 700, 380, 5, 44, w=6),
         cloud(140, 690, 1.6), cloud(710, 690, 1.6),
         cloud(425, 880, 3.0, face=True),
         g(unicorn_front(eyes="open", bow=True, detail=1), 425, 440, 1.0),
         star(110, 150, 42), star(740, 170, 46), heart(700, 380, 34), heart(150, 400, 30),
         sparkle(250, 120, 30), sparkle(600, 110, 26)]
    return page("".join(b), "Style A - kawaii simple - 3-5 ans")


def style_b():
    """Kawaii with a full scene (ages 5-8)."""
    b = [castle(590, 700, 1.0),
         balloon(120, 180, 50), balloon(215, 130, 44), balloon(720, 150, 46),
         cloud(420, 120, .9), sparkle(560, 90, 22), sparkle(330, 230, 18), star(790, 380, 26),
         g(unicorn_front(eyes="closed", crown=True, bow=False), 330, 560, .95),
         grass_line(890)]
    rnd = random.Random(3)
    for x in (70, 180, 560, 650, 760):
        b.append(tulip(x, 1000 - rnd.randint(0, 30), rnd.randint(100, 130)))
    for x, y in [(120, 1010), (250, 960), (420, 1000), (720, 1040), (480, 950)]:
        b.append(daisy(x, y, 30))
    for x, y in [(330, 1040), (600, 1030), (800, 960)]:
        b.append(tuft(x, y, 1.3))
    return page("".join(b), "Style B - kawaii avec decor - 5-8 ans")


def style_c():
    """Graceful flying unicorn in profile, sky scene (ages 6-8)."""
    b = [rainbow(425, 990, 400, 6, 36, w=5),
         cloud(110, 960, 1.9), cloud(740, 960, 1.9), cloud(430, 1010, 2.0),
         g(unicorn_side(), 400, 640, 1.1),
         star(90, 130, 30), star(760, 120, 34), star(640, 260, 22), sparkle(170, 300, 26),
         sparkle(760, 400, 22), star(110, 520, 22), heart(360, 110, 22), sparkle(480, 80, 18),
         cloud(760, 700, .7)]
    return page("".join(b), "Style C - licorne elegante qui vole - 6-8 ans")


def style_d():
    """Very first colouring: one huge head, extra thick lines (ages 3-4)."""
    head = unicorn_front(eyes="open", bow=False, crown=False, detail=1)
    clip = '<defs><clipPath id="c"><rect x="0" y="0" width="850" height="935"/></clipPath></defs>'
    b = [clip, f'<g clip-path="url(#c)">{g(head, 425, 560, 1.75)}</g>',
         stroke("M40,935 H810", 8),
         star(95, 110, 50, w=8), heart(760, 120, 44, w=8), star(430, 1015, 44, w=8),
         heart(180, 1010, 36, w=8), heart(680, 1010, 36, w=8)]
    return page("".join(b), "Style D - mon premier coloriage - 3-4 ans")


def style_e():
    """Candy land: kawaii unicorn with sweets (ages 4-7)."""
    b = [mushroom(130, 900, .9), mushroom(730, 910, 1.05),
         ice_cream(700, 480, .95), lollipop(150, 230, 50), donut(560, 130, 55),
         g(unicorn_front(eyes="open", crown=False, bow=True), 400, 560, .92),
         grass_line(905), heart(300, 110, 26), star(470, 80, 28), sparkle(110, 460, 24), heart(790, 330, 22),
         sparkle(540, 160, 20)]
    for x, y in [(300, 1000), (520, 1010), (420, 960), (80, 1020), (800, 1030)]:
        b.append(flower(x, y, 42, 5))
    for x, y in [(210, 980), (620, 990), (360, 1050)]:
        b.append(tuft(x, y, 1.3))
    return page("".join(b), "Style E - monde des bonbons - 4-7 ans")


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = [("A", style_a()), ("B", style_b()), ("C", style_c()), ("D", style_d()), ("E", style_e())]
    w = PdfWriter()
    for k, svg in pages:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, f"style-{k}.png"), output_width=1275)
        w.append(PdfReader(io.BytesIO(cairosvg.svg2pdf(bytestring=svg.encode()))))
    with open(os.path.join(OUT, "styles.pdf"), "wb") as fh:
        w.write(fh)


if __name__ == "__main__":
    main()
