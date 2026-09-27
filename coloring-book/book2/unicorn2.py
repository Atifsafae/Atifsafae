"""Full-body unicorn in the elegant style (style F), with poses, wings and accessories.

Origin = centre of the body, facing right. Hooves touch y = 235 when standing.
Approximate extent: x -330..330, y -420..245.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "styles"))

from art2 import INK, P, circ, dot, ell, ell_d, f, fill_path, g, heart, star, stroke, union  # noqa: E402
import girly as girly_module  # noqa: E402
from girly import DW, OW, blossom, butterfly, hair_lock, leaf, rose, wave_line  # noqa: E402

LEG = 34

# Fill colours: all white for colouring pages; set by colored() for the cover.
COL = {"body": "#fff", "hair": ["#fff"], "horn": "#fff", "hoof": "#fff", "wing": "#fff"}
_hair_i = [0]


def hair_fill():
    _hair_i[0] += 1
    return COL["hair"][_hair_i[0] % len(COL["hair"])]


class colored:
    """with colored(body=..., hair=[...], ...): draw a coloured unicorn."""
    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        self.old = dict(COL)
        COL.update(self.kw)

    def __exit__(self, *a):
        COL.clear()
        COL.update(self.old)


def tube(d, thick=LEG, w=OW):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{thick + 2 * w}" stroke-linecap="round" '
            f'stroke-linejoin="round"/><path d="{d}" fill="none" stroke="#fff" stroke-width="{thick}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def hoof(x, y, ang=0, s=1.0):
    d = "M-19,-14 L19,-14 Q24,4 22,14 Q0,20 -22,14 Q-24,4 -19,-14 Z"
    return g(fill_path(d, OW - .5, COL["hoof"]) + stroke("M-18,-6 Q0,-2 18,-6", DW - .4), x, y, s, rot=ang)


def leg(points, hoof_ang=0):
    """points: (x, y) from the body down to the hoof; upper part thicker, one clean outline."""
    segs = list(zip(points, points[1:]))
    widths = [42, 30][:len(segs)] + [30] * (len(segs) - 2)
    ds = [f"M{f(a[0])},{f(a[1])} L{f(b[0])},{f(b[1])}" for a, b in segs]
    out = "".join(f'<path d="{d}" stroke="{INK}" stroke-width="{w + 2 * OW}" stroke-linecap="round" fill="none"/>'
                  for d, w in zip(ds, widths))
    out += "".join(f'<path d="{d}" stroke="{COL["body"]}" stroke-width="{w}" stroke-linecap="round" fill="none"/>'
                   for d, w in zip(ds, widths))
    (x0, y0), (x1, y1) = points[-2], points[-1]
    a = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
    return out + hoof(x1, y1 + 8, a)


LEGS = {
    # (far legs, near legs) — each leg is a polyline from the body to the hoof
    "prance": ([[(70, 30), (80, 115), (84, 195)], [(-60, 30), (-50, 115), (-44, 195)]],
               [[(108, 30), (150, 92), (124, 138)], [(-95, 30), (-116, 112), (-104, 195)]]),
    "stand": ([[(76, 30), (82, 115), (84, 195)], [(-62, 30), (-54, 115), (-52, 195)]],
              [[(106, 30), (110, 115), (112, 195)], [(-98, 30), (-108, 115), (-102, 195)]]),
    "walk": ([[(80, 30), (98, 115), (116, 192)], [(-60, 30), (-68, 115), (-78, 192)]],
             [[(106, 30), (98, 115), (82, 195)], [(-98, 30), (-90, 115), (-64, 195)]]),
}


def feather_wing(x, y, s=1.0, rot=0):
    """Feathered wing with scalloped rows, root at (0,0), sweeping up and back."""
    def scallops(pts, closed_top=None):
        d = ""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            nx, ny = (y1 - y0), -(x1 - x0)
            d += f" Q{f(mx - nx * .5)},{f(my - ny * .5)} {f(x1)},{f(y1)}"
        return d
    outer = [(-230, -210), (-222, -150), (-205, -100), (-178, -58), (-140, -25), (-92, -4), (-40, 6), (0, 4)]
    art = fill_path("M0,0 C-20,-110 -110,-195 -230,-210" + scallops(outer) + " Z", OW, COL["wing"])
    for row, k in [([(-185, -165), (-170, -118), (-148, -80), (-115, -48), (-75, -26), (-30, -16)], 1),
                   ([(-130, -128), (-112, -92), (-86, -64), (-52, -44), (-16, -34)], 2)]:
        art += stroke(f"M{row[0][0]},{row[0][1]}" + scallops(row), DW + .3)
    art += stroke("M-10,-20 C-40,-90 -100,-150 -180,-180", DW)
    return g(art, x, y, s, rot=rot)


def fairy_wing(x, y, s=1.0, rot=0):
    """Ornate butterfly/fairy wings with swirls (like the Gemini mushroom page)."""
    up = "M0,0 C-20,-90 -60,-170 -120,-200 C-160,-215 -175,-160 -160,-110 C-140,-50 -70,-10 0,0 Z"
    lo = "M0,4 C-60,20 -120,60 -120,110 C-118,150 -80,150 -55,120 C-30,90 -10,50 0,4 Z"
    out = fill_path(up, OW, COL["wing"]) + fill_path(lo, OW, COL["wing"])
    out += stroke("M-10,-8 C-40,-80 -80,-150 -125,-180 C-150,-190 -158,-150 -148,-115 C-130,-60 -70,-20 -10,-8", DW)
    out += stroke("M-10,10 C-55,28 -100,62 -104,104 C-104,132 -80,132 -62,110 C-40,84 -22,50 -10,10", DW)
    # swirls and spots
    for cx, cy, r in [(-110, -150, 18), (-80, -100, 14), (-130, -110, 10), (-80, 85, 14), (-50, 60, 9)]:
        pts = []
        for i in range(50):
            t = i / 49
            a = t * 3.4 * math.pi
            pts.append((cx + r * (1 - .8 * t) * math.cos(a), cy + r * (1 - .8 * t) * math.sin(a)))
        out += stroke(P(pts, False), DW - .3)
    for cx, cy, r in [(-150, -175, 6), (-160, -135, 5), (-40, -40, 7), (-100, 125, 6), (-115, 95, 5)]:
        out += circ(cx, cy, r, DW - .3)
    out += stroke("M-10,-4 C-40,-50 -60,-70 -90,-60 M-12,6 C-40,20 -50,30 -45,40", DW - .5)
    return g(out, x, y, s, rot=rot)


def unicorn(pose="prance", eyes="open", wings=None, accessory="roses", mark=True, blanket=False):
    out = []
    lying = pose == "lie"

    # ---- tail
    tail = [(-140, -32, 150, 180, 18, 1.0, 50, 1), (-140, -18, 124, 225, 22, 1.1, 54, -1),
            (-136, -4, 102, 205, 18, 1.0, 46, 1)]
    if lying:
        tail = [(-150, 10, 172, 170, 16, 1.0, 48, 1), (-150, 20, 155, 200, 20, 1.1, 50, -1),
                (-145, 30, 140, 180, 16, 1.0, 44, 1)]
    for x, y, ang, L, amp, wv, w0, c in tail:
        out.append(hair_lock(wave_line(x, y, ang, L, amp, wv, curl=c, curl_r=22), w0, fill=hair_fill(), strands=2))

    # ---- far wing
    if wings == "feather":
        out.append(feather_wing(-20, -60, .8, 16))
    elif wings == "fairy":
        out.append(fairy_wing(-5, -60, .8, 18))

    # ---- legs (drawn before the body so the body hides their tops)
    if not lying:
        far, near = LEGS[pose]
        for p in far + near:
            out.append(leg(p))
    else:
        out.append(leg([(40, 70), (140, 125), (205, 118)]))
        out.append(leg([(-110, 70), (-20, 128), (45, 124)]))

    # ---- body + neck + head silhouette
    by = 40 if lying else 0
    sil = [ell_d(0, by, 130, 70), ell_d(92, by + 5, 60, 62), ell_d(-92, by - 2, 66, 66),
           f"M55,{by - 55} C75,{by - 130} 120,-190 160,-215 L228,-168 C195,-130 170,{by - 70} 140,{by + 10} Z",
           ell_d(196, -222, 70, 64),
           "M200,-262 C250,-262 300,-222 318,-192 C332,-166 318,-140 290,-138 C262,-136 232,-150 206,-165 Z"]
    out.append(union(sil, OW + .5, COL["body"]))
    # body details
    out.append(stroke(f"M-60,{by + 30} C-80,{by - 10} -120,{by - 20} -150,{by + 10}", DW))      # thigh
    out.append(stroke("M160,-205 C150,-190 146,-170 150,-150", DW))                            # jaw

    # ---- blanket / saddle cloth with flowers (party / princess themes)
    if blanket:
        out.append(fill_path(f"M-40,{by - 68} C0,{by - 74} 50,{by - 72} 80,{by - 62} L90,{by + 25} "
                             f"Q20,{by + 50} -50,{by + 25} Z", OW - 1))
        out.append(stroke(f"M-45,{by + 12} Q20,{by + 36} 86,{by + 12}", DW))
        for x in (-30, 0, 30, 60):
            out.append(circ(x + 2, by + 34 - abs(x - 20) * .15, 6, DW))
        out.append(heart(20, by - 20, 16, w=DW + .5))

    # ---- flank mark
    if mark and not blanket:
        out.append(star(-70, by - 5, 16, w=DW + .5) + star(-40, by + 18, 9, w=DW) + star(-98, by + 16, 8, w=DW))

    # ---- ear, horn
    out.append(fill_path("M168,-270 C158,-318 170,-345 186,-360 C205,-330 208,-298 200,-272 Z", OW, COL["body"]))
    out.append(stroke("M182,-284 C176,-310 180,-330 186,-342", DW))
    out.append(fill_path("M206,-276 Q240,-345 280,-412 Q262,-345 250,-266 Q226,-262 206,-276 Z", OW, COL["horn"]))
    for t in (.2, .38, .56, .74):
        x0, y0 = 210 + (280 - 210) * t, -272 + (-412 + 272) * t
        wd = 40 * (1 - t) + 5
        out.append(stroke(f"M{f(x0 - 3)},{f(y0 + 2)} q{f(wd * .5)},{f(-4)} {f(wd)},{f(8 * (1 - t) + 2)}", DW + .3))

    # ---- mane
    mane = [(172, -272, 152, 165, 16, 1.0, 48, 1), (165, -256, 130, 225, 20, 1.1, 54, -1),
            (150, -224, 116, 235, 20, 1.1, 52, 1), (130, -182, 108, 210, 18, 1.0, 48, -1),
            (110, -138, 104, 170, 14, 1.0, 42, 1)]
    for x, y, ang, L, amp, wv, w0, c in mane:
        out.append(hair_lock(wave_line(x, y, ang, L, amp, wv, curl=c, curl_r=20), w0, fill=hair_fill(), strands=2))
    # forelock
    out.append(hair_lock(wave_line(200, -270, 55, 110, 10, 1.0, curl=-1, curl_r=12), 36, fill=hair_fill(), strands=1))
    out.append(hair_lock(wave_line(186, -272, 80, 120, 12, 1.2, curl=1, curl_r=12), 32, fill=hair_fill(), strands=1))

    # ---- face: big eye, lashes, blush, nostril, smile
    if eyes == "open":
        out.append(ell(236, -214, 21, 26, OW - 1, "#ffffff"))
        out.append(ell(240, -210, 14, 18, 0, INK))
        out.append(dot(245, -218, 6, "#ffffff") + dot(236, -202, 3, "#ffffff"))
        out.append(stroke("M213,-236 Q234,-248 256,-234", OW - 1))
        for i, (dx, dy) in enumerate([(-10, -12), (-4, -16), (4, -16)]):
            bx, by2 = 224 + i * 11, -241 - (2 if i == 1 else 0)
            out.append(stroke(f"M{bx},{by2} q{dx * .4},{dy * .5} {dx},{dy}", DW))
    else:
        out.append(stroke("M216,-214 Q236,-196 258,-212", OW - .5))
        for i, x in enumerate([222, 232, 243, 253]):
            out.append(stroke(f"M{x},{-205 + (3 if i in (1, 2) else 0)} q-2,9 -6,14", DW))
    out.append(ell(262, -175, 16, 10, DW, rot=15))
    out.append(stroke("M306,-190 q7,-7 12,1", DW + .6))
    out.append(stroke("M268,-150 Q288,-136 310,-150", DW + .8))

    # ---- accessories
    if accessory == "roses":
        out.append(leaf(150, -288, 44, 200) + leaf(250, -290, 42, -30))
        out.append(rose(172, -290, 28, 20) + rose(228, -292, 24, 60) + blossom(146, -262, 18, rot=10))
    elif accessory == "crown":
        d = "M150,-292 L160,-340 L178,-310 L196,-352 L214,-312 L232,-342 L238,-292 Q194,-282 150,-292 Z"
        out.append(fill_path(d, OW - 1))
        for x, y in [(160, -340), (196, -352), (232, -342)]:
            out.append(circ(x, y, 6, DW))
        out.append(heart(194, -306, 9, w=DW) + stroke("M154,-298 Q194,-290 236,-298", DW))
    elif accessory == "bow":
        out.append(fill_path("M150,-280 C120,-320 100,-280 112,-258 C122,-244 140,-252 150,-280 Z", OW - 1)
                   + fill_path("M150,-280 C160,-322 200,-310 190,-282 C184,-262 162,-262 150,-280 Z", OW - 1)
                   + circ(150, -278, 9, OW - 1))
    elif accessory == "flowers":
        out.append(blossom(160, -290, 20, rot=0) + blossom(200, -300, 17, rot=30) + blossom(236, -288, 16, rot=10))

    # ---- near wing
    if wings == "feather":
        out.append(feather_wing(10, -60, 1.0, 0))
    elif wings == "fairy":
        out.append(fairy_wing(10, -55, 1.0, 5))
    return "".join(out)


def baby(**kw):
    kw.setdefault("accessory", "bow")
    return g(unicorn(**kw), 0, 0, .55)
