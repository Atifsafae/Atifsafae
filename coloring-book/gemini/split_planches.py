"""Cut Gemini contact sheets ("planches") into one image per page.

    python3 split_planches.py planche1.jpg planche2.jpg ...   -> gemini/pages-extraites/

Each panel is found automatically (panels are separated by white gutters), then
enlarged 4x with line-art sharpening. Files are named  <sheet>-<n>.png  in reading
order (left to right, top to bottom); rename them 01-..., 02-... to match THEMES.

Warning: a panel from a 9-page sheet is ~350 px wide. Even enlarged it prints at
only ~45 dpi of real detail: fine for a draft, too blurry for a book sold on KDP.
"""
import os
import sys
from collections import deque

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pages-extraites")
STEP = 3            # work on a 1/3 scale grid for speed
MIN_AREA = 0.02     # a panel covers at least 2% of the sheet


def panels(im):
    g = im.convert("L")
    w, h = g.width // STEP, g.height // STEP
    small = g.resize((w, h), Image.BOX).filter(ImageFilter.MinFilter(3))   # thicken lines, close dashed frames
    ink = [[small.getpixel((x, y)) < 200 for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if ink[y][x] and not seen[y][x]:
                q = deque([(x, y)])
                seen[y][x] = True
                x0 = x1 = x
                y0 = y1 = y
                while q:
                    cx, cy = q.popleft()
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and ink[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((nx, ny))
                if (x1 - x0) * (y1 - y0) > MIN_AREA * w * h:
                    boxes.append((x0 * STEP, y0 * STEP, (x1 + 1) * STEP, (y1 + 1) * STEP))
    # drop boxes contained in bigger ones, sort in reading order
    boxes = [b for b in boxes if not any(o != b and o[0] <= b[0] and o[1] <= b[1] and o[2] >= b[2] and o[3] >= b[3]
                                         for o in boxes)]
    rows = sorted(boxes, key=lambda b: b[1])
    out, line = [], []
    for b in rows:
        if line and b[1] > line[0][1] + (line[0][3] - line[0][1]) * .5:
            out += sorted(line, key=lambda b: b[0])
            line = []
        line.append(b)
    return out + sorted(line, key=lambda b: b[0])


def enlarge(im, k=4):
    im = im.convert("L").resize((im.width * k, im.height * k), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    return im.point(lambda v: 0 if v < 95 else 255 if v > 205 else int((v - 95) * 255 / 110))


def main(paths):
    os.makedirs(OUT, exist_ok=True)
    for p in paths:
        im = Image.open(p)
        base = os.path.splitext(os.path.basename(p))[0]
        bs = panels(im)
        for i, (x0, y0, x1, y1) in enumerate(bs, 1):
            crop = im.crop((max(0, x0 - 4), max(0, y0 - 4), min(im.width, x1 + 4), min(im.height, y1 + 4)))
            enlarge(crop).save(os.path.join(OUT, f"{base}-{i:02d}.png"))
        print(f"{p}: {len(bs)} pages ({im.width}x{im.height} px sheet)")


if __name__ == "__main__":
    main(sys.argv[1:])
