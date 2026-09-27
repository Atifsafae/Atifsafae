"""Second-generation line art: smoother, cuter shapes for the style samples."""
import math

INK = "#111"


def f(v):
    return f"{v:.1f}"


def P(pts, close=True):
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return d + (" Z" if close else "")


def fill_path(d, w=6, fill="#fff"):
    return (f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def stroke(d, w=4):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def ell(cx, cy, rx, ry, w=6, fill="#fff", rot=0):
    t = f' transform="rotate({rot} {f(cx)} {f(cy)})"' if rot else ""
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="{w}"{t}/>')


def circ(cx, cy, r, w=6, fill="#fff"):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>'


def dot(cx, cy, r, fill=INK):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"/>'


def union(ds, w=6, fill="#fff"):
    """Several closed paths drawn as one silhouette with a single outline."""
    a = "".join(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w * 2}" stroke-linejoin="round"/>' for d in ds)
    b = "".join(f'<path d="{d}" fill="{fill}" stroke="none"/>' for d in ds)
    return a + b


def ell_d(cx, cy, rx, ry):
    return (f"M{f(cx - rx)},{f(cy)} A{f(rx)},{f(ry)} 0 1 0 {f(cx + rx)},{f(cy)} "
            f"A{f(rx)},{f(ry)} 0 1 0 {f(cx - rx)},{f(cy)} Z")


def g(content, x=0, y=0, s=1.0, flip=False, rot=0):
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sx:.3f} {s:.3f})">{content}</g>'


# ---------------------------------------------------------------- curves
def bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
            u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


def bez_d(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    return (3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2),
            3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2))


def lock_d(p, w0, w1=3, n=48, bulge=0.0, root=1.0):
    """Closed path of a tapered lock of hair following cubic bezier p."""
    L, R = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(p, t)
        dx, dy = bez_d(p, t)
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m
        w = (w0 * (1 - t) ** 0.8 + w1 * t) * (1 + bulge * math.sin(math.pi * t)) / 2
        if root < 1:  # taper the root too, so the lock starts in a point
            w *= root + (1 - root) * min(1, t / 0.25)
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return P(L + R[::-1])


def lock(p, w0, w1=3, fill="#fff", w=5, detail=True, bulge=0.3, root=1.0):
    out = fill_path(lock_d(p, w0, w1, bulge=bulge, root=root), w, fill)
    if detail:
        pts = []
        for i in range(0, 21):
            t = 0.12 + 0.55 * i / 20
            x, y = bez(p, t)
            dx, dy = bez_d(p, t)
            m = math.hypot(dx, dy) or 1
            off = w0 * 0.12 * (1 - t)
            pts.append((x - dy / m * off, y + dx / m * off))
        out += stroke(P(pts, False), 3)
    return out


def swirl(cx, cy, r, turns=1.4, w=3, cw=True):
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = t * turns * 2 * math.pi * (1 if cw else -1)
        rr = r * (1 - t * 0.85)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return stroke(P(pts, False), w)


# ---------------------------------------------------------------- small things
def star_d(cx, cy, r, inner=0.5, rot=-90, pts=5):
    out = []
    for i in range(pts * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / pts)
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return P(out)


def star(cx, cy, r, fill="#fff", w=5, rot=-90):
    return fill_path(star_d(cx, cy, r, rot=rot), w, fill)


def heart_d(cx, cy, s):
    return (f"M{f(cx)},{f(cy + s * .9)} C{f(cx - s * 1.35)},{f(cy + s * .05)} {f(cx - s * .95)},{f(cy - s * .95)} "
            f"{f(cx)},{f(cy - s * .35)} C{f(cx + s * .95)},{f(cy - s * .95)} {f(cx + s * 1.35)},{f(cy + s * .05)} "
            f"{f(cx)},{f(cy + s * .9)} Z")


def heart(cx, cy, s, fill="#fff", w=5):
    return fill_path(heart_d(cx, cy, s), w, fill)


