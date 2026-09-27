"""Vector line-art building blocks for the unicorn coloring book.

All drawing is plain SVG. Coordinates are in 1/100 inch (a US-Letter page
is 850 x 1100 units). Every shape takes an optional `fill` so the same art
can be used uncoloured (interior pages) or coloured (cover).

Outlines of overlapping shapes are merged with the classic "stroke then
fill" trick: every shape of a group is first drawn with a double-width
black stroke, then all shapes are drawn again filled with no stroke, which
leaves a single clean outline around their union.
"""
import math
import random

INK = "#111"
W = 6          # main outline width
WD = 4         # detail line width


def f(v):
    return f"{v:.1f}"


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def circle(cx, cy, r, **kw):
    return ("circle", dict(cx=f(cx), cy=f(cy), r=f(r)), kw)


def ellipse(cx, cy, rx, ry, rot=0, **kw):
    t = f"rotate({f(rot)} {f(cx)} {f(cy)})" if rot else None
    a = dict(cx=f(cx), cy=f(cy), rx=f(rx), ry=f(ry))
    if t:
        a["transform"] = t
    return ("ellipse", a, kw)


def path(d, **kw):
    return ("path", dict(d=d), kw)


def rect(x, y, w, h, r=0, **kw):
    return ("rect", dict(x=f(x), y=f(y), width=f(w), height=f(h), rx=f(r)), kw)


def _attrs(a):
    return " ".join(f'{k}="{v}"' for k, v in a.items())


def union(shapes, fill="#fff", width=W):
    """Draw shapes as one merged silhouette with a single outline."""
    out = []
    for tag, a, kw in shapes:
        out.append(f'<{tag} {_attrs(a)} fill="none" stroke="{INK}" '
                   f'stroke-width="{width * 2}" stroke-linejoin="round"/>')
    for tag, a, kw in shapes:
        out.append(f'<{tag} {_attrs(a)} fill="{kw.get("fill", fill)}" stroke="none"/>')
    return "\n".join(out)


def shape(s, fill="#fff", width=W):
    tag, a, kw = s
    return (f'<{tag} {_attrs(a)} fill="{kw.get("fill", fill)}" stroke="{INK}" '
            f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')


def line(d, width=WD):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def g(content, x=0, y=0, s=1.0, flip=False, rot=0):
    sx = -s if flip else s
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) '
            f'scale({sx:.3f} {s:.3f})">{content}</g>')


# --------------------------------------------------------------------------
# small decorative objects
# --------------------------------------------------------------------------

def star_path(cx, cy, r, points=5, inner=0.48, rot=-90):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def star(cx, cy, r, fill="#fff", rot=-90):
    return shape(path(star_path(cx, cy, r, rot=rot)), fill=fill, width=WD + 1)


def sparkle(cx, cy, r, fill="#fff"):
    d = (f"M{f(cx)},{f(cy - r)} Q{f(cx + r * .18)},{f(cy - r * .18)} {f(cx + r)},{f(cy)} "
         f"Q{f(cx + r * .18)},{f(cy + r * .18)} {f(cx)},{f(cy + r)} "
         f"Q{f(cx - r * .18)},{f(cy + r * .18)} {f(cx - r)},{f(cy)} "
         f"Q{f(cx - r * .18)},{f(cy - r * .18)} {f(cx)},{f(cy - r)} Z")
    return shape(path(d), fill=fill, width=WD)


def heart_path(cx, cy, s):
    return (f"M{f(cx)},{f(cy + s * .9)} "
            f"C{f(cx - s * 1.3)},{f(cy + s * .1)} {f(cx - s * .9)},{f(cy - s * .9)} {f(cx)},{f(cy - s * .35)} "
            f"C{f(cx + s * .9)},{f(cy - s * .9)} {f(cx + s * 1.3)},{f(cy + s * .1)} {f(cx)},{f(cy + s * .9)} Z")


def heart(cx, cy, s, fill="#fff"):
    return shape(path(heart_path(cx, cy, s)), fill=fill, width=WD + 1)


def cloud(cx, cy, s, fill="#fff"):
    parts = [circle(cx - 55 * s, cy + 8 * s, 32 * s), circle(cx - 15 * s, cy - 18 * s, 42 * s),
             circle(cx + 32 * s, cy - 8 * s, 36 * s), circle(cx + 65 * s, cy + 14 * s, 26 * s),
             rect(cx - 60 * s, cy + 5 * s, 125 * s, 35 * s, 17 * s)]
    return union(parts, fill=fill)


