"""60 themed coloring pages: 12 themes x 5 variants."""
import math
import random

from unicorn2 import girly_module as girly
from scenery import *
from unicorn2 import unicorn

X0, Y0, X1, Y1 = 62, 62, 788, 1000        # inner scene frame


class Space:
    def __init__(self):
        self.c = []

    def block(self, x, y, r):
        self.c.append((x, y, r))

    def place(self, rnd, box, r, tries=150):
        x0, y0, x1, y1 = box
        for _ in range(tries):
            x, y = rnd.uniform(x0 + r, x1 - r), rnd.uniform(y0 + r, y1 - r)
            if all(math.hypot(x - a, y - b) > r + c for a, b, c in self.c):
                self.block(x, y, r)
                return x, y
        return None


def U(sp, x, y, s=1.0, flip=False, rot=0, **kw):
    """Place a full-body unicorn and reserve its space."""
    d = -1 if flip else 1
    parts = [(0, 0, 150), (200, -230, 110), (240, -360, 60), (120, -140, 80), (-200, 60, 110), (0, 150, 90),
             (100, 150, 70), (-100, 150, 70)]
    if kw.get("wings"):
        parts += [(-110, -170, 130)]
    for px, py, r in parts:
        sp.block(x + d * px * s, y + py * s, r * s)
    return g(unicorn(**kw), x, y, s, flip=flip, rot=rot)


def roses_band(rnd):
    """The lush band of roses from the validated sample page (covers the neck)."""
    b = []
    for x, y, L, a in [(230, 945, 90, -150), (330, 960, 80, -100), (610, 950, 90, -30), (700, 960, 80, -70),
                       (470, 970, 70, -90), (130, 990, 70, -120), (780, 990, 70, -60), (60, 1000, 70, -140)]:
        b.append(leaf(x, y, L, a))
    for x, y, r, rot in [(300, 960, 62, 0), (455, 970, 70, 50), (610, 955, 60, 100), (160, 1000, 48, 30),
                         (750, 1000, 50, 80), (380, 1045, 44, 20), (540, 1050, 44, 60)]:
        b.append(rose(x, y, r, rot))
    for x, y, r in [(375, 895, 30), (535, 890, 28), (80, 940, 26), (815, 935, 26), (680, 895, 26), (240, 1050, 26), (660, 1055, 26)]:
        b.append(blossom(x, y, r, rot=rnd.uniform(0, 70)))
    return "".join(b)


def portrait(sp, x=0, y=0, s=1.0, flip=False, seed=11):
    y -= 60
    sp.block(420 + x, 520 + y, 330 * s)
    sp.block(470 + x, 250 + y, 150 * s)
    sp.block(425, 950, 420)
    rnd = random.Random(seed)
    art = girly.unicorn_portrait(rnd)
    art += (blossom(318, 575, 24, rot=10) + blossom(205, 690, 22, rot=40) + blossom(372, 455, 20, rot=70)
            + blossom(262, 470, 18, rot=20))
    band = f'<g transform="translate(0 -50)">{roses_band(rnd)}</g>'
    if flip:
        return f'<g transform="translate({850 - x} {y}) scale({-s} {s})">{art}</g>' + band
    return f'<g transform="translate({x} {y}) scale({s})">{art}</g>' + band


def scatter(sp, rnd, n, box=(X0, Y0, X1, 700), kinds=("star", "sparkle", "heart", "dot"), size=1.0):
    out = []
    for _ in range(n):
        k = rnd.choice(kinds)
        r = {"butterfly": 60, "cloud": 90, "balloon": 60, "snow": 26}.get(k, 18) * size
        p = sp.place(rnd, box, r)
        if not p:
            continue
        x, y = p
        if k == "star":
            out.append(star(x, y, rnd.uniform(11, 17) * size, w=DW + .4, rot=rnd.uniform(-110, -70)))
        elif k == "sparkle":
            out.append(sparkle(x, y, rnd.uniform(11, 18) * size, w=DW + .4))
        elif k == "heart":
            out.append(heart(x, y, rnd.uniform(9, 14) * size, w=DW + .4))
        elif k == "dot":
            out.append(circ(x, y, rnd.uniform(3, 5), DW))
        elif k == "butterfly":
            out.append(butterfly(x, y, rnd.uniform(.38, .5) * size, rnd.uniform(-30, 30), rnd.randint(0, 1)))
        elif k == "cloud":
            out.append(cloud(x, y, rnd.uniform(.7, 1.0) * size))
        elif k == "snow":
            out.append(snowflake(x, y, rnd.uniform(12, 22) * size))
        elif k == "note":
            out.append(fill_path(f"M{f(x)},{f(y)} v-40 l24,-8 v8 l-18,6 v34 Z", DW) + ell(x - 8, y + 2, 11, 8, DW, "#fff", -20))
    return "".join(out)