def sparkle(cx, cy, r, fill="#fff", w=4):
    k = .2
    d = (f"M{f(cx)},{f(cy - r)} Q{f(cx + r * k)},{f(cy - r * k)} {f(cx + r)},{f(cy)} "
         f"Q{f(cx + r * k)},{f(cy + r * k)} {f(cx)},{f(cy + r)} Q{f(cx - r * k)},{f(cy + r * k)} {f(cx - r)},{f(cy)} "
         f"Q{f(cx - r * k)},{f(cy - r * k)} {f(cx)},{f(cy - r)} Z")
    return fill_path(d, w, fill)


def cloud(cx, cy, s, fill="#fff", w=6, face=False):
    ds = [ell_d(cx - 60 * s, cy + 10 * s, 38 * s, 34 * s), ell_d(cx - 18 * s, cy - 22 * s, 48 * s, 46 * s),
          ell_d(cx + 34 * s, cy - 10 * s, 42 * s, 40 * s), ell_d(cx + 72 * s, cy + 16 * s, 30 * s, 28 * s),
          f"M{f(cx - 70 * s)},{f(cy + 10 * s)} L{f(cx + 80 * s)},{f(cy + 10 * s)} L{f(cx + 80 * s)},{f(cy + 44 * s)} "
          f"L{f(cx - 70 * s)},{f(cy + 44 * s)} Z"]
    out = union(ds, w, fill)
    if face:
        out += (stroke(f"M{f(cx - 25 * s)},{f(cy + 8 * s)} q{f(8 * s)},{f(-10 * s)} {f(16 * s)},0 "
                       f"M{f(cx + 18 * s)},{f(cy + 8 * s)} q{f(8 * s)},{f(-10 * s)} {f(16 * s)},0", 4)
                + stroke(f"M{f(cx - 6 * s)},{f(cy + 20 * s)} q{f(8 * s)},{f(8 * s)} {f(16 * s)},0", 4))
    return out


def rainbow(cx, cy, r, bands=5, bw=28, fills=None, w=5):
    out = []
    for i in range(bands):
        ro, ri = r - i * bw, r - (i + 1) * bw
        d = (f"M{f(cx - ro)},{f(cy)} A{f(ro)},{f(ro)} 0 0 1 {f(cx + ro)},{f(cy)} L{f(cx + ri)},{f(cy)} "
             f"A{f(ri)},{f(ri)} 0 0 0 {f(cx - ri)},{f(cy)} Z")
        out.append(fill_path(d, w, fills[i % len(fills)] if fills else "#fff"))
    return "".join(out)


def flower(cx, cy, r, petals=5, fill="#fff", center="#fff", w=4, rot=0):
    ds = []
    for i in range(petals):
        a = math.radians(rot) + 2 * math.pi * i / petals
        ds.append(ell_d(cx + r * .55 * math.cos(a), cy + r * .55 * math.sin(a), r * .48, r * .48))
    return union(ds, w, fill) + circ(cx, cy, r * .32, w, center)


def daisy(cx, cy, r, petals=10, fill="#fff", w=3.5):
    out = []
    for i in range(petals):
        a = 360 * i / petals
        out.append(ell(cx + r * .55 * math.cos(math.radians(a)), cy + r * .55 * math.sin(math.radians(a)),
                       r * .45, r * .17, w, fill, rot=a))
    return "".join(out) + circ(cx, cy, r * .3, w, fill)


def leaf_d(x, y, L, ang, wd=0.35):
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    nx, ny = -math.sin(a) * L * wd, math.cos(a) * L * wd
    mx, my = (x + ex) / 2, (y + ey) / 2
    return (f"M{f(x)},{f(y)} Q{f(mx + nx)},{f(my + ny)} {f(ex)},{f(ey)} "
            f"Q{f(mx - nx)},{f(my - ny)} {f(x)},{f(y)} Z")


def limb(d, thick, w=6, fill="#fff"):
    """A rounded tube (leg, arm) following path d, with an outline."""
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{thick + 2 * w}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{thick}" stroke-linecap="round" stroke-linejoin="round"/>')