def flower(cx, cy, r, petals=6, fill="#fff", center="#fff"):
    ps = [circle(cx + r * .62 * math.cos(2 * math.pi * i / petals),
                 cy + r * .62 * math.sin(2 * math.pi * i / petals), r * .45)
          for i in range(petals)]
    return union(ps, fill=fill, width=WD) + shape(circle(cx, cy, r * .36), fill=center, width=WD)


def tulip(x, y, h, fill="#fff"):
    stem = line(f"M{f(x)},{f(y)} Q{f(x - 6)},{f(y - h * .5)} {f(x)},{f(y - h * .75)}", WD)
    leaf = shape(path(f"M{f(x - 2)},{f(y - h * .25)} Q{f(x - 30)},{f(y - h * .45)} {f(x - 34)},{f(y - h * .6)} "
                      f"Q{f(x - 10)},{f(y - h * .5)} {f(x - 2)},{f(y - h * .25)} Z"), width=WD)
    top = y - h
    cup = shape(path(f"M{f(x - 22)},{f(top)} L{f(x - 11)},{f(top + 12)} L{f(x)},{f(top - 2)} "
                     f"L{f(x + 11)},{f(top + 12)} L{f(x + 22)},{f(top)} "
                     f"Q{f(x + 24)},{f(top + 34)} {f(x)},{f(top + 36)} Q{f(x - 24)},{f(top + 34)} {f(x - 22)},{f(top)} Z"),
                fill=fill, width=WD)
    return stem + leaf + cup


def grass_tuft(x, y, s=1):
    return line(f"M{f(x - 14 * s)},{f(y)} Q{f(x - 12 * s)},{f(y - 14 * s)} {f(x - 18 * s)},{f(y - 24 * s)} "
                f"M{f(x)},{f(y)} Q{f(x + 2 * s)},{f(y - 18 * s)} {f(x - 2 * s)},{f(y - 32 * s)} "
                f"M{f(x + 14 * s)},{f(y)} Q{f(x + 14 * s)},{f(y - 12 * s)} {f(x + 20 * s)},{f(y - 22 * s)}", WD)


def rainbow(cx, cy, r, bands=5, bw=26, fills=None):
    """Semicircular rainbow standing on (cx, cy)."""
    out = []
    for i in range(bands):
        ro = r - i * bw
        ri = ro - bw
        d = (f"M{f(cx - ro)},{f(cy)} A{f(ro)},{f(ro)} 0 0 1 {f(cx + ro)},{f(cy)} "
             f"L{f(cx + ri)},{f(cy)} A{f(ri)},{f(ri)} 0 0 0 {f(cx - ri)},{f(cy)} Z")
        fill = fills[i % len(fills)] if fills else "#fff"
        out.append(shape(path(d), fill=fill, width=WD + 1))
    return "\n".join(out)


def sun(cx, cy, r, fill="#fff", face=True):
    rays = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        a1, a2 = a - .13, a + .13
        rays.append(path(f"M{f(cx + r * .9 * math.cos(a1))},{f(cy + r * .9 * math.sin(a1))} "
                         f"L{f(cx + r * 1.45 * math.cos(a))},{f(cy + r * 1.45 * math.sin(a))} "
                         f"L{f(cx + r * .9 * math.cos(a2))},{f(cy + r * .9 * math.sin(a2))} Z"))
    out = union(rays, fill=fill, width=WD) + shape(circle(cx, cy, r), fill=fill)
    if face:
        out += line(f"M{f(cx - r * .45)},{f(cy - r * .1)} q{f(r * .15)},{f(-r * .18)} {f(r * .3)},0 "
                    f"M{f(cx + r * .15)},{f(cy - r * .1)} q{f(r * .15)},{f(-r * .18)} {f(r * .3)},0 "
                    f"M{f(cx - r * .35)},{f(cy + r * .25)} q{f(r * .35)},{f(r * .35)} {f(r * .7)},0", WD)
    return out


def moon(cx, cy, r, fill="#fff"):
    d = (f"M{f(cx + r * .3)},{f(cy - r)} A{f(r)},{f(r)} 0 1 0 {f(cx + r * .3)},{f(cy + r)} "
         f"A{f(r * .78)},{f(r * .78)} 0 1 1 {f(cx + r * .3)},{f(cy - r)} Z")
    return shape(path(d), fill=fill)


