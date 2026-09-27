"""Style A: kawaii unicorn seen from the front (big head, big eyes)."""
from art2 import *


def eyes_open(x, y, s=1.0):
    out = ell(x, y, 25 * s, 31 * s, 3, INK)
    out += dot(x + 8 * s, y - 11 * s, 9 * s, "#fff") + dot(x - 8 * s, y + 12 * s, 4 * s, "#fff")
    side = 1 if x > 0 else -1
    for i, (a, L) in enumerate([(-60, 20), (-30, 22), (0, 18)]):
        ang = math.radians(a if side > 0 else 180 - a)
        bx = x + side * 18 * s * math.cos(math.radians(i * 25 - 60)) + side * 6 * s
        by = y - 24 * s + i * 9 * s
        out += stroke(f"M{f(bx)},{f(by)} q{f(side * L * .6 * s)},{f(-L * .2 * s)} "
                      f"{f(side * L * s)},{f(-L * .7 * s + i * 6 * s)}", 4)
    return out


def eyes_closed(x, y, s=1.0):
    side = 1 if x > 0 else -1
    out = stroke(f"M{f(x - 24 * s)},{f(y - 4 * s)} Q{f(x)},{f(y + 20 * s)} {f(x + 24 * s)},{f(y - 4 * s)}", 5)
    for i, dx in enumerate([-14, 0, 14]):
        out += stroke(f"M{f(x + dx * s)},{f(y + 7 * s + (3 if dx == 0 else 0) * s)} l{f(dx * .35 * s)},{f(11 * s)}", 4)
    return out


def unicorn_front(pose="sit", eyes="open", crown=False, bow=True, fills=None, body="#fff",
                  horn="#fff", hoof="#fff", cheek="#fff", detail=2):
    """Head centred on (0,0); sitting body below. detail=1 simpler lines for ages 3-5."""
    m = fills or ["#fff"] * 6
    out = []

    # ---- tail peeking out on the right, behind the body
    tail = [((150, 240), (250, 230), (260, 140), (215, 110)),
            ((150, 260), (270, 290), (300, 200), (275, 165)),
            ((140, 280), (230, 330), (280, 320), (290, 290))]
    for i, p in enumerate(tail[:3 if detail > 1 else 2]):
        out.append(lock(p, 70 - i * 8, 6, m[(i + 2) % 6], 5, detail > 1))
    out.append(swirl(215, 112, 14) if detail > 1 else "")

    # ---- back mane: locks falling behind the head on both sides
    left = [((-60, -115), (-185, -150), (-225, 20), (-165, 60)),
            ((-120, -40), (-240, 20), (-215, 190), (-140, 180))]
    back = left + [tuple((-x, y) for x, y in p) for p in left]
    for i, p in enumerate(back):
        out.append(lock(p, 88 - (i % 2) * 10, 12, m[i % 6], 6, detail > 1, bulge=0.25))

    # ---- body (sitting): chest, front legs, folded back legs
    if pose == "sit":
        out.append(union([ell_d(0, 210, 118, 100)], 6, body))
        out.append(ell(-112, 285, 58, 40, 6, body))
        out.append(ell(112, 285, 58, 40, 6, body))
        out.append(ell(-150, 305, 26, 18, 5, hoof))
        out.append(ell(150, 305, 26, 18, 5, hoof))
        legs = [f"M{x - 30},170 L{x - 32},300 Q{x},322 {x + 32},300 L{x + 30},170 Z" for x in (-42, 42)]
        out.append(union(legs, 6, body))
        for x in (-42, 42):
            out.append(fill_path(f"M{x - 32},288 Q{x},305 {x + 32},288 L{x + 32},300 Q{x},324 {x - 32},300 Z", 5, hoof))
    # ---- ears
    for sd in (-1, 1):
        out.append(fill_path(f"M{sd * 70},-100 C{sd * 80},-160 {sd * 110},-190 {sd * 140},-195 "
                             f"C{sd * 150},-160 {sd * 140},-120 {sd * 120},-85 Z", 6, body))
        out.append(fill_path(f"M{sd * 88},-108 C{sd * 96},-145 {sd * 115},-168 {sd * 130},-172 "
                             f"C{sd * 134},-150 {sd * 128},-125 {sd * 116},-104 Z", 4, cheek))

    # ---- head + muzzle silhouette
    out.append(union([ell_d(0, 0, 148, 126), ell_d(0, 70, 92, 62)], 6, body))
    out.append(stroke("M-78,40 Q0,18 78,40", 4))
    out.append(ell(-28, 82, 7, 10, 3, INK) + ell(28, 82, 7, 10, 3, INK))
    out.append(stroke("M-22,108 Q0,122 22,108", 4))

    # ---- horn
    out.append(fill_path("M-32,-112 Q-10,-200 0,-268 Q10,-200 32,-112 Q0,-100 -32,-112 Z", 6, horn))
    for y, wd in [(-140, 26), (-175, 18), (-210, 11)]:
        out.append(stroke(f"M{-wd},{y + 6} Q0,{y - 6} {wd},{y - 14}", 4))

    # ---- forelock (bangs) sweeping over the forehead
    bangs = [((5, -122), (-70, -140), (-125, -80), (-115, -25)),
             ((-12, -118), (-45, -95), (-60, -60), (-40, -45)),
             ((15, -120), (70, -140), (120, -100), (122, -55))]
    for i, p in enumerate(bangs):
        out.append(lock(p, [70, 42, 52][i], 5, m[(i + 4) % 6], 6, detail > 1))

    # ---- flower crown or bow
    if crown:
        for x, y, r, c in [(-80, -120, 26, 0), (-38, -140, 22, 1), (42, -140, 22, 2), (82, -120, 26, 3)]:
            out.append(flower(x, y, r, 5, m[c], "#fff"))
    if bow:
        out.append(fill_path("M100,-118 C80,-160 140,-175 150,-140 C152,-128 140,-120 100,-118 Z", 5, cheek))
        out.append(fill_path("M100,-118 C95,-80 140,-60 158,-88 C162,-100 150,-110 100,-118 Z", 5, cheek))
        out.append(circ(102, -118, 13, 5, cheek))

    # ---- face
    if eyes == "open":
        out.append(eyes_open(-62, -8) + eyes_open(62, -8))
    else:
        out.append(eyes_closed(-62, -8) + eyes_closed(62, -8))
    for sd in (-1, 1):
        out.append(ell(sd * 100, 40, 20, 13, 3, cheek))
        if detail > 1:
            out.append(stroke(f"M{sd * 96 - 10},{36} l6,-8 M{sd * 96},{38} l6,-8 M{sd * 96 + 10},{40} l6,-8", 3))
    return "".join(out)
