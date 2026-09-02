#!/usr/bin/env python3
"""Rumi face renderer - kawaii eyes + mouth glyphs in the Rumi logo's language (glowing white on the
navy face patch). Grammar learned from Kamal's 17 reference renders (reference/faces/):

  * features are SMALL and THIN: eye radius ~6-7% of patch width, stroke ~2.5%, eyes ~47% apart,
    mouth ~13% below the eye line, lots of navy breathing room. Calm, cute, friendly.
  * eyes and mouth are separate glyphs by default; `link=True` joins them with the logo's exact
    connecting curve (the brand mark) - used for the resting face and where the refs show it.
  * the BODY carries the drama (pseudopods, props, sparks, sweat, bubbles); the face stays gentle.

    render(name, width)             -> RGBA (white on transparent), coordinate box = logo box (661:255)
    compose(left, right, mouth, link=False, width=...) -> same, for any new expression
    python3 scripts/rumi_face.py out.png   -> prints logo IoU + writes the 54-face sheet

Glyph names (eyes, optional ":s|:m|:l" size suffix on dot):
  dot  arch(^)  squint(> <)  x  spiral  heart  star  closed(︶ sleep)  lidded  lid:sad  lid:angry
  dome(+worried brow)  wink  look:up  look:down  look:side
Mouths (optional size suffix on smile/open):  smile  open(filled D)  frown  flat  zigzag  o  openfrown  smirk
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw

# logo geometry, measured from rumi-mark-white-smile.png (661x255), in units of width
R_LOGO, EY, EXL, EXR, STROKE_LOGO, BOTTOM = 0.095, 0.103, 0.10, 0.90, 0.023, 0.372
R, STROKE, MY = 0.10, 0.032, EY + 0.22   # default eye radius, glyph stroke, mouth centre line
SS = 6
TOP, SIDE = 0.10, 0.06   # headroom above the eye row / beside the outer eyes - paste_face subtracts both

FACES = {  # name: (left eye, right eye, mouth, link)   - refs marked with the reference image number
    "happy": ("dot", "dot", "smile:m", True),            # brand face = the logo
    "wink": ("dot", "wink", "smile:s", False),
    "wave": ("dot", "dot", "smile:m", False),
    "thumbs-up": ("arch", "arch", "smile:m", False),
    "heart-eyes": ("heart", "heart", "smile:m", True),   # ref 9
    "laugh": ("squint", "squint", "open:l", False),
    "thinking": ("look:up", "look:up", "smirk", False),
    "sad": ("lid:sad", "lid:sad", "frown", False),
    "celebrate": ("squint", "squint", "smile:m", False),  # ref 2
    "done": ("arch", "arch", "smile:m", False),
    "working": ("dot:s", "dot:s", "flat", False),
    "loading": ("lidded", "lidded", "smile:s", False),
    "searching": ("dot:s", "dot:l", "smile:s", False),    # ref 6
    "idea": ("dot:l", "dot:l", "open:s", False),
    "writing": ("look:down", "look:down", "smile:s", False),
    "error": ("x", "x", "flat", False),                   # ref 4
    "warning": ("dome", "dome", "openfrown", False),      # ref 14
    "blocked": ("lidded", "lidded", "flat", False),
    "sleeping": ("closed", "closed", "smile:s", False),   # ref 5
    "low-battery": ("lidded", "lidded", "frown", False),
    "surprised": ("dot:l", "dot:l", "o", False),
    "confused": ("dot:l", "dot:s", "zigzag", False),      # ref 13
    "shy": ("lidded", "lidded", "smile:m", True),         # ref 8
    "crying": ("dome", "dome", "frown", False),
    "crying-laughing": ("squint", "squint", "open:l", False),
    "angry": ("dot", "dot", "frown", False),              # ref 1 (the 💢 lives on the body)
    "nervous": ("dot:l", "dot:s", "zigzag", False),       # ref 10
    "smug": ("lidded", "lidded", "smirk", False),
    "mind-blown": ("spiral", "spiral", "o", False),       # ref 11
    "eye-roll": ("look:up", "look:up", "flat", False),
    "facepalm": ("closed", "closed", "flat", False),
    "cool": ("dot", "dot", "smirk", False),
    "starstruck": ("star", "star", "open:l", False),      # ref 15
    "salute": ("wink", "dot", "smile:m", False),          # ref 12
    "shrug": ("dot", "dot", "zigzag", False),
    "peek": ("dot:l", "dot:l", "smile:s", False),
    "teaching": ("dot", "dot", "smile:m", False),
    "graduate": ("arch", "arch", "smile:m", False),
    "clap": ("arch", "arch", "open:s", False),            # ref 3
    "encourage": ("arch", "arch", "open:s", False),
    "listening": ("dot", "dot", "smile:s", False),
    "speaking": ("dot", "dot", "open:s", False),
    "100": ("star", "star", "open:s", False),
    "trophy": ("arch", "arch", "open:s", False),
    "book": ("look:down", "look:down", "smile:s", False),
    "thanks": ("closed", "closed", "smile:m", False),
    "dance": ("squint", "squint", "open:s", False),
    "heart": ("arch", "arch", "smile:m", False),
    "reading": ("look:down", "look:down", "smile:s", False),
    "charging": ("squint", "squint", "smile:m", False),   # ref 7 (energized)
    "hello": ("dot", "dot", "open:s", False),
    "curious": ("dot:s", "dot:l", "smile:s", False),      # ref 6
    "proud": ("lidded", "lidded", "open:s", False),       # ref 16
    "high-five": ("arch", "arch", "smile:l", False),
}


class _Shifted:
    """ImageDraw proxy that shifts every y by `dy` so glyph code can stay in logo coordinates."""
    def __init__(self, d, dx, dy): self.d, self.dx, self.dy = d, dx, dy
    def _sh(self, xy):
        flat = [c for p in xy for c in (p if isinstance(p, tuple) else (p,))] if isinstance(xy[0], tuple) else list(xy)
        return [(flat[i] + self.dx, flat[i + 1] + self.dy) for i in range(0, len(flat), 2)]
    def line(self, xy, **k): self.d.line(self._sh(xy), **k)
    def ellipse(self, xy, **k): self.d.ellipse(self._sh(xy), **k)
    def rectangle(self, xy, **k): self.d.rectangle(self._sh(xy), **k)
    def polygon(self, xy, **k): self.d.polygon(self._sh(xy), **k)
    def chord(self, xy, a, b, **k): self.d.chord(self._sh(xy), a, b, **k)


def _stroke(d, pts, w):
    d.line(pts, fill=255, width=max(1, int(w)), joint="curve")
    r = w / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)


def _arc(x0, y0, x1, y1, bulge, n=32):
    """points from (x0,y0) to (x1,y1) bowed by `bulge` (positive = downward on screen)."""
    return [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + bulge * 4 * t * (1 - t)) for t in [i / n for i in range(n + 1)]]


def _eye(d, spec, cx, cy, s, left):
    kind, _, size = spec.partition(":")
    r = R * s * {"s": 0.7, "m": 1.0, "l": 1.35}.get(size, 1.0)
    w = STROKE * s
    if kind == "dot":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    elif kind in ("lidded", "lid"):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        tilt = {"sad": (1 if left else -1), "angry": (-1 if left else 1)}.get(size, 0) * r * 0.55
        d.polygon([(cx - r - 2, cy - r - 2), (cx + r + 2, cy - r - 2),
                   (cx + r + 2, cy - r * 0.15 + tilt), (cx - r - 2, cy - r * 0.15 - tilt)], fill=0)
    elif kind == "dome":            # worried: flat-topped half dome + arched brow above
        d.ellipse((cx - r, cy - r * 0.6, cx + r, cy + r * 0.9), fill=255)
        d.rectangle((cx - r - 2, cy - r - 2, cx + r + 2, cy - r * 0.05), fill=0)
        inner = 1 if left else -1
        _stroke(d, _arc(cx - inner * r * 1.0, cy - r * 1.35, cx + inner * r * 0.9, cy - r * 1.9, -r * 0.35), w * 0.9)
    elif kind == "arch":            # ^ happy closed eye
        _stroke(d, [(cx - r, cy + r * 0.45), (cx, cy - r * 0.55), (cx + r, cy + r * 0.45)], w)
    elif kind == "wink":
        _stroke(d, [(cx - r, cy + r * 0.15), (cx, cy - r * 0.3), (cx + r, cy + r * 0.15)], w)
    elif kind == "closed":          # ︶ sleeping
        _stroke(d, _arc(cx - r, cy - r * 0.15, cx + r, cy - r * 0.15, r * 0.7), w)
    elif kind == "squint":          # > on the left eye, < on the right
        tip = cx + (r * 0.7 if left else -r * 0.7)
        base = cx - (r * 0.8 if left else -r * 0.8)
        _stroke(d, [(base, cy - r * 0.8), (tip, cy), (base, cy + r * 0.8)], w)
    elif kind == "x":
        _stroke(d, [(cx - r * 0.8, cy - r * 0.8), (cx + r * 0.8, cy + r * 0.8)], w)
        _stroke(d, [(cx - r * 0.8, cy + r * 0.8), (cx + r * 0.8, cy - r * 0.8)], w)
    elif kind == "spiral":
        pts = [(cx + (r * 1.25 * t) * math.cos(t * 2 * math.pi * 2.5 + math.pi), cy + (r * 1.25 * t) * math.sin(t * 2 * math.pi * 2.5 + math.pi))
               for t in [i / 60 for i in range(61)]]
        d.line(pts, fill=255, width=max(1, int(w * 0.8)), joint="curve")
    elif kind == "heart":
        rr = r * 1.2
        d.ellipse((cx - rr, cy - rr * 0.95, cx, cy + rr * 0.05), fill=255)
        d.ellipse((cx, cy - rr * 0.95, cx + rr, cy + rr * 0.05), fill=255)
        d.polygon([(cx - rr * 0.97, cy - rr * 0.25), (cx + rr * 0.97, cy - rr * 0.25), (cx, cy + rr * 0.95)], fill=255)
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rad = r * 1.3 if i % 2 == 0 else r * 0.58
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        d.polygon(pts, fill=255)
    elif kind == "look":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=max(1, int(w * 0.8)))
        dx, dy = {"up": (r * 0.1, -r * 0.4), "down": (0, r * 0.4), "side": (r * 0.45, 0)}.get(size, (0, 0))
        pr = r * 0.42
        d.ellipse((cx + dx - pr, cy + dy - pr, cx + dx + pr, cy + dy + pr), fill=255)


def _mouth(d, spec, s):
    kind, _, size = spec.partition(":")
    w = STROKE * s
    mx, my = 0.5 * s, MY * s
    if kind == "smile":
        hw = {"s": 0.11, "m": 0.17, "l": 0.23}.get(size, 0.17) * s
        _stroke(d, _arc(mx - hw, my - hw * 0.25, mx + hw, my - hw * 0.25, hw * 0.75), w)
    elif kind == "open":            # filled D: flat top, round bottom
        hw = {"s": 0.13, "l": 0.19}.get(size, 0.13) * s
        top = my - hw * 0.25
        d.chord((mx - hw, top - hw * 1.1, mx + hw, top + hw * 1.1), 0, 180, fill=255)
    elif kind == "frown":
        hw = 0.15 * s
        _stroke(d, _arc(mx - hw, my + hw * 0.3, mx + hw, my + hw * 0.3, -hw * 0.6), w)
    elif kind == "flat":
        _stroke(d, [(mx - 0.15 * s, my), (mx + 0.15 * s, my)], w)
    elif kind == "zigzag":
        hw, amp, n = 0.18 * s, 0.035 * s, 4
        pts = [(mx - hw + 2 * hw * i / (2 * n), my + (amp if i % 2 else -amp)) for i in range(2 * n + 1)]
        d.line(pts, fill=255, width=max(1, int(w)), joint="curve")
        _stroke(d, pts[:1], w); _stroke(d, pts[-1:], w)
    elif kind == "o":
        rr = 0.05 * s
        d.ellipse((mx - rr, my - rr, mx + rr, my + rr), fill=255)
    elif kind == "openfrown":       # small filled blob bulging UP (worried)
        hw = 0.085 * s
        d.chord((mx - hw, my - hw * 0.9, mx + hw, my + hw * 0.9), 180, 360, fill=255)
    elif kind == "smirk":
        hw = 0.16 * s
        _stroke(d, _arc(mx - hw, my + hw * 0.1, mx + hw * 1.05, my - hw * 0.35, hw * 0.45), w)


def _logo_curve(d, s):
    """the exact connecting curve of the logo mark (attach x ≈ 0.145, bottom 0.372)"""
    x0, x1, ay = 0.145, 0.855, 0.195
    k = (BOTTOM - ay) / ((x1 - x0) / 2) ** 2
    pts = [((x0 + (x1 - x0) * i / 48) * s, (BOTTOM - k * ((x0 + (x1 - x0) * i / 48) - 0.5) ** 2) * s) for i in range(49)]
    _stroke(d, pts, STROKE_LOGO * s)


def compose(left, right, mouth, link=False, width=661):
    s = width * SS
    W, H = int((1 + 2 * SIDE) * s), int((TOP + 255 / 661 + 0.10) * s)
    im = Image.new("L", (W, H), 0)
    d = _Shifted(ImageDraw.Draw(im), SIDE * s, TOP * s)
    if link:
        _logo_curve(d, s)
        if left == "dot" and right == "dot":   # pure brand mark: logo-exact dots, no separate mouth
            for cx in (EXL, EXR):
                d.ellipse(((cx - R_LOGO) * s, (EY - R_LOGO) * s, (cx + R_LOGO) * s, (EY + R_LOGO) * s), fill=255)
        else:
            _eye(d, left, EXL * s, EY * s, s, True); _eye(d, right, EXR * s, EY * s, s, False)
    else:
        _eye(d, left, EXL * s, EY * s, s, True)
        _eye(d, right, EXR * s, EY * s, s, False)
        _mouth(d, mouth, s)
    im = im.resize((W // SS, H // SS), Image.LANCZOS)
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(im)
    return out


def render(name, width):
    l, r, m, link = FACES.get(name.replace("rumi-", ""), FACES["happy"])
    return compose(l, r, m, link, width)


if __name__ == "__main__":
    import numpy as np
    logo = Image.open(Path.home() / ".claude/skills/rumi-brand/assets/rumi-mark-white-smile.png").convert("RGBA")
    mine = render("happy", 661).crop((int(SIDE * 661), int(TOP * 661), int(SIDE * 661) + 661, int(TOP * 661) + 255))
    a, b = np.array(logo)[:, :, 3] > 128, np.array(mine)[:, :, 3] > 128
    print(f"happy vs logo IoU = {(a & b).sum() / (a | b).sum():.3f}")
    names = list(FACES); cols, cell = 9, 240
    sheet = Image.new("RGBA", (cols * cell, -(-len(names) // cols) * cell), (0, 31, 63, 255))
    dr = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        x, y = (i % cols) * cell, (i // cols) * cell
        sheet.alpha_composite(render(n, 180), (x + 30, y + 70))
        dr.text((x + 30, y + 20), n, fill=(168, 199, 255, 255))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("faces-sheet.png")
    sheet.save(out); print("sheet ->", out)