def balloon(x, y, r, fill="#fff"):
    body = shape(ellipse(x, y, r * .85, r), fill=fill)
    knot = shape(path(f"M{f(x - 8)},{f(y + r + 10)} L{f(x)},{f(y + r - 2)} L{f(x + 8)},{f(y + r + 10)} Z"), fill=fill, width=WD)
    string = line(f"M{f(x)},{f(y + r + 10)} q-18,40 0,80 q18,40 -4,90", 3)
    shine = line(f"M{f(x - r * .5)},{f(y - r * .3)} q{f(r * .1)},{f(-r * .35)} {f(r * .4)},{f(-r * .45)}", WD)
    return string + body + knot + shine


def butterfly(x, y, s, fill="#fff"):
    wings = [ellipse(x - 22 * s, y - 16 * s, 22 * s, 18 * s, -30), ellipse(x + 22 * s, y - 16 * s, 22 * s, 18 * s, 30),
             ellipse(x - 16 * s, y + 14 * s, 14 * s, 12 * s, 30), ellipse(x + 16 * s, y + 14 * s, 14 * s, 12 * s, -30)]
    out = "".join(shape(w, fill=fill, width=WD) for w in wings)
    out += shape(ellipse(x, y, 5 * s, 24 * s), fill=fill, width=WD)
    out += line(f"M{f(x - 2 * s)},{f(y - 22 * s)} q-6,-14 -14,-18 M{f(x + 2 * s)},{f(y - 22 * s)} q6,-14 14,-18", 3)
    out += shape(circle(x - 22 * s, y - 16 * s, 7 * s), width=3) + shape(circle(x + 22 * s, y - 16 * s, 7 * s), width=3)
    return out


def mushroom_house(x, y, s=1.0, fill="#fff", cap="#fff"):
    """Mushroom house standing on ground point (x, y)."""
    stem = shape(path(f"M{f(x - 48 * s)},{f(y)} Q{f(x - 55 * s)},{f(y - 70 * s)} {f(x - 40 * s)},{f(y - 110 * s)} "
                      f"L{f(x + 40 * s)},{f(y - 110 * s)} Q{f(x + 55 * s)},{f(y - 70 * s)} {f(x + 48 * s)},{f(y)} Z"), fill=fill)
    door = shape(path(f"M{f(x - 16 * s)},{f(y)} L{f(x - 16 * s)},{f(y - 38 * s)} "
                      f"A{f(16 * s)},{f(16 * s)} 0 0 1 {f(x + 16 * s)},{f(y - 38 * s)} L{f(x + 16 * s)},{f(y)} Z"), width=WD)
    knob = shape(circle(x + 9 * s, y - 20 * s, 3 * s), fill=INK, width=2)
    win = shape(circle(x + 30 * s, y - 72 * s, 11 * s), width=WD) + line(
        f"M{f(x + 19 * s)},{f(y - 72 * s)} h{f(22 * s)} M{f(x + 30 * s)},{f(y - 83 * s)} v{f(22 * s)}", 3)
    capd = (f"M{f(x - 100 * s)},{f(y - 100 * s)} C{f(x - 100 * s)},{f(y - 200 * s)} {f(x + 100 * s)},{f(y - 200 * s)} "
            f"{f(x + 100 * s)},{f(y - 100 * s)} Q{f(x)},{f(y - 80 * s)} {f(x - 100 * s)},{f(y - 100 * s)} Z")
    capsvg = shape(path(capd), fill=cap)
    spots = "".join(shape(circle(x + dx * s, y + dy * s, r * s), width=WD)
                    for dx, dy, r in [(-55, -125, 14), (0, -155, 17), (52, -128, 13), (-20, -115, 8), (28, -108, 7)])
    return stem + door + knob + win + capsvg + spots


