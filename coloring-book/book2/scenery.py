"""Scenery for the themed pages, drawn in the same elegant line style."""
import math
import random

from unicorn2 import (INK, P, circ, dot, ell, ell_d, f, fill_path, g, heart, star, stroke, union,
                      DW, OW, blossom, butterfly, leaf, rose)
from art2 import sparkle, cloud as _cloud, rainbow as _rainbow, daisy, swirl


def cloud(x, y, s=1.0):
    return _cloud(x, y, s, w=OW)


def rainbow(x, y, r, bands=6, bw=None):
    return _rainbow(x, y, r, bands, bw or r / 11, w=OW - 1)


def hills(y, seed=0, w=850):
    rnd = random.Random(seed)
    a, b = rnd.uniform(-30, 30), rnd.uniform(-30, 30)
    return fill_path(f"M-20,{f(y + a)} C200,{f(y - 60 + b)} 360,{f(y + 40)} 520,{f(y + 5 - a)} "
                     f"S760,{f(y - 45 + b)} {w + 20},{f(y + 5)} L{w + 20},1300 L-20,1300 Z", OW)


def tuft(x, y, s=1.0):
    return stroke(f"M{f(x - 16 * s)},{f(y)} q{f(2 * s)},{f(-16 * s)} {f(-8 * s)},{f(-28 * s)} "
                  f"M{f(x - 4 * s)},{f(y)} q{f(0)},{f(-22 * s)} {f(4 * s)},{f(-40 * s)} "
                  f"M{f(x + 10 * s)},{f(y)} q{f(2 * s)},{f(-14 * s)} {f(12 * s)},{f(-26 * s)}", DW + .4)


