#!/usr/bin/env python3
"""Paste the real Rumi logo mark onto the blank navy face patch of every emoji.

usage: paste_face.py <emoji-dir>/512 [out-dir]   (default: in place; sibling 128/ is refreshed too)
Per PNG: find the largest dark-navy blob (the face patch), fit its bbox, scale
the white logo mark to ~74% of the patch width and center it slightly above
the patch centre. Deterministic: the face IS the logo, pixel for pixel.
"""
import sys
from collections import deque
from pathlib import Path
from PIL import Image, ImageFilter

LOGO = Path.home() / ".claude/skills/rumi-brand/assets/rumi-mark-white-smile.png"
MARK_W = 0.74      # mark width as a fraction of patch width
Y_SHIFT = -0.02    # mark centre offset (fraction of patch height); logo dots sit high
GLOW = (168, 199, 255)  # brand pale-blue #A8C7FF


def is_navy(p):
    r, g, b, a = p
    return a > 200 and b > r + 30 and b > g + 15 and max(r, g, b) < 150  # shaded patches reach ~(40,70,120)


def face_bbox(im):
    px = im.load()
    w, h = im.size
    seen = bytearray(w * h)
    best = None
    for sy in range(0, h, 2):
        for sx in range(0, w, 2):
            if seen[sy * w + sx] or not is_navy(px[sx, sy]):
                continue
            q = deque([(sx, sy)]); seen[sy * w + sx] = 1
            n = 0; x0 = x1 = sx; y0 = y1 = sy
            while q:
                x, y = q.popleft(); n += 1
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and is_navy(px[nx, ny]):
                        seen[ny * w + nx] = 1; q.append((nx, ny))
            if best is None or n > best[0]:
                best = (n, (x0, y0, x1, y1))
    return best[1] if best else None


def paste(src, dst, logo):
    im = Image.open(src).convert("RGBA")
    bb = face_bbox(im)
    if not bb:
        print(f"  !! no face patch: {src.name}", file=sys.stderr); im.save(dst); return
    x0, y0, x1, y1 = bb
    pw, ph = x1 - x0 + 1, y1 - y0 + 1
    # erase anything the model drew on the patch: refill the inscribed ellipse row by row, lerping the
    # navy sampled just inside the ellipse's left/right edge (edges are never where features get drawn)
    px = im.load(); ex, ey = pw * 0.46, ph * 0.46; mx, my = x0 + pw / 2, y0 + ph / 2
    for y in range(int(my - ey), int(my + ey) + 1):
        t = (y - my) / ey
        hw = ex * max(0.0, 1 - t * t) ** 0.5
        xl, xr = int(mx - hw), int(mx + hw)
        if xr - xl < 6:
            continue
        cl, cr = px[xl + 2, y], px[xr - 2, y]
        if not (is_navy(cl) and is_navy(cr)):
            continue  # pseudopod overlapping the patch edge - leave this row alone
        for x in range(xl + 3, xr - 2):
            f = (x - xl) / (xr - xl)
            px[x, y] = tuple(int(cl[i] * (1 - f) + cr[i] * f) for i in range(3)) + (255,)
    # soften the row-wise refill (kills banding + any faint ghost) - blur only inside a slightly smaller ellipse
    blurred = im.filter(ImageFilter.GaussianBlur(max(2, pw // 40)))
    mask = Image.new("L", im.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).ellipse((mx - ex * 0.92, my - ey * 0.92, mx + ex * 0.92, my + ey * 0.92), fill=255)
    im.paste(blurred, (0, 0), mask)
    mw = int(pw * MARK_W)
    mark = logo.resize((mw, int(logo.height * mw / logo.width)), Image.LANCZOS)
    pad = mw // 8
    glow = Image.new("RGBA", (mark.width + 2 * pad, mark.height + 2 * pad), GLOW + (0,))
    glow.putalpha(Image.new("L", glow.size, 0))
    a = Image.new("L", glow.size, 0); a.paste(mark.getchannel("A"), (pad, pad))
    glow.putalpha(a.filter(ImageFilter.GaussianBlur(mw / 22)).point(lambda v: min(255, int(v * 0.9))))
    cx, cy = x0 + pw // 2, y0 + ph // 2 + int(ph * Y_SHIFT)
    im.alpha_composite(glow, (cx - glow.width // 2, cy - glow.height // 2))
    im.alpha_composite(mark, (cx - mark.width // 2, cy - mark.height // 2))
    im.save(dst)
    small = dst.parent.parent / "128"  # keep the Slack-size copies in sync with the pasted face
    if small.is_dir():
        im.resize((128, 128), Image.LANCZOS).save(small / dst.name)


if __name__ == "__main__":
    src = Path(sys.argv[1]); out = Path(sys.argv[2]) if len(sys.argv) > 2 else src
    out.mkdir(parents=True, exist_ok=True)
    logo = Image.open(LOGO).convert("RGBA")
    for f in sorted(src.glob("*.png")):
        paste(f, out / f.name, logo); print(f"  {f.name}")