def castle(x, y, s=1.0, fill="#fff"):
    """Fairy-tale castle standing on ground point (x, y)."""
    out = []

    def tower(cx, top, w, h):
        body = shape(rect(cx - w / 2, top, w, h), fill=fill)
        roof = shape(path(f"M{f(cx - w / 2 - 10 * s)},{f(top)} L{f(cx)},{f(top - w * 1.3)} L{f(cx + w / 2 + 10 * s)},{f(top)} Z"), fill=fill)
        pole = line(f"M{f(cx)},{f(top - w * 1.3)} v{f(-28 * s)}", 3)
        flag = shape(path(f"M{f(cx)},{f(top - w * 1.3 - 28 * s)} l{f(26 * s)},{f(8 * s)} l{f(-26 * s)},{f(8 * s)} Z"), width=3)
        win = shape(path(f"M{f(cx - 8 * s)},{f(top + 50 * s)} v{f(-14 * s)} a{f(8 * s)},{f(8 * s)} 0 0 1 {f(16 * s)},0 v{f(14 * s)} Z"), width=WD)
        return pole + flag + body + roof + win

    out.append(shape(rect(x - 120 * s, y - 150 * s, 240 * s, 150 * s), fill=fill))
    for i in range(6):
        out.append(shape(rect(x - 120 * s + i * 44 * s, y - 172 * s, 26 * s, 24 * s), fill=fill, width=WD))
    out.append(tower(x - 140 * s, y - 230 * s, 60 * s, 230 * s))
    out.append(tower(x + 140 * s, y - 230 * s, 60 * s, 230 * s))
    out.append(tower(x, y - 300 * s, 70 * s, 130 * s))
    out.append(shape(path(f"M{f(x - 35 * s)},{f(y)} v{f(-60 * s)} a{f(35 * s)},{f(35 * s)} 0 0 1 {f(70 * s)},0 v{f(60 * s)} Z"), width=WD))
    out.append(line(f"M{f(x)},{f(y)} v{f(-95 * s)}", 3))
    for dx in (-70, 70):
        out.append(shape(path(f"M{f(x + dx * s - 10 * s)},{f(y - 80 * s)} v{f(-18 * s)} a{f(10 * s)},{f(10 * s)} 0 0 1 {f(20 * s)},0 v{f(18 * s)} Z"), width=WD))
    return "\n".join(out)


def tree(x, y, s=1.0, fill="#fff"):
    trunk = shape(path(f"M{f(x - 14 * s)},{f(y)} L{f(x - 10 * s)},{f(y - 80 * s)} L{f(x + 10 * s)},{f(y - 80 * s)} L{f(x + 14 * s)},{f(y)} Z"), fill=fill)
    crown = union([circle(x, y - 130 * s, 50 * s), circle(x - 40 * s, y - 100 * s, 38 * s),
                   circle(x + 40 * s, y - 100 * s, 38 * s), circle(x, y - 88 * s, 34 * s)], fill=fill)
    apples = "".join(shape(circle(x + dx * s, y + dy * s, 7 * s), width=3)
                     for dx, dy in [(-30, -110), (20, -140), (35, -95), (-5, -100)])
    return trunk + crown + apples


def hills(y, width=850, fill="#fff", seed=0):
    rnd = random.Random(seed)
    a, b = rnd.uniform(-40, 40), rnd.uniform(-40, 40)
    d = (f"M-20,{f(y + a)} C200,{f(y - 60 + b)} 360,{f(y + 50)} 520,{f(y + 10 - a)} "
         f"S760,{f(y - 50 + b)} {width + 20},{f(y + 5)} L{width + 20},1200 L-20,1200 Z")
    return shape(path(d), fill=fill)


def gem(x, y, s, fill="#fff"):
    outer = shape(path(f"M{f(x - 30 * s)},{f(y - 10 * s)} L{f(x - 15 * s)},{f(y - 28 * s)} L{f(x + 15 * s)},{f(y - 28 * s)} "
                       f"L{f(x + 30 * s)},{f(y - 10 * s)} L{f(x)},{f(y + 28 * s)} Z"), fill=fill, width=WD)
    facets = line(f"M{f(x - 30 * s)},{f(y - 10 * s)} H{f(x + 30 * s)} M{f(x - 10 * s)},{f(y - 10 * s)} L{f(x)},{f(y + 28 * s)} "
                  f"L{f(x + 10 * s)},{f(y - 10 * s)} M{f(x - 15 * s)},{f(y - 28 * s)} L{f(x - 10 * s)},{f(y - 10 * s)} "
                  f"M{f(x + 15 * s)},{f(y - 28 * s)} L{f(x + 10 * s)},{f(y - 10 * s)}", 3)
    return outer + facets