def tall_grass(x, y, h, n=5, seed=0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        bx = x + (i - n / 2) * 12
        tip = bx + rnd.uniform(-30, 30)
        hh = h * rnd.uniform(.7, 1.1)
        out.append(fill_path(f"M{f(bx - 6)},{f(y)} Q{f(bx - 4)},{f(y - hh * .6)} {f(tip)},{f(y - hh)} "
                             f"Q{f(bx + 6)},{f(y - hh * .5)} {f(bx + 7)},{f(y)} Z", DW + .4))
    return "".join(out)


def tulip(x, y, h, rot=0):
    top = y - h
    o = stroke(f"M{f(x)},{f(y)} Q{f(x - 8)},{f(y - h * .5)} {f(x)},{f(top + 30)}", DW + 1)
    o += leaf(x, y - h * .15, h * .45, -125, .3) + leaf(x, y - h * .3, h * .38, -55, .3)
    o += fill_path(f"M{f(x - 24)},{f(top)} L{f(x - 12)},{f(top + 14)} L{f(x)},{f(top - 4)} L{f(x + 12)},{f(top + 14)} "
                   f"L{f(x + 24)},{f(top)} Q{f(x + 26)},{f(top + 40)} {f(x)},{f(top + 42)} "
                   f"Q{f(x - 26)},{f(top + 40)} {f(x - 24)},{f(top)} Z", OW - 1)
    o += stroke(f"M{f(x)},{f(top + 4)} Q{f(x - 4)},{f(top + 24)} {f(x)},{f(top + 38)}", DW)
    return o


def stem_flower(x, y, h, r, kind="daisy"):
    o = stroke(f"M{f(x)},{f(y)} Q{f(x + 10)},{f(y - h * .5)} {f(x)},{f(y - h)}", DW + 1)
    o += leaf(x + 2, y - h * .35, h * .35, -30, .3)
    if kind == "daisy":
        o += daisy(x, y - h, r, 11, w=DW + .4)
    elif kind == "rose":
        o += rose(x, y - h, r)
    else:
        o += blossom(x, y - h, r)
    return o


def flower_bed(y0, seed=0, x0=40, x1=810, dense=1.0):
    """A lush strip of flowers, leaves and grass along the bottom of the page."""
    rnd = random.Random(seed)
    out = []
    for i in range(int(9 * dense)):
        x = x0 + (x1 - x0) * (i + rnd.uniform(.1, .9)) / (9 * dense)
        out.append(tall_grass(x, y0 + 70, rnd.uniform(60, 100), 4, seed + i))
    n = int(8 * dense)
    for i in range(n):
        x = x0 + 40 + (x1 - x0 - 80) * (i + rnd.uniform(.2, .8)) / n
        y = y0 + rnd.uniform(0, 45)
        k = rnd.random()
        if k < .3:
            out.append(tulip(x, y + 70, rnd.uniform(90, 130)))
        elif k < .65:
            out.append(stem_flower(x, y + 70, rnd.uniform(50, 90), rnd.uniform(26, 34), "daisy"))
        else:
            out.append(stem_flower(x, y + 70, rnd.uniform(40, 70), rnd.uniform(24, 30), "blossom"))
    for i in range(int(5 * dense)):
        out.append(rose(x0 + rnd.uniform(30, x1 - x0 - 30), y0 + rnd.uniform(60, 95), rnd.uniform(24, 34), rnd.uniform(0, 90)))
    return "".join(out)


def castle(x, y, s=1.0):
    out = []

    def tower(cx, top, tw, h, roof=1.5, flag=True):
        o = fill_path(f"M{f(cx - tw / 2)},{f(top)} h{f(tw)} V{f(y)} h{f(-tw)} Z", OW - .5)
        for i in range(int(h / (26 * s))):                        # bricks
            yy = top + 40 * s + i * 26 * s
            if yy < y - 20 * s and i % 2 == 0:
                o += stroke(f"M{f(cx - tw / 2 + 6)},{f(yy)} h{f(12 * s)} M{f(cx + tw / 2 - 18 * s)},{f(yy + 13 * s)} h{f(12 * s)}", DW - .6)
        for i in range(4):                                        # battlement
            bw = tw / 7
            o += fill_path(f"M{f(cx - tw / 2 + i * 2 * bw)},{f(top)} v{f(-16 * s)} h{f(bw)} v{f(16 * s)} Z", DW)
        o += fill_path(f"M{f(cx - tw / 2 - 10 * s)},{f(top - 14 * s)} h{f(tw + 20 * s)} v{f(14 * s)} h{f(-tw - 20 * s)} Z", DW + .4)
        rt = top - 14 * s
        o += fill_path(f"M{f(cx - tw / 2 - 8 * s)},{f(rt)} Q{f(cx - tw * .1)},{f(rt - tw * .5)} {f(cx)},{f(rt - tw * roof)} "
                       f"Q{f(cx + tw * .1)},{f(rt - tw * .5)} {f(cx + tw / 2 + 8 * s)},{f(rt)} Z", OW - .5)
        o += stroke(f"M{f(cx - tw * .25)},{f(rt - 4)} Q{f(cx - tw * .05)},{f(rt - tw * .7)} {f(cx)},{f(rt - tw * roof + 10)}", DW - .4)
        if flag:
            ft = rt - tw * roof
            o += stroke(f"M{f(cx)},{f(ft)} v{f(-34 * s)}", DW + .4)
            o += fill_path(f"M{f(cx)},{f(ft - 34 * s)} q{f(18 * s)},{f(-8 * s)} {f(34 * s)},{f(4 * s)} "
                           f"q{f(-14 * s)},{f(10 * s)} {f(-34 * s)},{f(12 * s)} Z", DW + .4)
        wy = top + 50 * s
        o += fill_path(f"M{f(cx - 11 * s)},{f(wy + 30 * s)} v{f(-22 * s)} a{f(11 * s)},{f(11 * s)} 0 0 1 {f(22 * s)},0 "
                       f"v{f(22 * s)} Z", DW + .4) + stroke(f"M{f(cx)},{f(wy - 3 * s)} V{f(wy + 30 * s)}", DW - .6)
        return o

    out.append(fill_path(f"M{f(x - 150 * s)},{f(y - 170 * s)} h{f(300 * s)} V{f(y)} H{f(x - 150 * s)} Z", OW))
    for i in range(8):
        out.append(fill_path(f"M{f(x - 150 * s + i * 40 * s)},{f(y - 170 * s)} v{f(-20 * s)} h{f(22 * s)} v{f(20 * s)} Z", DW + .4))
    out.append(tower(x - 185 * s, y - 280 * s, 80 * s, 280 * s))
    out.append(tower(x + 185 * s, y - 280 * s, 80 * s, 280 * s))
    out.append(tower(x - 80 * s, y - 330 * s, 60 * s, 160 * s, 1.7))
    out.append(tower(x + 80 * s, y - 330 * s, 60 * s, 160 * s, 1.7))
    out.append(tower(x, y - 400 * s, 95 * s, 230 * s, 1.6))
    out.append(fill_path(f"M{f(x - 48 * s)},{f(y)} v{f(-80 * s)} a{f(48 * s)},{f(48 * s)} 0 0 1 {f(96 * s)},0 v{f(80 * s)} Z", OW - 1))
    for i in range(1, 4):
        out.append(stroke(f"M{f(x - 48 * s + i * 24 * s)},{f(y)} V{f(y - 80 * s - (18 if i == 2 else 12) * s)}", DW - .4))
    for dx in (-110, 110):
        out.append(heart(x + dx * s, y - 110 * s, 14 * s, w=DW + .4))
    out.append(rose(x - 60 * s, y - 10 * s, 18 * s) + rose(x + 60 * s, y - 10 * s, 18 * s))
    return "".join(out)


def mushroom(x, y, s=1.0, door=True, spots=True, stars=False):
    o = fill_path(f"M{f(x - 44 * s)},{f(y)} Q{f(x - 52 * s)},{f(y - 70 * s)} {f(x - 34 * s)},{f(y - 120 * s)} "
                  f"L{f(x + 34 * s)},{f(y - 120 * s)} Q{f(x + 52 * s)},{f(y - 70 * s)} {f(x + 44 * s)},{f(y)} Z", OW - .5)
    if door:
        o += fill_path(f"M{f(x - 18 * s)},{f(y)} v{f(-42 * s)} a{f(18 * s)},{f(18 * s)} 0 0 1 {f(36 * s)},0 v{f(42 * s)} Z", DW + .4)
        o += dot(x + 10 * s, y - 22 * s, 3.2 * s)
        o += circ(x + 26 * s, y - 84 * s, 11 * s, DW) + stroke(f"M{f(x + 15 * s)},{f(y - 84 * s)} h{f(22 * s)} M{f(x + 26 * s)},{f(y - 95 * s)} v{f(22 * s)}", DW - .6)
    # gills
    o += fill_path(f"M{f(x - 105 * s)},{f(y - 112 * s)} Q{f(x)},{f(y - 70 * s)} {f(x + 105 * s)},{f(y - 112 * s)} "
                   f"Q{f(x)},{f(y - 100 * s)} {f(x - 105 * s)},{f(y - 112 * s)} Z", DW + .4)
    for i in range(-4, 5):
        o += stroke(f"M{f(x + i * 10 * s)},{f(y - 104 * s)} L{f(x + i * 22 * s)},{f(y - 94 * s + abs(i) * 2 * s)}", DW - .8)
    o += fill_path(f"M{f(x - 112 * s)},{f(y - 110 * s)} C{f(x - 118 * s)},{f(y - 230 * s)} {f(x + 118 * s)},{f(y - 230 * s)} "
                   f"{f(x + 112 * s)},{f(y - 110 * s)} Q{f(x)},{f(y - 128 * s)} {f(x - 112 * s)},{f(y - 110 * s)} Z", OW)
    if spots:
        for dx, dy, r in [(-62, -150, 16), (0, -180, 19), (60, -152, 15), (-25, -130, 9), (32, -128, 8)]:
            o += star(x + dx * s, y + dy * s, r * s, w=DW + .2) if stars else ell(x + dx * s, y + dy * s, r * s, r * .8 * s, DW + .4)
    return o


def balloon(x, y, r, heart_shape=False, string=160):
    if heart_shape:
        body = fill_path(f"M{f(x)},{f(y + r)} C{f(x - r * 1.5)},{f(y + r * .1)} {f(x - r * 1.05)},{f(y - r * 1.05)} "
                         f"{f(x)},{f(y - r * .4)} C{f(x + r * 1.05)},{f(y - r * 1.05)} {f(x + r * 1.5)},{f(y + r * .1)} "
                         f"{f(x)},{f(y + r)} Z", OW)
    else:
        body = fill_path(f"M{f(x)},{f(y + r)} C{f(x - r * 1.25)},{f(y + r * .55)} {f(x - r)},{f(y - r)} {f(x)},{f(y - r)} "
                         f"C{f(x + r)},{f(y - r)} {f(x + r * 1.25)},{f(y + r * .55)} {f(x)},{f(y + r)} Z", OW)
    return (stroke(f"M{f(x)},{f(y + r + 12)} q-18,{string * .25} 0,{string * .5} q16,{string * .25} -6,{string * .5}", DW)
            + body + fill_path(f"M{f(x - 9)},{f(y + r + 12)} L{f(x)},{f(y + r - 2)} L{f(x + 9)},{f(y + r + 12)} Z", DW + .4)
            + stroke(f"M{f(x - r * .5)},{f(y - r * .25)} q{f(r * .05)},{f(-r * .38)} {f(r * .38)},{f(-r * .52)}", DW + .6))


def bunting(x0, y0, x1, y1, n=9, sag=60, letters=None):
    """Garland of pennant flags; optional letters (one per flag)."""
    out = [stroke(f"M{f(x0)},{f(y0)} Q{f((x0 + x1) / 2)},{f((y0 + y1) / 2 + sag * 2)} {f(x1)},{f(y1)}", DW + .4)]

    def at(t):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag * 2
        return ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1,
                (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1)
    for i in range(n):
        t0, t1 = (i + .1) / n, (i + .9) / n
        (ax, ay), (bx, by) = at(t0), at(t1)
        cx, cy = (ax + bx) / 2, (ay + by) / 2 + 70
        out.append(fill_path(f"M{f(ax)},{f(ay)} L{f(bx)},{f(by)} L{f(cx)},{f(cy)} Z", DW + .6))
        if letters and i < len(letters) and letters[i] != " ":
            out.append(f'<text x="{f(cx)}" y="{f((ay + by) / 2 + 36)}" font-family="DejaVu Sans" font-weight="bold" '
                       f'font-size="30" fill="#fff" stroke="{INK}" stroke-width="2.4" text-anchor="middle">{letters[i]}</text>')
        else:
            out.append(heart(cx, (ay + by) / 2 + 26, 9, w=DW - .2) if i % 2 else star(cx, (ay + by) / 2 + 26, 10, w=DW - .2))
    return "".join(out)


def cake(x, y, s=1.0, candles=5):
    out = []
    tiers = [(170, 90), (135, 80), (100, 70)]
    top = y
    for i, (w, h) in enumerate(tiers):
        w, h = w * s, h * s
        yb = top
        yt = yb - h
        out.append(fill_path(f"M{f(x - w)},{f(yt + 12 * s)} L{f(x - w)},{f(yb - 10 * s)} Q{f(x)},{f(yb + 16 * s)} "
                             f"{f(x + w)},{f(yb - 10 * s)} L{f(x + w)},{f(yt + 12 * s)} Z", OW))
        drip = f"M{f(x - w - 4)},{f(yt + 10 * s)}"
        k = 7
        for j in range(k):
            xa = x - w + (2 * w) * (j + .5) / k
            xb = x - w + (2 * w) * (j + 1) / k
            drip += f" Q{f(xa - 8 * s)},{f(yt + 44 * s)} {f(xa)},{f(yt + 40 * s)} Q{f(xa + 10 * s)},{f(yt + 36 * s)} {f(xb + 4)},{f(yt + 14 * s)}"
        drip += f" L{f(x + w + 4)},{f(yt + 4 * s)} Q{f(x)},{f(yt - 16 * s)} {f(x - w - 4)},{f(yt + 4 * s)} Z"
        out.append(fill_path(drip, OW - 1))
        for j in range(5):
            xx = x - w * .7 + j * w * .35
            out.append(heart(xx, yb - h * .35, 9 * s, w=DW) if (i + j) % 2 else circ(xx, yb - h * .35, 6 * s, DW))
        top = yt + 6 * s
    for j in range(candles):
        cx = x - 60 * s + j * 30 * s
        out.append(fill_path(f"M{f(cx - 7 * s)},{f(top)} v{f(-50 * s)} h{f(14 * s)} v{f(50 * s)} Z", DW + .4))
        out.append(stroke(f"M{f(cx - 7 * s)},{f(top - 14 * s)} l{f(14 * s)},{f(-10 * s)} M{f(cx - 7 * s)},{f(top - 32 * s)} l{f(14 * s)},{f(-10 * s)}", DW - .6))
        out.append(fill_path(f"M{f(cx)},{f(top - 56 * s)} q{f(-10 * s)},{f(-14 * s)} 0,{f(-30 * s)} q{f(10 * s)},{f(16 * s)} 0,{f(30 * s)} Z", DW + .4))
    out.append(fill_path(f"M{f(x - 210 * s)},{f(y + 4)} Q{f(x)},{f(y + 40 * s)} {f(x + 210 * s)},{f(y + 4)} "
                         f"Q{f(x)},{f(y - 20 * s)} {f(x - 210 * s)},{f(y + 4)} Z", OW - 1))
    return "".join(out)


def gift(x, y, w, h, s=1.0):
    o = fill_path(f"M{f(x - w / 2)},{f(y - h)} h{f(w)} v{f(h)} h{f(-w)} Z", OW - .5)
    o += fill_path(f"M{f(x - w / 2 - 8)},{f(y - h - 26)} h{f(w + 16)} v{f(26)} h{f(-w - 16)} Z", OW - .5)
    o += fill_path(f"M{f(x - 9)},{f(y)} V{f(y - h - 26)} h18 V{f(y)} Z", DW)
    o += fill_path(f"M{f(x)},{f(y - h - 26)} C{f(x - 40)},{f(y - h - 70)} {f(x - 60)},{f(y - h - 26)} {f(x)},{f(y - h - 26)} Z", DW + .4)
    o += fill_path(f"M{f(x)},{f(y - h - 26)} C{f(x + 40)},{f(y - h - 70)} {f(x + 60)},{f(y - h - 26)} {f(x)},{f(y - h - 26)} Z", DW + .4)
    for i in range(3):
        o += dot(x - w / 4 + (i % 2) * w / 2 - 10, y - h * (.3 + .3 * i), 4)
    return o


def cupcake(x, y, s=1.0):
    o = fill_path(f"M{f(x - 40 * s)},{f(y - 50 * s)} L{f(x - 28 * s)},{f(y)} L{f(x + 28 * s)},{f(y)} L{f(x + 40 * s)},{f(y - 50 * s)} Z", OW - 1)
    o += stroke("".join(f"M{f(x + dx * s)},{f(y - 48 * s)} L{f(x + dx * .72 * s)},{f(y - 2 * s)} " for dx in (-24, -8, 8, 24)), DW - .4)
    o += union([ell_d(x - 26 * s, y - 60 * s, 22 * s, 18 * s), ell_d(x + 26 * s, y - 60 * s, 22 * s, 18 * s),
                ell_d(x, y - 78 * s, 30 * s, 24 * s), ell_d(x, y - 104 * s, 18 * s, 16 * s)], OW - 1)
    o += stroke(f"M{f(x - 30 * s)},{f(y - 66 * s)} q{f(30 * s)},{f(14 * s)} {f(60 * s)},0", DW - .4)
    o += circ(x, y - 126 * s, 9 * s, DW + .4) + stroke(f"M{f(x + 2 * s)},{f(y - 134 * s)} q4,-12 14,-16", DW)
    for dx, dy in [(-18, -80), (14, -90), (-4, -60), (24, -62)]:
        o += stroke(f"M{f(x + dx * s)},{f(y + dy * s)} l{f(6 * s)},{f(-3 * s)}", DW)
    return o


def ice_cream(x, y, s=1.0):
    cone = fill_path(f"M{f(x - 36 * s)},{f(y - 92 * s)} L{f(x)},{f(y)} L{f(x + 36 * s)},{f(y - 92 * s)} Z", OW - 1)
    grid = stroke(f"M{f(x - 24 * s)},{f(y - 92 * s)} L{f(x + 12 * s)},{f(y - 30 * s)} M{f(x)},{f(y - 92 * s)} L{f(x + 22 * s)},{f(y - 56 * s)} "
                  f"M{f(x + 24 * s)},{f(y - 92 * s)} L{f(x - 12 * s)},{f(y - 30 * s)} M{f(x)},{f(y - 92 * s)} L{f(x - 22 * s)},{f(y - 56 * s)}", DW - .6)
    s2 = circ(x, y - 160 * s, 34 * s, OW - 1)
    s1 = circ(x, y - 116 * s, 42 * s, OW - 1)
    drip = fill_path(f"M{f(x - 46 * s)},{f(y - 104 * s)} q{f(10 * s)},{f(24 * s)} {f(22 * s)},0 q{f(10 * s)},{f(28 * s)} {f(22 * s)},0 "
                     f"q{f(12 * s)},{f(20 * s)} {f(24 * s)},0 q{f(10 * s)},{f(22 * s)} {f(22 * s)},0 Q{f(x)},{f(y - 90 * s)} {f(x - 46 * s)},{f(y - 104 * s)} Z", OW - 1)
    cherry = circ(x + 4 * s, y - 202 * s, 11 * s, DW + .4) + stroke(f"M{f(x + 8 * s)},{f(y - 212 * s)} q4,-14 16,-18", DW)
    return cone + grid + s2 + s1 + drip + cherry


def lollipop(x, y, r):
    o = fill_path(f"M{f(x - 6)},{f(y)} h12 v{f(r * 3)} h-12 Z", DW + .4) + circ(x, y, r, OW - 1)
    pts = [(x + r * (1 - .85 * t) * math.cos(t * 4.4 * math.pi), y + r * (1 - .85 * t) * math.sin(t * 4.4 * math.pi))
           for t in [i / 80 for i in range(81)]]
    o += stroke(P(pts, False), DW + .4)
    o += fill_path(f"M{f(x - 8)},{f(y + r + 6)} C{f(x - 40)},{f(y + r - 14)} {f(x - 40)},{f(y + r + 34)} {f(x - 8)},{f(y + r + 14)} Z", DW)
    o += fill_path(f"M{f(x + 8)},{f(y + r + 6)} C{f(x + 40)},{f(y + r - 14)} {f(x + 40)},{f(y + r + 34)} {f(x + 8)},{f(y + r + 14)} Z", DW)
    return o


def donut(x, y, r):
    o = circ(x, y, r, OW - 1)
    o += fill_path(f"M{f(x - r * .92)},{f(y - r * .05)} C{f(x - r * .9)},{f(y - r * 1.05)} {f(x + r * .9)},{f(y - r * 1.05)} {f(x + r * .92)},{f(y - r * .05)} "
                   f"q{f(-r * .15)},{f(r * .35)} {f(-r * .3)},{f(r * .1)} q{f(-r * .3)},{f(r * .45)} {f(-r * .6)},{f(r * .2)} "
                   f"q{f(-r * .3)},{f(r * .42)} {f(-r * .62)},0 q{f(-r * .2)},{f(r * .2)} {f(-r * .3)},{f(-r * .25)} Z", DW + .4)
    o += circ(x, y - r * .1, r * .26, OW - 1)
    for dx, dy in [(-.55, -.4), (-.2, -.64), (.3, -.58), (.58, -.25), (-.62, .02), (.1, -.35)]:
        o += stroke(f"M{f(x + dx * r)},{f(y + dy * r)} l{f(r * .12)},{f(-r * .08)}", DW)
    return o


def moon(x, y, r, face=True):
    o = fill_path(f"M{f(x + r * .3)},{f(y - r)} A{f(r)},{f(r)} 0 1 0 {f(x + r * .3)},{f(y + r)} "
                  f"A{f(r * .78)},{f(r * .78)} 0 1 1 {f(x + r * .3)},{f(y - r)} Z", OW)
    if face:
        o += stroke(f"M{f(x - r * .42)},{f(y - r * .1)} q{f(r * .12)},{f(r * .12)} {f(r * .24)},0", DW + .4)
        o += stroke(f"M{f(x - r * .45)},{f(y + r * .3)} q{f(r * .15)},{f(r * .15)} {f(r * .3)},{f(-r * .03)}", DW + .4)
        o += ell(x - r * .55, y + r * .12, r * .1, r * .07, DW - .4)
    return o


def snowflake(x, y, r):
    o = ""
    for i in range(6):
        a = math.radians(i * 60)
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        o += stroke(f"M{f(x)},{f(y)} L{f(ex)},{f(ey)}", DW)
        for t in (.5, .75):
            bx, by = x + r * t * math.cos(a), y + r * t * math.sin(a)
            for sd in (-1, 1):
                o += stroke(f"M{f(bx)},{f(by)} l{f(r * .25 * math.cos(a + sd * .8))},{f(r * .25 * math.sin(a + sd * .8))}", DW - .4)
    return o + circ(x, y, r * .14, DW - .4)


def pine(x, y, h, snow=True):
    o = fill_path(f"M{f(x - 10)},{f(y)} v{f(-h * .15)} h20 v{f(h * .15)} Z", DW + .4)
    for i, (w, top) in enumerate([(.42, .55), (.34, .78), (.24, 1.0)]):
        yb = y - h * (.12 + i * .26)
        o += fill_path(f"M{f(x - h * w)},{f(yb)} Q{f(x)},{f(yb + 16)} {f(x + h * w)},{f(yb)} L{f(x)},{f(y - h * top)} Z", OW - 1)
        if snow:
            o += stroke(f"M{f(x - h * w * .6)},{f(yb - h * .08)} q{f(h * .1)},{f(10)} {f(h * .2)},0 q{f(h * .1)},{f(10)} {f(h * .2)},0", DW - .4)
    return o + star(x, y - h - 8, 14, w=DW + .4)


def snowman(x, y, s=1.0):
    o = circ(x, y - 70 * s, 70 * s, OW) + circ(x, y - 175 * s, 50 * s, OW)
    o += fill_path(f"M{f(x - 55 * s)},{f(y - 140 * s)} Q{f(x)},{f(y - 115 * s)} {f(x + 55 * s)},{f(y - 140 * s)} "
                   f"l{f(8 * s)},{f(20 * s)} Q{f(x)},{f(y - 92 * s)} {f(x - 62 * s)},{f(y - 120 * s)} Z", DW + .6)
    o += fill_path(f"M{f(x + 30 * s)},{f(y - 124 * s)} l{f(14 * s)},{f(60 * s)} l{f(22 * s)},{f(-8 * s)} Z", DW + .6)
    o += fill_path(f"M{f(x - 45 * s)},{f(y - 212 * s)} h{f(90 * s)} v{f(12 * s)} h{f(-90 * s)} Z", DW + .6)
    o += fill_path(f"M{f(x - 30 * s)},{f(y - 212 * s)} v{f(-60 * s)} h{f(60 * s)} v{f(60 * s)} Z", DW + .6)
    o += dot(x - 16 * s, y - 185 * s, 5 * s) + dot(x + 16 * s, y - 185 * s, 5 * s)
    o += fill_path(f"M{f(x)},{f(y - 172 * s)} l{f(40 * s)},{f(8 * s)} l{f(-40 * s)},{f(6 * s)} Z", DW)
    o += stroke(f"M{f(x - 18 * s)},{f(y - 155 * s)} q{f(18 * s)},{f(12 * s)} {f(36 * s)},0", DW)
    for dy in (50, 80, 110):
        o += dot(x, y - dy * s, 5 * s)
    return o


def shell(x, y, s=1.0, rot=0):
    o = fill_path("M0,30 C-50,20 -60,-30 -30,-50 Q0,-68 30,-50 C60,-30 50,20 0,30 Z", OW - 1)
    for a in (-40, -20, 0, 20, 40):
        o += stroke(f"M0,26 L{f(55 * math.sin(math.radians(a)))},{f(-55 * math.cos(math.radians(a)) + 6)}", DW - .4)
    o += fill_path("M-14,26 h28 l-6,14 h-16 Z", DW)
    return g(o, x, y, s, rot=rot)


def starfish(x, y, r, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * .45
        a = math.radians(rot - 90 + i * 36)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    o = fill_path(star_path_round(x, y, r, rot), OW - 1)
    for i in range(5):
        a = math.radians(rot - 90 + i * 72)
        for t in (.25, .45, .65):
            o += dot(x + r * t * math.cos(a), y + r * t * math.sin(a), 2.6)
    return o


def star_path_round(x, y, r, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * .45
        a = math.radians(rot - 90 + i * 36)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d = f"M{f((pts[9][0] + pts[0][0]) / 2)},{f((pts[9][1] + pts[0][1]) / 2)}"
    for i in range(10):
        p, q = pts[i], pts[(i + 1) % 10]
        d += f" Q{f(p[0])},{f(p[1])} {f((p[0] + q[0]) / 2)},{f((p[1] + q[1]) / 2)}"
    return d + " Z"


def fish(x, y, s=1.0, flip=False):
    o = fill_path("M-50,0 C-30,-36 30,-36 50,0 C30,36 -30,36 -50,0 Z", OW - 1)
    o += fill_path("M46,0 L84,-28 Q74,0 84,28 Z", OW - 1)
    o += fill_path("M-10,-28 Q6,-50 24,-26 Z", DW + .4)
    o += circ(-26, -6, 8, DW) + dot(-24, -6, 4)
    o += stroke("M-44,10 q6,6 12,0", DW) + stroke("M6,-18 q10,18 0,36 M22,-14 q8,14 0,28", DW - .4)
    return g(o, x, y, s, flip=flip)


def waves(y, x0=30, x1=820, amp=16, n=8):
    d = f"M{x0},{y}"
    step = (x1 - x0) / n
    for i in range(n):
        d += f" q{f(step / 4)},{f(-amp)} {f(step / 2)},0 q{f(step / 4)},{f(amp)} {f(step / 2)},0"
    return stroke(d, OW - 1)


def bubbles(rnd, n, box):
    x0, y0, x1, y1 = box
    o = ""
    for _ in range(n):
        x, y, r = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(6, 16)
        o += circ(x, y, r, DW) + stroke(f"M{f(x - r * .45)},{f(y - r * .1)} q{f(r * .1)},{f(-r * .35)} {f(r * .35)},{f(-r * .4)}", DW - .6)
    return o


def teapot(x, y, s=1.0):
    o = fill_path(f"M{f(x + 60 * s)},{f(y - 70 * s)} C{f(x + 110 * s)},{f(y - 80 * s)} {f(x + 110 * s)},{f(y - 140 * s)} "
                  f"{f(x + 140 * s)},{f(y - 150 * s)} L{f(x + 146 * s)},{f(y - 138 * s)} C{f(x + 124 * s)},{f(y - 124 * s)} "
                  f"{f(x + 124 * s)},{f(y - 50 * s)} {f(x + 50 * s)},{f(y - 40 * s)} Z", OW - 1)
    o += fill_path(f"M{f(x - 70 * s)},{f(y - 110 * s)} C{f(x - 130 * s)},{f(y - 120 * s)} {f(x - 130 * s)},{f(y - 40 * s)} "
                   f"{f(x - 66 * s)},{f(y - 44 * s)} L{f(x - 64 * s)},{f(y - 60 * s)} C{f(x - 110 * s)},{f(y - 60 * s)} "
                   f"{f(x - 106 * s)},{f(y - 104 * s)} {f(x - 70 * s)},{f(y - 94 * s)} Z", OW - 1)
    o += fill_path(f"M{f(x - 80 * s)},{f(y - 120 * s)} C{f(x - 100 * s)},{f(y - 20 * s)} {f(x - 50 * s)},{f(y)} {f(x)},{f(y)} "
                   f"C{f(x + 50 * s)},{f(y)} {f(x + 100 * s)},{f(y - 20 * s)} {f(x + 80 * s)},{f(y - 120 * s)} Z", OW)
    o += fill_path(f"M{f(x - 85 * s)},{f(y - 120 * s)} Q{f(x)},{f(y - 150 * s)} {f(x + 85 * s)},{f(y - 120 * s)} "
                   f"Q{f(x)},{f(y - 104 * s)} {f(x - 85 * s)},{f(y - 120 * s)} Z", OW - 1)
    o += fill_path(f"M{f(x - 50 * s)},{f(y - 134 * s)} Q{f(x)},{f(y - 185 * s)} {f(x + 50 * s)},{f(y - 134 * s)} Z", OW - 1)
    o += circ(x, y - 170 * s, 11 * s, DW + .4)
    o += rose(x, y - 62 * s, 26 * s) + leaf(x - 24 * s, y - 60 * s, 34 * s, 190) + leaf(x + 24 * s, y - 60 * s, 34 * s, -10)
    o += stroke(f"M{f(x - 90 * s)},{f(y - 100 * s)} Q{f(x)},{f(y - 80 * s)} {f(x + 90 * s)},{f(y - 100 * s)}", DW - .4)
    return o


def teacup(x, y, s=1.0):
    o = fill_path(f"M{f(x - 70 * s)},{f(y + 4 * s)} Q{f(x)},{f(y + 26 * s)} {f(x + 70 * s)},{f(y + 4 * s)} "
                  f"Q{f(x)},{f(y - 12 * s)} {f(x - 70 * s)},{f(y + 4 * s)} Z", OW - 1)
    o += fill_path(f"M{f(x + 40 * s)},{f(y - 60 * s)} C{f(x + 80 * s)},{f(y - 70 * s)} {f(x + 80 * s)},{f(y - 20 * s)} "
                   f"{f(x + 34 * s)},{f(y - 20 * s)} L{f(x + 36 * s)},{f(y - 32 * s)} C{f(x + 64 * s)},{f(y - 34 * s)} "
                   f"{f(x + 64 * s)},{f(y - 56 * s)} {f(x + 40 * s)},{f(y - 48 * s)} Z", OW - 1)
    o += fill_path(f"M{f(x - 50 * s)},{f(y - 70 * s)} C{f(x - 50 * s)},{f(y - 10 * s)} {f(x - 20 * s)},{f(y)} {f(x)},{f(y)} "
                   f"C{f(x + 20 * s)},{f(y)} {f(x + 50 * s)},{f(y - 10 * s)} {f(x + 50 * s)},{f(y - 70 * s)} Z", OW - 1)
    o += ell(x, y - 70 * s, 50 * s, 10 * s, DW + .4)
    o += heart(x, y - 38 * s, 12 * s, w=DW)
    o += stroke(f"M{f(x - 10 * s)},{f(y - 90 * s)} q{f(-10 * s)},{f(-14 * s)} 0,{f(-28 * s)} q{f(10 * s)},{f(-14 * s)} 0,{f(-28 * s)} "
                f"M{f(x + 14 * s)},{f(y - 86 * s)} q{f(-10 * s)},{f(-12 * s)} 0,{f(-24 * s)} q{f(10 * s)},{f(-12 * s)} 0,{f(-24 * s)}", DW - .4)
    return o


def table(x, y, w, h=120):
    o = fill_path(f"M{f(x - w / 2)},{f(y)} h{f(w)} l{f(20)},{f(h)} h{f(-w - 40)} Z", OW)
    d = f"M{f(x - w / 2 - 20)},{f(y + h)}"
    n = 10
    for i in range(n):
        d += f" q{f((w + 40) / n / 2)},{f(28)} {f((w + 40) / n)},0"
    o += stroke(d, OW - 1)
    o += stroke(f"M{f(x - w / 2 + 10)},{f(y + 30)} q{f(w / 4)},{f(20)} {f(w / 2)},0 q{f(w / 4)},{f(20)} {f(w / 2 - 20)},0", DW - .2)
    return o


def crown(x, y, s=1.0):
    d = (f"M{f(x - 70 * s)},{f(y)} L{f(x - 80 * s)},{f(y - 80 * s)} L{f(x - 40 * s)},{f(y - 40 * s)} L{f(x)},{f(y - 100 * s)} "
         f"L{f(x + 40 * s)},{f(y - 40 * s)} L{f(x + 80 * s)},{f(y - 80 * s)} L{f(x + 70 * s)},{f(y)} Z")
    o = fill_path(d, OW) + fill_path(f"M{f(x - 72 * s)},{f(y)} h{f(144 * s)} v{f(22 * s)} h{f(-144 * s)} Z", OW - 1)
    for dx, dy in [(-80, -80), (0, -100), (80, -80)]:
        o += circ(x + dx * s, y + dy * s, 10 * s, DW + .4)
    o += heart(x, y - 34 * s, 14 * s, w=DW) + circ(x - 40 * s, y + 11 * s, 6 * s, DW) + circ(x + 40 * s, y + 11 * s, 6 * s, DW)
    return o


def gem(x, y, s=1.0):
    o = fill_path(f"M{f(x - 30 * s)},{f(y - 10 * s)} L{f(x - 15 * s)},{f(y - 28 * s)} L{f(x + 15 * s)},{f(y - 28 * s)} "
                  f"L{f(x + 30 * s)},{f(y - 10 * s)} L{f(x)},{f(y + 30 * s)} Z", DW + .6)
    o += stroke(f"M{f(x - 30 * s)},{f(y - 10 * s)} H{f(x + 30 * s)} M{f(x - 10 * s)},{f(y - 10 * s)} L{f(x)},{f(y + 30 * s)} "
                f"L{f(x + 10 * s)},{f(y - 10 * s)} M{f(x - 15 * s)},{f(y - 28 * s)} L{f(x - 10 * s)},{f(y - 10 * s)} "
                f"M{f(x + 15 * s)},{f(y - 28 * s)} L{f(x + 10 * s)},{f(y - 10 * s)}", DW - .6)
    return o


def fairy_house(x, y, s=1.0):
    """Tree-stump house with a round door and a mushroom roof."""
    o = fill_path(f"M{f(x - 80 * s)},{f(y)} Q{f(x - 70 * s)},{f(y - 90 * s)} {f(x - 64 * s)},{f(y - 160 * s)} "
                  f"L{f(x + 64 * s)},{f(y - 160 * s)} Q{f(x + 70 * s)},{f(y - 90 * s)} {f(x + 80 * s)},{f(y)} Z", OW)
    for dx in (-44, 44):
        o += stroke(f"M{f(x + dx * s)},{f(y - 150 * s)} q{f(-6 * s)},{f(40 * s)} 0,{f(80 * s)}", DW - .4)
    o += fill_path(f"M{f(x - 30 * s)},{f(y)} v{f(-60 * s)} a{f(30 * s)},{f(30 * s)} 0 0 1 {f(60 * s)},0 v{f(60 * s)} Z", DW + .6)
    o += stroke(f"M{f(x)},{f(y)} V{f(y - 88 * s)}", DW - .4) + dot(x + 14 * s, y - 34 * s, 4 * s)
    o += circ(x + 44 * s, y - 110 * s, 14 * s, DW + .4) + circ(x - 44 * s, y - 116 * s, 12 * s, DW + .4)
    o += fill_path(f"M{f(x - 130 * s)},{f(y - 150 * s)} C{f(x - 120 * s)},{f(y - 280 * s)} {f(x + 120 * s)},{f(y - 280 * s)} "
                   f"{f(x + 130 * s)},{f(y - 150 * s)} Q{f(x)},{f(y - 170 * s)} {f(x - 130 * s)},{f(y - 150 * s)} Z", OW)
    for dx, dy, r in [(-70, -190, 16), (0, -225, 20), (70, -192, 15), (-30, -170, 9), (36, -168, 9)]:
        o += heart(x + dx * s, y + dy * s, r * s * .9, w=DW + .2)
    o += stroke(f"M{f(x - 90 * s)},{f(y)} q{f(10 * s)},{f(-8 * s)} {f(20 * s)},0 M{f(x + 70 * s)},{f(y)} q{f(10 * s)},{f(-8 * s)} {f(20 * s)},0", DW)
    return o


def sun(x, y, r, face=True):
    rays = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        rays.append(f"M{f(x + r * .9 * math.cos(a - .14))},{f(y + r * .9 * math.sin(a - .14))} "
                    f"Q{f(x + r * 1.5 * math.cos(a))},{f(y + r * 1.5 * math.sin(a))} "
                    f"{f(x + r * .9 * math.cos(a + .14))},{f(y + r * .9 * math.sin(a + .14))} Z")
    o = union(rays, DW + .6) + circ(x, y, r, OW)
    if face:
        o += stroke(f"M{f(x - r * .45)},{f(y - r * .05)} q{f(r * .13)},{f(r * .14)} {f(r * .26)},0 "
                    f"M{f(x + r * .19)},{f(y - r * .05)} q{f(r * .13)},{f(r * .14)} {f(r * .26)},0 "
                    f"M{f(x - r * .3)},{f(y + r * .3)} q{f(r * .3)},{f(r * .26)} {f(r * .6)},0", DW + .4)
    return o


def lantern(x, y, s=1.0):
    o = stroke(f"M{f(x)},{f(y - 70 * s)} v{f(-40 * s)}", DW)
    o += fill_path(f"M{f(x - 30 * s)},{f(y - 70 * s)} h{f(60 * s)} l{f(-10 * s)},{f(-14 * s)} h{f(-40 * s)} Z", DW + .4)
    o += fill_path(f"M{f(x - 26 * s)},{f(y - 70 * s)} Q{f(x - 40 * s)},{f(y - 35 * s)} {f(x - 26 * s)},{f(y)} h{f(52 * s)} "
                   f"Q{f(x + 40 * s)},{f(y - 35 * s)} {f(x + 26 * s)},{f(y - 70 * s)} Z", OW - 1)
    o += heart(x, y - 34 * s, 12 * s, w=DW) + fill_path(f"M{f(x - 22 * s)},{f(y)} h{f(44 * s)} v{f(10 * s)} h{f(-44 * s)} Z", DW + .4)
    return o


def book_heart_frame():
    return ""


def parasol(x, y, s=1.0):
    """Striped beach umbrella planted in the sand at (x, y)."""
    top = y - 230 * s
    o = stroke(f"M{f(x)},{f(y)} L{f(x + 8 * s)},{f(top)}", OW + 2)
    d = f"M{f(x - 150 * s)},{f(top + 60 * s)} Q{f(x - 120 * s)},{f(top - 70 * s)} {f(x + 8 * s)},{f(top - 80 * s)} " \
        f"Q{f(x + 136 * s)},{f(top - 70 * s)} {f(x + 166 * s)},{f(top + 60 * s)}"
    for i in range(5):
        xa = x - 150 * s + i * 63.2 * s
        d += "" if i == 0 else ""
    sc = ""
    xs = [x - 150 * s + i * 63.2 * s for i in range(6)]
    for xa, xb in zip(xs[::-1], xs[::-1][1:]):
        sc += f" Q{f((xa + xb) / 2)},{f(top + 30 * s)} {f(xb)},{f(top + 60 * s)}"
    o += fill_path(d + sc + " Z", OW)
    for xa in xs[1:-1]:
        o += stroke(f"M{f(xa)},{f(top + 60 * s)} Q{f((xa + x) / 2)},{f(top - 20 * s)} {f(x + 8 * s)},{f(top - 80 * s)}", DW)
    return o + circ(x + 8 * s, top - 84 * s, 7 * s, DW)


def towel(x, y, w=220, h=60):
    o = fill_path(f"M{f(x - w / 2)},{f(y)} L{f(x - w / 2 + 40)},{f(y - h)} H{f(x + w / 2 + 40)} L{f(x + w / 2)},{f(y)} Z", OW - 1)
    for i in range(1, 5):
        t = i / 5
        o += stroke(f"M{f(x - w / 2 + w * t)},{f(y)} L{f(x - w / 2 + 40 + w * t)},{f(y - h)}", DW)
    return o


def snow_mounds(y, seed=0):
    rnd = random.Random(seed)
    o = ""
    x = 30
    while x < 820:
        w = rnd.uniform(120, 220)
        h = rnd.uniform(30, 60)
        o += fill_path(f"M{f(x)},{f(y + 80)} Q{f(x + w / 2)},{f(y - h)} {f(x + w)},{f(y + 80)} Z", OW - 1)
        x += w * .7
    return o
