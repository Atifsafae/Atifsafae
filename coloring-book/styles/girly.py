"""Style F: elegant, feminine, more realistic unicorn with butterflies and flowers (ages 4-8)."""
import math
import random

from art2 import INK, P, dot, f, fill_path, g, stroke, star, sparkle, heart, leaf_d, circ, ell

OW = 5      # outline width
DW = 2.6    # inner detail width


# ---------------------------------------------------------------- ribbons (hair)
def normals(pts):
    ns = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1
        ns.append((-dy / m, dx / m))
    return ns


def ribbon_d(pts, widths):
    ns = normals(pts)
    L = [(x + nx * w / 2, y + ny * w / 2) for (x, y), (nx, ny), w in zip(pts, ns, widths)]
    R = [(x - nx * w / 2, y - ny * w / 2) for (x, y), (nx, ny), w in zip(pts, ns, widths)]
    return P(L + R[::-1])


def wave_line(x, y, ang, length, amp, waves, curl=1, curl_r=None, n=160):
    """Centreline: wavy stroke heading at `ang` degrees, ending in a curl."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i / n
        env = math.sin(math.pi / 2 * min(1, t * 2.2)) ** 2
        o = amp * math.sin(t * waves * 2 * math.pi) * env
        pts.append((x + ux * length * t + px * o, y + uy * length * t + py * o))
    # curl at the end
    ex, ey = pts[-1]
    dx, dy = ex - pts[-2][0], ey - pts[-2][1]
    m = math.hypot(dx, dy) or 1
    dx, dy = dx / m, dy / m
    r = curl_r or length * .09
    cx, cy = ex + (-dy) * r * curl, ey + dx * r * curl
    a0 = math.atan2(ey - cy, ex - cx)
    for i in range(1, 40):
        t = i / 40
        aa = a0 + curl * t * 1.6 * math.pi
        rr = r * (1 - .55 * t)
        pts.append((cx + rr * math.cos(aa), cy + rr * math.sin(aa)))
    return pts


def hair_lock(pts, w0, fill="#fff", strands=2, root=.12):
    n = len(pts)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        w = w0 * (1 - t) ** .9 + 3
        k = min(1, t / .2)
        w *= root + (1 - root) * (3 * k * k - 2 * k ** 3)
        ws.append(w)
    out = fill_path(ribbon_d(pts, ws), OW, fill)
    ns = normals(pts)
    for k in range(strands):
        off = (k + 1) / (strands + 1) - .5
        a, b = int(n * (.08 + .05 * k)), int(n * (.72 - .06 * k))
        line = [(x + nx * ws[i] * off * .8, y + ny * ws[i] * off * .8)
                for i, ((x, y), (nx, ny)) in enumerate(zip(pts, ns)) if a <= i <= b]
        out += stroke(P(line, False), DW)
    return out


# ---------------------------------------------------------------- flowers & butterflies
def rose(cx, cy, r, rot=0):
    """Cartoon rose: scalloped outline, crescent petals, curled centre."""
    ds = []
    for i in range(7):
        a = math.radians(rot + i * 360 / 7)
        x, y, rr = cx + r * .62 * math.cos(a), cy + r * .62 * math.sin(a), r * .42
        ds.append(f"M{f(x - rr)},{f(y)} A{f(rr)},{f(rr)} 0 1 0 {f(x + rr)},{f(y)} A{f(rr)},{f(rr)} 0 1 0 {f(x - rr)},{f(y)} Z")
    from art2 import union
    out = [union(ds, OW - 1)]
    for ring, (r0, r1, n, sp) in enumerate([(.5, .88, 5, 1.1), (.3, .56, 4, 1.3)]):   # cupped petals
        for i in range(n):
            a = math.radians(rot + ring * 30 + i * 360 / n)
            x0, y0 = cx + r * r0 * math.cos(a), cy + r * r0 * math.sin(a)
            x1, y1 = cx + r * r0 * math.cos(a + sp), cy + r * r0 * math.sin(a + sp)
            mx, my = cx + r * r1 * math.cos(a + sp / 2), cy + r * r1 * math.sin(a + sp / 2)
            out.append(stroke(f"M{f(x0)},{f(y0)} Q{f(mx)},{f(my)} {f(x1)},{f(y1)}", DW))
    pts = []                                             # curled bud in the centre
    for i in range(50):
        t = i / 49
        aa = math.radians(rot + 200) + t * 1.8 * math.pi
        rr = r * (.22 * (1 - t) + .04)
        pts.append((cx + rr * math.cos(aa), cy + rr * math.sin(aa)))
    out.append(stroke(P(pts, False), DW + .4))
    return "".join(out)


def leaf(x, y, L, ang, w=.34):
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    out = fill_path(leaf_d(x, y, L, ang, w), OW - 1)
    out += stroke(f"M{f(x)},{f(y)} Q{f((x + ex) / 2 + math.sin(a) * 4)},{f((y + ey) / 2 - math.cos(a) * 4)} "
                  f"{f(x + (ex - x) * .85)},{f(y + (ey - y) * .85)}", DW)
    for t in (.3, .5, .7):
        bx, by = x + (ex - x) * t, y + (ey - y) * t
        for sd in (-1, 1):
            vx = math.cos(a + sd * .7) * L * .16
            vy = math.sin(a + sd * .7) * L * .16
            out += stroke(f"M{f(bx)},{f(by)} l{f(vx)},{f(vy)}", DW - .6)
    return out


def blossom(cx, cy, r, petals=5, rot=0):
    """Five-petal flower with pointed-heart petals and stamens."""
    out = []
    for i in range(petals):
        a = math.radians(rot + i * 360 / petals)
        tipx, tipy = cx + r * math.cos(a), cy + r * math.sin(a)
        l = a - .55
        rr = a + .55
        d = (f"M{f(cx)},{f(cy)} C{f(cx + r * .9 * math.cos(l))},{f(cy + r * .9 * math.sin(l))} "
             f"{f(tipx + r * .35 * math.cos(a - 1.4))},{f(tipy + r * .35 * math.sin(a - 1.4))} {f(tipx)},{f(tipy)} "
             f"C{f(tipx + r * .35 * math.cos(a + 1.4))},{f(tipy + r * .35 * math.sin(a + 1.4))} "
             f"{f(cx + r * .9 * math.cos(rr))},{f(cy + r * .9 * math.sin(rr))} {f(cx)},{f(cy)} Z")
        out.append(fill_path(d, OW - 1))
        out.append(stroke(f"M{f(cx + r * .3 * math.cos(a))},{f(cy + r * .3 * math.sin(a))} "
                          f"L{f(cx + r * .62 * math.cos(a))},{f(cy + r * .62 * math.sin(a))}", DW - .4))
    out.append(circ(cx, cy, r * .2, OW - 1))
    for i in range(petals):
        a = math.radians(rot + 36 + i * 360 / petals)
        out.append(dot(cx + r * .3 * math.cos(a), cy + r * .3 * math.sin(a), 2.6))
    return "".join(out)


def butterfly(cx, cy, s=1.0, rot=0, pattern=0):
    """Detailed butterfly: layered wings with inner bands, veins and spots."""
    def wing(side):
        sd = side
        up = (f"M0,-6 C{sd * 30},-70 {sd * 110},-105 {sd * 128},-70 C{sd * 142},-40 {sd * 110},-5 {sd * 12},4 Z")
        lo = (f"M0,4 C{sd * 70},6 {sd * 108},40 {sd * 92},78 C{sd * 78},108 {sd * 30},92 0,20 Z")
        up_in = (f"M{sd * 10},-8 C{sd * 38},-52 {sd * 92},-78 {sd * 106},-62 C{sd * 116},-44 {sd * 92},-16 {sd * 18},-2 Z")
        lo_in = (f"M{sd * 10},8 C{sd * 58},12 {sd * 84},38 {sd * 76},64 C{sd * 66},84 {sd * 34},72 {sd * 10},22 Z")
        o = fill_path(lo, OW) + fill_path(up, OW)
        o += stroke(up_in, DW) + stroke(lo_in, DW)
        # veins
        for vx, vy in [(60, -70), (95, -55), (100, -30)]:
            o += stroke(f"M{sd * 8},-4 Q{sd * vx * .5},{vy * .45} {sd * vx},{vy}", DW - .6)
        for vx, vy in [(70, 50), (55, 75)]:
            o += stroke(f"M{sd * 8},8 Q{sd * vx * .5},{vy * .4} {sd * vx},{vy}", DW - .6)
        # spots along the edge
        spots = [(118, -62, 6), (126, -42, 5), (112, -20, 5), (96, 68, 6), (80, 88, 5)]
        if pattern == 1:
            spots += [(70, -60, 10), (70, 40, 9)]
        for x, y, r in spots:
            o += circ(sd * x, y, r, DW)
        if pattern == 0:
            o += fill_path(f"M{sd * 55},-50 q{sd * 14},-10 {sd * 24},4 q{sd * -8},14 {sd * -24},-4 Z", DW)
        return o

    body = (ell(0, 8, 7, 44, OW - 1) + circ(0, -40, 9, OW - 1)
            + stroke("M-3,-48 C-10,-72 -22,-86 -34,-90 M3,-48 C10,-72 22,-86 34,-90", DW)
            + circ(-35, -90, 3.5, DW) + circ(35, -90, 3.5, DW)
            + "".join(stroke(f"M-6,{y} q6,4 12,0", DW - .6) for y in (-10, 4, 18, 32)))
    return g(wing(-1) + wing(1) + body, cx, cy, s, rot=rot)


def dots_stars(rnd, n, box, avoid):
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        for _ in range(60):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if all(math.hypot(x - a, y - b) > r for a, b, r in avoid):
                break
        else:
            continue
        k = rnd.random()
        if k < .35:
            out.append(sparkle(x, y, rnd.uniform(9, 16), w=DW + .4))
        elif k < .65:
            out.append(star(x, y, rnd.uniform(8, 13), w=DW + .4, rot=rnd.uniform(-110, -70)))
        elif k < .8:
            out.append(heart(x, y, rnd.uniform(7, 11), w=DW + .4))
        else:
            out.append(circ(x, y, rnd.uniform(3, 5), DW))
        avoid.append((x, y, 30))
    return "".join(out)


# ---------------------------------------------------------------- the unicorn portrait
def unicorn_portrait(rnd):
    out = []
    # --- mane behind the neck: long wavy locks flowing down-left
    back_locks = [
        (425, 318, 152, 300, 34, 1.1, 66, 1), (412, 350, 138, 440, 42, 1.3, 78, -1),
        (398, 405, 124, 520, 44, 1.4, 80, 1), (382, 470, 113, 500, 40, 1.3, 76, -1),
        (366, 540, 104, 430, 36, 1.2, 70, 1), (352, 620, 97, 330, 30, 1.1, 62, -1),
        (430, 318, 165, 200, 22, .9, 50, -1),
    ]
    for x, y, ang, L, amp, wv, w0, c in back_locks:
        out.append(hair_lock(wave_line(x, y, ang, L, amp, wv, curl=c), w0, strands=3))

    # --- head + neck silhouette (profile facing right)
    head = ("M430,300 C492,286 545,330 572,398 C600,462 640,510 658,548 C672,582 652,612 620,614 "
            "C600,616 588,604 572,608 C552,614 530,604 515,584 C500,566 474,566 458,594 "
            "C470,650 500,700 530,760 C555,810 575,870 590,930 L270,930 C285,760 330,480 430,300 Z")
    out.append(fill_path(head, OW + 1))
    out.append(stroke("M458,594 C425,565 420,488 470,452", DW + .8))            # cheek
    out.append(stroke("M598,512 C612,530 614,548 606,560", DW))                  # nose ridge
    out.append(stroke("M628,560 q10,-10 18,2", DW + .8))                          # nostril
    out.append(stroke("M586,598 q12,6 24,0", DW + .6))                            # mouth
    # closed eye with long lashes
    out.append(stroke("M500,410 Q524,432 552,414", OW - .5))
    out.append(stroke("M497,404 Q522,392 552,408", DW))
    for i, (x, y) in enumerate([(506, 419), (517, 425), (529, 427), (541, 423), (551, 416)]):
        out.append(stroke(f"M{x},{y} q{-2 + i},{10} {-6 + i * 2.5},{16 + (2 if i in (1, 2, 3) else 0)}", DW))
    out.append(ell(560, 480, 20, 12, DW, rot=20))                                # blush
    # neck detail curve
    out.append(stroke("M480,680 C505,750 525,820 540,880", DW))

    # --- ear and horn
    out.append(fill_path("M412,318 C400,262 418,212 440,190 C462,226 470,272 462,318 Z", OW))
    out.append(stroke("M428,300 C422,262 430,232 440,214", DW))
    out.append(fill_path("M470,305 Q505,215 548,120 Q532,225 520,318 Q494,322 470,305 Z", OW))
    for t in (.18, .34, .5, .66, .8):
        x0 = 474 + (548 - 474) * t
        y0 = 303 + (120 - 303) * t
        wd = 44 * (1 - t) + 6
        out.append(stroke(f"M{f(x0 - 2)},{f(y0 + 2)} q{f(wd * .5)},{f(-4)} {f(wd)},{f(8 * (1 - t) + 2)}", DW + .4))

    # --- forelock falling over the forehead
    out.append(hair_lock(wave_line(462, 318, 70, 150, 14, 1.2, curl=-1, curl_r=16), 46, strands=2))
    out.append(hair_lock(wave_line(445, 322, 95, 175, 16, 1.4, curl=1, curl_r=16), 40, strands=2))

    # --- front mane locks over the neck
    front_locks = [(430, 320, 110, 440, 30, 1.3, 56, -1), (415, 335, 102, 400, 28, 1.2, 52, 1),
                   (400, 345, 96, 350, 24, 1.1, 46, -1)]
    for x, y, ang, L, amp, wv, w0, c in front_locks:
        out.append(hair_lock(wave_line(x, y, ang, L, amp, wv, curl=c), w0, strands=2))

    # --- crown of roses, leaves and blossoms around ear/horn
    for x, y, L, a in [(360, 300, 60, 200), (385, 262, 55, 240), (560, 300, 55, -20), (540, 262, 50, -50)]:
        out.append(leaf(x, y, L, a))
    out.append(rose(400, 322, 38, 10) + rose(528, 318, 34, 40) + rose(462, 300, 30, 80))
    out.append(blossom(355, 355, 26, rot=15) + blossom(570, 345, 22, rot=40))
    return "".join(out)


def page_f():
    rnd = random.Random(11)
    b = []
    b.append(unicorn_portrait(rnd))
    # flowers at the bottom, covering the neck
    for x, y, L, a in [(230, 945, 90, -150), (330, 960, 80, -100), (610, 950, 90, -30), (700, 960, 80, -70),
                       (470, 970, 70, -90), (130, 990, 70, -120), (780, 990, 70, -60), (60, 1000, 70, -140)]:
        b.append(leaf(x, y, L, a))
    for x, y, r, rot in [(300, 960, 62, 0), (455, 970, 70, 50), (610, 955, 60, 100), (160, 1000, 48, 30),
                         (750, 1000, 50, 80), (380, 1045, 44, 20), (540, 1050, 44, 60)]:
        b.append(rose(x, y, r, rot))
    for x, y, r in [(375, 895, 30), (535, 890, 28), (80, 940, 26), (815, 935, 26), (680, 895, 26), (240, 1050, 26), (660, 1055, 26)]:
        b.append(blossom(x, y, r, rot=rnd.uniform(0, 70)))
    # little flowers woven into the mane
    b.append(blossom(318, 575, 24, rot=10) + blossom(205, 690, 22, rot=40) + blossom(372, 455, 20, rot=70)
             + blossom(262, 470, 18, rot=20))
    # butterflies
    b.append(butterfly(700, 230, .9, 18, 0) + butterfly(760, 520, .6, -12, 1) + butterfly(140, 140, .55, -20, 1)
             + butterfly(690, 760, .45, 25, 0))
    avoid = [(700, 230, 130), (760, 520, 90), (140, 140, 80), (690, 760, 70), (470, 250, 120), (560, 150, 60),
             (600, 450, 110), (620, 600, 60)]
    b.append(dots_stars(rnd, 26, (30, 40, 820, 880), avoid + [(300, 600, 290), (420, 400, 130)]))
    return b