def cupcake(x, y, s, fill="#fff"):
    wrap = shape(path(f"M{f(x - 34 * s)},{f(y - 40 * s)} L{f(x - 24 * s)},{f(y)} L{f(x + 24 * s)},{f(y)} L{f(x + 34 * s)},{f(y - 40 * s)} Z"), fill=fill, width=WD)
    ribs = line("".join(f"M{f(x + dx * s)},{f(y - 38 * s)} L{f(x + dx * .75 * s)},{f(y - 2 * s)} " for dx in (-17, 0, 17)), 3)
    icing = union([circle(x - 22 * s, y - 50 * s, 18 * s), circle(x + 22 * s, y - 50 * s, 18 * s),
                   circle(x, y - 64 * s, 24 * s), circle(x, y - 44 * s, 20 * s)], fill=fill, width=WD)
    cherry = shape(circle(x, y - 94 * s, 9 * s), width=WD) + line(f"M{f(x)},{f(y - 102 * s)} q4,-12 12,-16", 3)
    return wrap + ribs + icing + cherry


# --------------------------------------------------------------------------
# the unicorn
# --------------------------------------------------------------------------

def unicorn(eyes="open", wings=False, mark="star", bow=False, crown=False,
            pose="stand", body="#fff", mane_fills=None, horn="#fff", hoof="#fff",
            wing_fill="#fff", accent="#fff"):
    """A chibi unicorn facing right, origin at the centre of its body.

    Returns SVG markup. Roughly spans x -230..260, y -340..170.
    """
    mf = mane_fills or ["#fff"] * 6
    out = []

    # --- tail (behind everything)
    tail = [path("M-100,-30 C-170,-60 -230,-10 -205,60 C-190,100 -150,110 -130,90 "
                 "C-160,70 -160,30 -120,20 Z")]
    tail2 = [path("M-105,-10 C-190,0 -215,90 -165,140 C-140,160 -110,150 -105,130 "
                  "C-140,120 -140,60 -95,40 Z")]
    out.append(union(tail2, fill=mf[2]))
    out.append(union(tail, fill=mf[0]))
    out.append(line("M-175,20 q-10,30 5,55 M-160,90 q-10,20 0,40"))

    # --- far legs
    if pose == "stand":
        far = [rect(-58, 20, 34, 125, 17), rect(92, 20, 34, 125, 17)]
    else:  # lying down: far legs tucked under the body
        far = [ellipse(-30, 84, 45, 18)]
    out.append(union(far, fill=body))
    if pose == "stand":
        out.append(line("M-58,122 h34 M92,122 h34"))
        out.append(shape(rect(-56, 124, 30, 19, 8), fill=hoof, width=WD) +
                   shape(rect(94, 124, 30, 19, 8), fill=hoof, width=WD))

    # --- wing behind (far)
    if wings:
        out.append(_wing(-20, -55, 0.8, -15, wing_fill))

    # --- body, neck, head as a single silhouette
    sil = [ellipse(0, 0, 118, 80),
           ellipse(80, -80, 46, 95, 32),
           circle(112, -170, 80),
           ellipse(180, -128, 62, 50, 18)]
    if pose == "stand":
        sil += [rect(-100, 20, 36, 132, 18), rect(50, 20, 36, 132, 18)]
    else:
        sil += [ellipse(95, 78, 58, 22)]
    out.append(union(sil, fill=body))
    if pose == "stand":
        out.append(line("M-100,128 h36 M50,128 h36"))
        out.append(shape(rect(-98, 130, 32, 20, 8), fill=hoof, width=WD) +
                   shape(rect(52, 130, 32, 20, 8), fill=hoof, width=WD))
    else:
        out.append(line("M-112,62 C-120,10 -60,-5 -30,40"))                # haunch
        out.append(shape(ellipse(-5, 86, 42, 16), fill=body))              # back leg
        out.append(shape(ellipse(40, 86, 16, 14), fill=hoof, width=WD))
        out.append(shape(ellipse(150, 82, 16, 17), fill=hoof, width=WD))

    # --- ear
    out.append(shape(path("M78,-228 C60,-280 72,-305 88,-312 C112,-290 115,-258 108,-238 Z"), fill=body))
    out.append(line("M86,-240 C80,-270 86,-290 90,-298", 3))

    # --- horn
    out.append(shape(path("M118,-236 L168,-335 L150,-228 Z"), fill=horn))
    out.append(line("M124,-258 L155,-248 M132,-282 L159,-272 M142,-305 L163,-298", 3))

    # --- mane: two rows of soft overlapping locks along head and neck
    back = [(70, -238, 40), (40, -200, 42), (22, -155, 40), (10, -110, 38), (2, -68, 32)]
    front = [(100, -246, 32), (72, -212, 34), (56, -172, 34), (46, -130, 32), (40, -90, 28)]
    for i, (x, y, r) in enumerate(back):
        out.append(shape(ellipse(x, y, r, r * .9, -30), fill=mf[(i + 3) % len(mf)]))
        out.append(line(f"M{f(x - r * .55)},{f(y - r * .1)} q{f(r * .1)},{f(r * .5)} {f(r * .55)},{f(r * .6)}", 3))
    for i, (x, y, r) in enumerate(front):
        out.append(shape(ellipse(x, y, r, r * .85, -30), fill=mf[i % len(mf)]))
        out.append(line(f"M{f(x - r * .45)},{f(y - r * .2)} q{f(r * .05)},{f(r * .5)} {f(r * .5)},{f(r * .55)}", 3))
    # forelock
    out.append(shape(path("M112,-238 C140,-238 150,-212 140,-196 C130,-205 118,-210 104,-208 Z"), fill=mf[1]))

    # --- flower crown or bow
    if crown:
        for i, (x, y) in enumerate([(70, -250), (100, -262), (135, -245)]):
            out.append(flower(x, y, 20, 5))
    if bow:
        out.append(_bow(40, -250, accent))

    # --- face
    if eyes == "open":
        out.append(shape(ellipse(150, -168, 15, 20), fill=INK, width=2))
        out.append(f'<circle cx="155" cy="-176" r="6" fill="#fff"/><circle cx="146" cy="-160" r="3" fill="#fff"/>')
        out.append(line("M160,-186 l10,-10 M152,-189 l6,-13", 3))
    elif eyes == "wink":
        out.append(line("M134,-168 Q150,-152 166,-168 M160,-162 l10,-8", WD + 1))
    else:  # happy closed eyes like a sleeping / smiling pony
        out.append(line("M134,-166 Q150,-150 166,-166 M140,-158 l-6,8 M150,-155 l0,10 M160,-158 l6,8", WD + 1))
    out.append(shape(circle(182, -128, 13), fill=accent, width=3))       # cheek
    out.append(line("M218,-128 q6,-4 10,2", WD))                         # nostril
    out.append(line("M200,-100 Q214,-90 230,-104", WD))                   # smile

    # --- flank mark
    if mark == "star":
        out.append(star(-40, 0, 26, fill=accent))
    elif mark == "heart":
        out.append(heart(-40, 0, 26, fill=accent))
    elif mark == "moon":
        out.append(moon(-40, 0, 24, fill=accent))
    elif mark == "rainbow":
        out.append(rainbow(-40, 16, 38, bands=3, bw=10))

    # --- near wing
    if wings:
        out.append(_wing(-10, -45, 1.0, 0, wing_fill))
    return "\n".join(out)