def ground(y, seed):
    return hills(y, seed)


# ======================================================================= themes
def t_rainbow(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [rainbow(425, 700, 380), cloud(110, 690, 1.5), cloud(740, 690, 1.5), ground(720, v)]
        b.append(U(sp, 400, 650, .95, pose="prance", accessory="roses"))
        b.append(flower_bed(880, 1))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 14))
        cap = "Sous l'arc-en-ciel"
    elif v == 1:
        b += [rainbow(425, 640, 360), cloud(120, 640, 1.4), cloud(730, 640, 1.4), ground(700, 7)]
        b.append(U(sp, 420, 700, 1.0, flip=True, pose="lie", eyes="closed", accessory="flowers"))
        b.append(flower_bed(870, 2))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 14))
        cap = "Une petite sieste"
    elif v == 2:
        b += [rainbow(425, 960, 400), cloud(140, 930, 2.0), cloud(710, 930, 2.0), cloud(430, 990, 2.4)]
        b.append(U(sp, 430, 560, .9, rot=-8, pose="prance", wings="feather", accessory="crown"))
        b.append(scatter(sp, rnd, 3, kinds=("cloud",), box=(X0, Y0, X1, 500)) + scatter(sp, rnd, 16))
        cap = "Je vole dans le ciel"
    elif v == 3:
        b += [rainbow(425, 1000, 360, 6)]
        b.append(portrait(sp, 0, -10, 1.0))
        b.append(scatter(sp, rnd, 2, kinds=("butterfly",)) + scatter(sp, rnd, 14))
        cap = "Belle licorne"
    else:
        b += [rainbow(425, 700, 380), cloud(110, 690, 1.5), cloud(740, 690, 1.5), ground(730, 3)]
        b.append(U(sp, 480, 650, .85, flip=True, pose="stand", accessory="roses"))
        b.append(U(sp, 190, 765, .5, pose="prance", accessory="bow", mark=False))
        b.append(flower_bed(880, 4))
        b.append(scatter(sp, rnd, 2, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Maman et moi"
    return b, cap


def t_castle(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [cloud(150, 180, 1.1), cloud(700, 150, 1.0), castle(560, 700, .95), ground(700, 1)]
        sp.block(560, 450, 230)
        b.append(U(sp, 330, 690, .9, pose="prance", accessory="crown"))
        b.append(flower_bed(880, 5))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Mon beau château"
    elif v == 1:
        b += [cloud(420, 130, 1.2), castle(425, 640, 1.2), ground(650, 2)]
        sp.block(425, 380, 300)
        b.append(U(sp, 450, 760, .75, flip=True, pose="walk", accessory="crown", blanket=True))
        b.append(flower_bed(900, 6, dense=.8))
        b.append(scatter(sp, rnd, 12))
        cap = "La princesse arrive"
    elif v == 2:
        b += [cloud(620, 640, 2.6), castle(620, 610, .7), cloud(160, 900, 1.8), cloud(420, 960, 1.6)]
        sp.block(620, 450, 200)
        b.append(U(sp, 310, 470, .75, rot=-10, pose="prance", wings="feather", accessory="roses"))
        b.append(scatter(sp, rnd, 16, box=(X0, Y0, X1, 950)))
        cap = "Le château dans les nuages"
    elif v == 3:
        b += [castle(640, 470, .55), castle(200, 470, .45)]
        b.append(portrait(sp, 0, 30, .95))
        b.append(scatter(sp, rnd, 12))
        cap = "Princesse licorne"
    else:
        b += [castle(425, 560, .9), ground(560, 8)]
        b.append(fill_path("M330,560 Q300,700 180,1000 L660,1000 Q540,700 510,560 Z", OW - 1))
        sp.block(425, 360, 250)
        for x, y in [(250, 620), (600, 620), (180, 760), (680, 760)]:
            b.append(lantern(x, y, 1.0))
            sp.block(x, y - 40, 60)
        b.append(U(sp, 420, 820, .7, pose="stand", accessory="crown", eyes="closed"))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 10))
        cap = "Le chemin du château"
    return b, cap


def t_birthday(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [bunting(62, 110, 788, 110, 6, 30, "JOYEUX"), bunting(62, 230, 788, 230, 12, 30, "ANNIVERSAIRE")]
        sp.block(425, 200, 190)
        b += [balloon(120, 420, 50), balloon(730, 400, 52, True), ground(820, 3)]
        for x, y in [(120, 480, ), (730, 460)]:
            sp.block(x, y, 110)
        b.append(U(sp, 260, 720, .75, pose="prance", accessory="bow"))
        b.append(flower_bed(900, 3, dense=.8))
        b.append(cake(580, 880, .85))
        sp.block(580, 760, 190)
        sp.block(425, 960, 400)
        b.append(scatter(sp, rnd, 10, box=(X0, 300, X1, 900)))
        cap = "Joyeux anniversaire !"
    elif v == 1:
        for x, y, r, h in [(110, 170, 52, 0), (210, 110, 46, 1), (650, 120, 50, 1), (740, 200, 46, 0), (180, 300, 40, 1)]:
            b.append(balloon(x, y, r, h == 1, 180))
            sp.block(x, y + 60, 90)
        b += [ground(740, 4)]
        b.append(U(sp, 430, 680, .9, flip=True, pose="prance", accessory="crown"))
        for x, w, h in [(130, 90, 70), (230, 70, 55), (700, 100, 80)]:
            b.append(gift(x, 950, w, h))
            sp.block(x, 900, 70)
        b.append(scatter(sp, rnd, 12, box=(X0, Y0, X1, 950)))
        cap = "Plein de ballons"
    elif v == 2:
        b += [bunting(62, 90, 788, 90, 9, 40)]
        b.append(U(sp, 300, 650, .72, pose="stand", accessory="bow", mark=False))
        b += [table(425, 800, 620, 130)]
        b.append(cupcake(150, 800, 1.0) + cake(560, 800, .7) + cupcake(740, 800, .9))
        sp.block(560, 680, 160)
        b.append(balloon(120, 380, 46) + balloon(730, 380, 46, True))
        b.append(scatter(sp, rnd, 10, box=(X0, 150, X1, 600)))
        cap = "Le goûter d'anniversaire"
    elif v == 3:
        b += [ground(760, 5)]
        b.append(U(sp, 420, 700, .95, pose="walk", accessory="flowers", blanket=True))
        b.append(balloon(160, 170, 54, True) + balloon(260, 120, 46) + balloon(640, 150, 52) + balloon(730, 230, 44, True))
        for x in (120, 250, 600, 720):
            sp.block(x, 200, 100)
        for x, w, h in [(140, 110, 90), (300, 70, 60), (560, 80, 60), (700, 110, 90)]:
            b.append(gift(x, 985, w, h))
        b.append(scatter(sp, rnd, 12, box=(X0, Y0, X1, 900)))
        cap = "Des cadeaux pour moi"
    else:
        b += [bunting(62, 100, 788, 100, 7, 30, "BRAVO !"), ground(900, 19)]
        b.append(cake(560, 960, 1.0))
        sp.block(560, 800, 230)
        b.append(U(sp, 260, 720, .66, pose="prance", wings="fairy", accessory="crown"))
        b.append(balloon(110, 330, 46) + balloon(740, 330, 46, True))
        b.append(scatter(sp, rnd, 14, box=(X0, 150, X1, 900), kinds=("star", "sparkle", "heart", "dot")))
        cap = "Souffle les bougies"
    return b, cap


def t_mushroom(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [rainbow(425, 600, 330), cloud(130, 200, 1.1), cloud(700, 160, 1.0), ground(700, 11)]
        b += [mushroom(130, 900, 1.3, False, True, True), mushroom(730, 880, 1.2, False, True, True),
              mushroom(250, 1000, .7), mushroom(630, 1000, .6)]
        for x, y, r in [(130, 700, 160), (730, 690, 150)]:
            sp.block(x, y, r)
        b.append(U(sp, 420, 700, .85, pose="prance", wings="fairy", accessory="flowers"))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "La forêt enchantée"
    elif v == 1:
        b += [ground(640, 12), mushroom(180, 700, 1.5), mushroom(650, 690, 1.3)]
        sp.block(180, 470, 180)
        sp.block(650, 480, 170)
        b.append(U(sp, 420, 830, .8, pose="lie", accessory="roses", eyes="closed"))
        b.append(flower_bed(900, 13, dense=.8))
        b.append(scatter(sp, rnd, 2, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Le village des champignons"
    elif v == 2:
        b += [ground(620, 14), fill_path("M360,620 Q420,760 260,1000 L600,1000 Q470,760 480,620 Z", OW - 1)]
        b += [mushroom(130, 980, 1.2, False), mushroom(740, 980, 1.3, False), mushroom(640, 640, .7), mushroom(220, 650, .6)]
        for x, y, r in [(130, 790, 150), (740, 780, 160), (640, 540, 90), (220, 560, 80)]:
            sp.block(x, y, r)
        b.append(U(sp, 430, 660, .8, flip=True, pose="walk", accessory="bow"))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Promenade dans les bois"
    elif v == 3:
        b.append(portrait(sp, 0, -40, .92, flip=True))
        b += [mushroom(150, 1000, .9, True), mushroom(710, 1000, .8, True)]
        b.append(scatter(sp, rnd, 2, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Licorne des bois"
    else:
        b += [ground(700, 15), mushroom(640, 780, 1.6, True)]
        sp.block(640, 560, 200)
        b.append(U(sp, 300, 740, .75, pose="stand", accessory="flowers"))
        b.append(U(sp, 120, 870, .42, flip=True, pose="prance", accessory="bow", mark=False))
        b.append(flower_bed(900, 16, dense=.7))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Ma maison champignon"
    return b, cap


def t_butterfly(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [ground(740, 21)]
        b.append(U(sp, 400, 680, .95, pose="prance", wings="fairy", accessory="roses"))
        b.append(flower_bed(870, 21))
        b.append(scatter(sp, rnd, 6, kinds=("butterfly",), size=1.3) + scatter(sp, rnd, 10))
        cap = "Des ailes de papillon"
    elif v == 1:
        b.append(butterfly(425, 480, 3.0, 0, 0))
        sp.block(425, 480, 400)
        b.append(U(sp, 425, 860, .45, pose="stand", accessory="bow", mark=False))
        b.append(flower_bed(900, 22, dense=.8))
        b.append(scatter(sp, rnd, 12))
        cap = "Le grand papillon"
    elif v == 2:
        b += [ground(760, 23)]
        b.append(U(sp, 430, 700, .9, flip=True, pose="stand", eyes="closed", accessory="flowers"))
        b.append(butterfly(560, 330, .6, 20, 1))
        b.append(flower_bed(870, 24))
        b.append(scatter(sp, rnd, 5, kinds=("butterfly",), size=1.2) + scatter(sp, rnd, 8))
        cap = "Un papillon sur mon nez"
    elif v == 3:
        b.append(portrait(sp, 0, 0, 1.0))
        b.append(scatter(sp, rnd, 5, kinds=("butterfly",)) + scatter(sp, rnd, 8))
        cap = "Mes amis papillons"
    else:
        b += [sun(700, 160, 60), ground(720, 25)]
        sp.block(700, 160, 110)
        b.append(U(sp, 380, 660, .85, pose="walk", accessory="roses"))
        b.append(flower_bed(860, 26, dense=1.1))
        b.append(scatter(sp, rnd, 6, kinds=("butterfly",)) + scatter(sp, rnd, 8))
        cap = "Le jardin des papillons"
    return b, cap


def t_roses(v, rnd):
    sp, b = Space(), []

    def arch(cx, top, w, h):
        o = stroke(f"M{cx - w / 2},{top + h} V{top + w / 2} A{w / 2},{w / 2} 0 0 1 {cx + w / 2},{top + w / 2} V{top + h}", OW + 8)
        o += stroke(f"M{cx - w / 2},{top + h} V{top + w / 2} A{w / 2},{w / 2} 0 0 1 {cx + w / 2},{top + w / 2} V{top + h}", OW + 8).replace(INK, "#fff").replace(f'stroke-width="{OW + 8}"', f'stroke-width="{OW - 1}"')
        for i in range(14):
            a = math.pi + math.pi * i / 13
            x, y = cx + w / 2 * math.cos(a), top + w / 2 + w / 2 * math.sin(a)
            o += leaf(x, y, 36, math.degrees(a) + 90) + rose(x, y, rnd.uniform(22, 28), rnd.uniform(0, 90))
        for yy in range(int(top + w / 2 + 40), int(top + h), 70):
            for sx in (-1, 1):
                o += leaf(cx + sx * w / 2, yy, 34, 90 - sx * 60) + rose(cx + sx * w / 2, yy + 20, 22)
        return o

    if v == 0:
        b += [ground(820, 31), arch(425, 170, 560, 700)]
        sp.block(425, 200, 300)
        b.append(U(sp, 420, 700, .75, pose="stand", accessory="roses", eyes="closed"))
        b.append(flower_bed(880, 31, dense=.9))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 8))
        cap = "L'arche de roses"
    elif v == 1:
        b += [ground(760, 32)]
        for x, y in [(140, 700), (720, 690)]:
            for i in range(7):
                b.append(leaf(x + rnd.uniform(-60, 60), y + rnd.uniform(-60, 60), 40, rnd.uniform(0, 360)))
            for i in range(6):
                b.append(rose(x + rnd.uniform(-60, 60), y + rnd.uniform(-70, 50), rnd.uniform(28, 36), rnd.uniform(0, 90)))
            sp.block(x, y, 120)
        b.append(U(sp, 420, 700, .85, flip=True, pose="prance", accessory="roses"))
        b.append(flower_bed(880, 33))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 10))
        cap = "Le jardin de roses"
    elif v == 2:
        b.append(portrait(sp, 0, -20, 1.0, flip=True))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Une couronne de roses"
    elif v == 3:
        # heart-shaped wreath of roses around the unicorn
        for i in range(46):
            t = i / 46 * 2 * math.pi
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            x, y = 425 + hx * 22, 470 + hy * 24
            b.append(leaf(x, y, 34, rnd.uniform(0, 360)))
            b.append(rose(x, y, rnd.uniform(28, 36), rnd.uniform(0, 90)) if i % 3 else blossom(x, y, 24, rot=rnd.uniform(0, 70)))
        b.append(U(sp, 400, 610, .6, pose="prance", accessory="crown"))
        b.append(flower_bed(880, 34, dense=.9))
        sp.block(425, 470, 380)
        b.append(scatter(sp, rnd, 10, box=(X0, Y0, X1, 900)))
        cap = "Mon coeur de roses"
    else:
        b += [ground(780, 35)]
        b.append(U(sp, 420, 720, .9, pose="lie", eyes="open", accessory="flowers"))
        for i in range(12):
            x = 90 + i * 60
            b.append(stem_flower(x, 1000, rnd.uniform(90, 150), rnd.uniform(26, 32), "rose"))
        b.append(scatter(sp, rnd, 4, kinds=("butterfly",)) + scatter(sp, rnd, 10))
        cap = "Le parfum des roses"
    return b, cap


def t_night(v, rnd):
    sp, b = Space(), []
    kinds = ("star", "star", "sparkle", "dot")
    if v == 0:
        b += [moon(650, 190, 90)]
        sp.block(650, 190, 120)
        b.append(cloud(420, 880, 3.3))
        b.append(U(sp, 420, 700, .9, pose="lie", eyes="closed", accessory="flowers"))
        b.append(scatter(sp, rnd, 26, kinds=kinds))
        cap = "Bonne nuit, licorne"
    elif v == 1:
        b += [moon(170, 170, 80), ground(760, 41)]
        sp.block(170, 170, 110)
        b.append(U(sp, 440, 700, .9, flip=True, pose="stand", accessory="crown"))
        for x in (120, 730):
            b.append(lantern(x, 900, 1.1))
        b.append(flower_bed(900, 42, dense=.6))
        b.append(scatter(sp, rnd, 24, kinds=kinds))
        cap = "Sous les étoiles"
    elif v == 2:
        b += [moon(620, 360, 170, False)]
        sp.block(620, 360, 180)
        b.append(U(sp, 330, 560, .7, rot=-12, pose="prance", wings="feather", accessory="bow"))
        b += [cloud(170, 900, 2.0), cloud(650, 930, 2.2)]
        b.append(scatter(sp, rnd, 26, kinds=kinds, box=(X0, Y0, X1, 850)))
        cap = "Voyage vers la lune"
    elif v == 3:
        b.append(portrait(sp, 0, 10, .95))
        b.append(moon(680, 180, 60))
        sp.block(680, 180, 80)
        b.append(scatter(sp, rnd, 20, kinds=kinds))
        cap = "Rêve étoilé"
    else:
        b += [moon(425, 170, 80)]
        sp.block(425, 170, 110)
        b.append(cloud(425, 900, 3.4))
        b.append(U(sp, 460, 720, .7, flip=True, pose="lie", eyes="closed", accessory="roses"))
        b.append(U(sp, 200, 800, .42, pose="lie", eyes="closed", accessory="bow", mark=False))
        b.append(scatter(sp, rnd, 24, kinds=kinds))
        cap = "Fais de beaux rêves"
    return b, cap


def t_sea(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [sun(160, 170, 60), cloud(620, 150, 1.0), waves(560), waves(600, amp=12), ground(820, 51)]
        sp.block(160, 170, 110)
        b.append(parasol(700, 900, .7))
        sp.block(700, 760, 130)
        b.append(U(sp, 390, 750, .85, pose="prance", accessory="flowers"))
        for x, y, k in [(110, 960, 0), (250, 1000, 1), (620, 990, 0), (730, 940, 1), (380, 980, 2)]:
            b.append(shell(x, y, .8, rnd.uniform(-30, 30)) if k == 0 else starfish(x, y, 34, rnd.uniform(0, 40)) if k == 1 else shell(x, y, .6))
        b.append(scatter(sp, rnd, 8, box=(X0, Y0, X1, 520)))
        cap = "À la plage"
    elif v == 1:
        b.append(bubbles(rnd, 30, (X0, Y0, X1, 900)))
        for x, y, fl in [(150, 250, False), (690, 200, True), (700, 520, False)]:
            b.append(fish(x, y, .9, fl))
            sp.block(x, y, 90)
        b.append(U(sp, 380, 640, .8, pose="prance", accessory="crown", mark=False))
        for x in range(90, 800, 110):
            b.append(tall_grass(x, 1000, rnd.uniform(90, 150), 5, x))
        b.append(shell(300, 970, .9) + starfish(560, 975, 40) + shell(720, 980, .8, 20))
        cap = "Sous l'océan"
    elif v == 2:
        b += [waves(700, amp=18), waves(760, amp=14), waves(820, amp=10)]
        b.append(U(sp, 420, 560, .8, flip=True, rot=6, pose="prance", wings="feather", accessory="roses"))
        b.append(cloud(150, 180, 1.0) + cloud(720, 240, 1.1))
        b.append(starfish(200, 930, 44, 10) + shell(420, 950, 1.0) + starfish(650, 940, 38, 30))
        b.append(scatter(sp, rnd, 14, box=(X0, Y0, X1, 680)))
        cap = "Au-dessus des vagues"
    elif v == 3:
        b.append(portrait(sp, 0, -10, .95, flip=True))
        b.append(shell(140, 960, .9, -20) + starfish(300, 990, 36) + shell(560, 990, .7, 10) + starfish(720, 950, 40, 20))
        b.append(bubbles(rnd, 12, (X0, Y0, X1, 400)))
        cap = "Licorne des mers"
    else:
        b += [sun(700, 170, 58), waves(600), ground(800, 54)]
        sp.block(700, 170, 110)
        b.append(U(sp, 380, 760, .8, pose="stand", accessory="bow", eyes="closed"))
        b.append(parasol(650, 990, 1.0) + towel(560, 990, 200, 50))
        b.append(shell(130, 970, .8) + starfish(260, 990, 34) + shell(400, 985, .6, 25) + starfish(760, 960, 30, 20))
        b.append(scatter(sp, rnd, 10, box=(X0, Y0, X1, 560)))
        cap = "Vive les vacances"
    return b, cap


def t_winter(v, rnd):
    sp, b = Space(), []
    kinds = ("snow", "snow", "star", "dot")
    if v == 0:
        b += [ground(760, 61), pine(130, 820, 260), pine(720, 800, 300), snow_mounds(930, 1)]
        for x, y, r in [(130, 700, 110), (720, 670, 120)]:
            sp.block(x, y, r)
        b.append(U(sp, 420, 720, .85, pose="prance", accessory="crown"))
        b.append(scatter(sp, rnd, 22, kinds=kinds))
        cap = "Il neige !"
    elif v == 1:
        b += [ground(760, 62), snow_mounds(930, 2), snowman(650, 940, 1.2), pine(110, 960, 160)]
        sp.block(650, 760, 160)
        b.append(U(sp, 330, 760, .8, pose="stand", accessory="bow"))
        b.append(scatter(sp, rnd, 22, kinds=kinds))
        cap = "Mon ami le bonhomme de neige"
    elif v == 2:
        b += [ground(700, 63)]
        for x, h in [(100, 240), (220, 200), (640, 220), (760, 260)]:
            b.append(pine(x, 760, h))
            sp.block(x, 640, 90)
        b.append(U(sp, 430, 800, .75, flip=True, pose="lie", accessory="roses", eyes="closed"))
        for x, w, h in [(120, 90, 70), (720, 100, 80)]:
            b.append(gift(x, 990, w, h))
        b.append(scatter(sp, rnd, 20, kinds=kinds))
        cap = "Un Noël magique"
    elif v == 3:
        b.append(portrait(sp, 0, 0, .98))
        b.append(scatter(sp, rnd, 18, kinds=kinds))
        cap = "Licorne des neiges"
    else:
        b.append(snowflake(425, 380, 280))
        sp.block(425, 380, 290)
        b += [ground(820, 64), snow_mounds(940, 4)]
        b.append(U(sp, 420, 800, .55, pose="prance", accessory="crown", mark=False))
        b.append(scatter(sp, rnd, 14, kinds=kinds, box=(X0, Y0, X1, 950)))
        cap = "Le grand flocon"
    return b, cap


def t_candy(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [ground(760, 71), lollipop(120, 520, 60), lollipop(740, 480, 64), ice_cream(620, 330, .9)]
        for x, y, r in [(120, 560, 90), (740, 520, 90), (620, 240, 110)]:
            sp.block(x, y, r)
        b.append(U(sp, 350, 710, .8, pose="prance", accessory="bow"))
        b.append(cupcake(140, 990, 1.0) + donut(420, 960, 50) + cupcake(700, 990, 1.0))
        b.append(scatter(sp, rnd, 12))
        cap = "Le pays des bonbons"
    elif v == 1:
        b.append(ice_cream(425, 820, 3.0))
        sp.block(425, 500, 300)
        b.append(U(sp, 200, 880, .45, pose="stand", accessory="flowers", mark=False))
        b.append(U(sp, 650, 880, .45, flip=True, pose="stand", accessory="bow", mark=False))
        b.append(scatter(sp, rnd, 12))
        cap = "Une glace géante"
    elif v == 2:
        b.append(U(sp, 425, 640, .72, pose="stand", accessory="crown"))
        b += [table(425, 790, 640, 120)]
        b.append(cupcake(170, 790, 1.1) + donut(330, 770, 44) + cupcake(520, 790, .9) + donut(680, 770, 44))
        b.append(lollipop(130, 300, 50) + lollipop(730, 300, 50))
        b.append(scatter(sp, rnd, 12, box=(X0, Y0, X1, 650)))
        cap = "Miam, des gâteaux !"
    elif v == 3:
        b.append(portrait(sp, 0, -20, .92, flip=True))
        b.append(cupcake(150, 1000, .9) + donut(330, 970, 40) + ice_cream(560, 1000, .55) + cupcake(720, 1000, .9))
        b.append(scatter(sp, rnd, 12))
        cap = "Douce comme un bonbon"
    else:
        b += [ground(700, 75)]
        for x in (110, 260, 590, 740):
            b.append(lollipop(x, 560 + rnd.uniform(-40, 40), 46))
            sp.block(x, 590, 80)
        b.append(U(sp, 420, 720, .8, flip=True, pose="walk", wings="fairy", accessory="flowers"))
        b.append(donut(150, 960, 50) + cupcake(420, 1000, 1.0) + donut(700, 960, 50))
        b.append(scatter(sp, rnd, 12))
        cap = "La forêt de sucettes"
    return b, cap


def t_tea(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [bunting(62, 90, 788, 90, 9, 36)]
        b.append(U(sp, 430, 640, .72, pose="stand", accessory="crown", blanket=True))
        b += [table(425, 800, 640, 130)]
        b.append(teapot(250, 800, .9) + teacup(560, 800, .9) + cupcake(710, 800, .8))
        b.append(scatter(sp, rnd, 12, box=(X0, 150, X1, 650)))
        cap = "L'heure du thé"
    elif v == 1:
        b.append(crown(425, 380, 2.4))
        sp.block(425, 290, 250)
        b.append(U(sp, 420, 760, .7, pose="prance", accessory="roses"))
        b.append(gem(150, 880, 1.4) + gem(700, 900, 1.2) + gem(260, 980, 1.0))
        b.append(scatter(sp, rnd, 14, box=(X0, Y0, X1, 950)))
        cap = "La couronne magique"
    elif v == 2:
        b.append(U(sp, 430, 660, .75, flip=True, pose="stand", wings="fairy", accessory="flowers"))
        b += [table(425, 820, 640, 110)]
        b.append(teacup(190, 820, 1.1) + teapot(460, 820, 1.0) + teacup(690, 820, 1.0))
        b.append(scatter(sp, rnd, 4, kinds=("butterfly",), box=(X0, Y0, X1, 640)) + scatter(sp, rnd, 8, box=(X0, Y0, X1, 640)))
        cap = "Un thé chez les fées"
    elif v == 3:
        b.append(portrait(sp, 0, 0, .98))
        b.append(gem(130, 880, 1.2) + gem(720, 860, 1.1))
        b.append(scatter(sp, rnd, 14))
        cap = "La reine licorne"
    else:
        b += [ground(760, 85)]
        b.append(U(sp, 430, 700, .9, pose="walk", accessory="crown", blanket=True))
        for x, y in [(140, 180), (700, 170)]:
            b.append(crown(x, y, .7))
            sp.block(x, y - 30, 80)
        b.append(flower_bed(880, 86))
        b.append(scatter(sp, rnd, 10))
        cap = "La parade royale"
    return b, cap


def t_fairy(v, rnd):
    sp, b = Space(), []
    if v == 0:
        b += [ground(720, 91), fairy_house(640, 830, 1.2)]
        sp.block(640, 620, 200)
        b.append(U(sp, 300, 740, .75, pose="stand", wings="fairy", accessory="flowers"))
        b.append(flower_bed(890, 91, dense=.8))
        b.append(scatter(sp, rnd, 4, kinds=("butterfly",)) + scatter(sp, rnd, 12, kinds=("sparkle", "star", "dot")))
        cap = "La maison des fées"
    elif v == 1:
        b.append(U(sp, 430, 600, 1.0, pose="prance", wings="fairy", accessory="crown"))
        b.append(cloud(200, 950, 1.8) + cloud(640, 960, 2.0))
        b.append(scatter(sp, rnd, 30, kinds=("sparkle", "star", "dot", "heart"), box=(X0, Y0, X1, 900)))
        cap = "Poussière de fée"
    elif v == 2:
        b += [ground(700, 93)]
        for x, y in [(120, 300), (300, 220), (560, 230), (740, 310)]:
            b.append(lantern(x, y, 1.0))
            sp.block(x, y - 40, 60)
        b.append(stroke("M62,140 Q425,330 788,150", DW + .4))
        b.append(U(sp, 430, 720, .85, flip=True, pose="lie", wings="fairy", accessory="roses"))
        b.append(flower_bed(880, 94))
        b.append(scatter(sp, rnd, 10, kinds=("sparkle", "star", "dot")))
        cap = "Les lanternes magiques"
    elif v == 3:
        b.append(portrait(sp, 0, 10, .95, flip=True))
        b.append(scatter(sp, rnd, 5, kinds=("butterfly",)) + scatter(sp, rnd, 14, kinds=("sparkle", "star", "dot")))
        cap = "La fée licorne"
    else:
        b += [rainbow(425, 700, 360), ground(720, 95), mushroom(130, 900, 1.0, True), fairy_house(720, 900, .8)]
        for x, y, r in [(130, 780, 120), (720, 760, 130)]:
            sp.block(x, y, r)
        b.append(U(sp, 420, 740, .7, pose="prance", wings="fairy", accessory="bow"))
        b.append(scatter(sp, rnd, 3, kinds=("butterfly",)) + scatter(sp, rnd, 12))
        cap = "Le royaume magique"
    return b, cap


THEMES = [t_rainbow, t_castle, t_birthday, t_mushroom, t_butterfly, t_roses,
          t_night, t_sea, t_winter, t_candy, t_tea, t_fairy]


def design_list():
    """Interleave themes so neighbouring pages always differ."""
    out = []
    for v in range(5):
        for i, t in enumerate(THEMES):
            out.append((t, (v + i) % 5, 1000 + len(out)))
    return out