def _wing(x, y, s, rot, fill):
    d = ("M0,0 C-20,-70 -80,-130 -170,-140 C-160,-120 -150,-110 -150,-100 "
         "C-170,-95 -185,-85 -190,-70 C-165,-68 -150,-62 -142,-55 "
         "C-160,-45 -170,-30 -170,-15 C-140,-22 -110,-22 -90,-15 "
         "C-100,0 -100,15 -95,25 C-60,15 -25,10 0,0 Z")
    art = shape(path(d), fill=fill) + line("M-30,-10 C-60,-60 -100,-90 -150,-100 "
                                           "M-40,-5 C-80,-35 -110,-50 -142,-55 M-45,2 C-70,-10 -80,-14 -90,-15", 3)
    return g(art, x, y, s, rot=rot)


def _bow(x, y, fill):
    return (shape(path(f"M{x},{y} C{x - 30},{y - 35} {x - 50},{y - 5} {x - 40},{y + 15} C{x - 25},{y + 20} {x - 10},{y + 10} {x},{y} Z"), fill=fill, width=WD)
            + shape(path(f"M{x},{y} C{x + 30},{y - 35} {x + 50},{y - 5} {x + 40},{y + 15} C{x + 25},{y + 20} {x + 10},{y + 10} {x},{y} Z"), fill=fill, width=WD)
            + shape(circle(x, y, 9), fill=fill, width=WD))


def baby_unicorn(**kw):
    return g(unicorn(**kw), 0, 0, 0.55)


def unicorn_portrait(eyes="open", mane_fills=None, horn="#fff", body="#fff", accent="#fff", crown=True):
    """Big head-and-shoulders unicorn portrait (reuses the head of `unicorn`)."""
    return unicorn(eyes=eyes, mane_fills=mane_fills, horn=horn, body=body, accent=accent,
                   crown=crown, mark=None, pose="sit")
