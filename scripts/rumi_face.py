#!/usr/bin/env python3
"""Vector renderer of the Rumi logo mark (two dots joined by one smile curve) with per-emotion
variants. The neutral render reproduces rumi-mark-white-smile.png; every other expression is the
SAME mark with the dots reshaped and/or the connecting curve bent - the two ends always stay
attached to the eyes, like the logo. Vocabulary copied from the flat-vector robot pack (grids/).

    render(name, width) -> RGBA image (white on transparent), height = width * 255/661
    python3 scripts/rumi_face.py            -> writes a contact sheet + prints IoU vs the real logo
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw

# --- geometry measured from rumi-mark-white-smile.png (661x255), in units of width ---
R, EY, EXL, EXR, STROKE, BOTTOM = 0.095, 0.103, 0.10, 0.90, 0.023, 0.372
SS = 6  # supersample

FACES = {  # name: (left eye, right eye, mouth) - see EYES / MOUTHS
    "happy": ("dot", "dot", "smile"), "wink": ("dot", "wink", "smile"), "wave": ("closed", "closed", "laugh"),
    "thumbs-up": ("dot", "dot", "smile"), "heart-eyes": ("heart", "heart", "smile"), "laugh": ("squint", "squint", "laugh"),
    "thinking": ("lookup", "lookup", "smirk"), "sad": ("sad", "sad", "frown"), "celebrate": ("closed", "closed", "laugh"),
    "done": ("closed", "closed", "smile"), "working": ("dot", "dot", "flat"), "loading": ("lidded", "lidded", "flat"),
    "searching": ("big", "small", "smile"), "idea": ("big", "big", "laugh"), "writing": ("lookdown", "lookdown", "smile"),
    "error": ("x", "x", "flat"), "warning": ("worried", "worried", "o"), "blocked": ("lidded", "lidded", "flat"),
    "sleeping": ("sleep", "sleep", "smile"), "low-battery": ("lidded", "lidded", "frown"), "surprised": ("big", "big", "o"),
    "confused": ("big", "small", "wavy"), "shy": ("lookside", "lookside", "smile"), "crying": ("sad", "sad", "frown"),
    "crying-laughing": ("squint", "squint", "laugh"), "angry": ("angry", "angry", "frown"), "nervous": ("dot", "small", "wavy"),
    "smug": ("lidded", "lidded", "smirk"), "mind-blown": ("spiral", "spiral", "o"), "eye-roll": ("lookup", "lookup", "flat"),
    "facepalm": ("closed", "closed", "flat"), "cool": ("dot", "dot", "smile"), "starstruck": ("star", "star", "laugh"),
    "salute": ("dot", "wink", "smirk"), "shrug": ("dot", "dot", "wavy"), "peek": ("big", "big", "smile"),
    "teaching": ("dot", "dot", "smile"), "graduate": ("dot", "dot", "smile"), "clap": ("closed", "closed", "laugh"),
    "encourage": ("closed", "closed", "laugh"), "listening": ("dot", "dot", "smile"), "speaking": ("dot", "dot", "laugh"),
    "100": ("star", "star", "laugh"), "trophy": ("closed", "closed", "laugh"), "book": ("lookdown", "lookdown", "smile"),
    "thanks": ("closed", "closed", "smile"), "dance": ("closed", "closed", "laugh"), "heart": ("closed", "closed", "smile"),
    "reading": ("lookdown", "lookdown", "smile"), "charging": ("closed", "closed", "smile"), "hello": ("dot", "dot", "laugh"),
    "curious": ("big", "small", "smile"), "proud": ("lidded", "lidded", "laugh"), "high-five": ("dot", "dot", "laugh"),
}


def _stroke(d, pts, w, fill=255):
    d.line(pts, fill=fill, width=int(w), joint="curve")
    r = w / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def _eye(d, kind, cx, cy, r, s, left):
    """Draw one eye centred at (cx,cy) with radius r. s = px per width unit."""
    w = STROKE * s
    if kind in ("dot", "big", "small", "lidded", "sad", "angry", "lookup", "lookdown", "lookside"):
        rr = r * {"big": 1.2, "small": 0.7}.get(kind, 1.0)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255)
        if kind == "lidded":      # flat lid cutting the top third
            d.rectangle((cx - rr - 2, cy - rr - 2, cx + rr + 2, cy - rr * 0.25), fill=0)
        if kind in ("sad", "angry"):  # slanted lid: sad droops outward-up, angry inward-up
            sign = (1 if left else -1) * (1 if kind == "sad" else -1)
            poly = [(cx - rr - 2, cy - rr - 2), (cx + rr + 2, cy - rr - 2),
                    (cx + rr + 2, cy - rr * 0.3 - sign * rr * 0.5), (cx - rr - 2, cy - rr * 0.3 + sign * rr * 0.5)]
            d.polygon(poly, fill=0)
        if kind in ("lookup", "lookdown", "lookside"):  # ring with an offset pupil
            d.ellipse((cx - rr * 0.62, cy - rr * 0.62, cx + rr * 0.62, cy + rr * 0.62), fill=0)
            dx, dy = {"lookup": (rr * 0.15, -rr * 0.33), "lookdown": (0, rr * 0.33), "lookside": (rr * 0.36 * (1 if left else 1), 0)}[kind]
            d.ellipse((cx + dx - rr * 0.36, cy + dy - rr * 0.36, cx + dx + rr * 0.36, cy + dy + rr * 0.36), fill=255)
    elif kind == "closed":      # happy closed eye: an arch  ^
        _stroke(d, [(cx - r, cy + r * 0.4), (cx, cy - r * 0.5), (cx + r, cy + r * 0.4)], w)
    elif kind == "sleep":       # sleeping: a gentle downward arc
        _stroke(d, [(cx - r, cy - r * 0.1), (cx, cy + r * 0.5), (cx + r, cy - r * 0.1)], w)
    elif kind == "wink":
        _stroke(d, [(cx - r, cy + r * 0.2), (cx, cy - r * 0.2), (cx + r, cy + r * 0.2)], w)
    elif kind == "worried":
        _stroke(d, [(cx - r, cy + r * 0.3), (cx, cy - r * 0.4), (cx + r, cy + r * 0.3)], w)
        d.ellipse((cx - r * 0.55, cy + r * 0.1, cx + r * 0.55, cy + r * 1.2), fill=255)
    elif kind == "squint":      # >< laugh eyes
        _stroke(d, [(cx - r, cy - r * 0.7), (cx + r * 0.2 * (1 if left else -1), cy), (cx - r, cy + r * 0.7)] if left
                else [(cx + r, cy - r * 0.7), (cx - r * 0.2, cy), (cx + r, cy + r * 0.7)], w)
    elif kind == "x":
        _stroke(d, [(cx - r * 0.8, cy - r * 0.8), (cx + r * 0.8, cy + r * 0.8)], w)
        _stroke(d, [(cx - r * 0.8, cy + r * 0.8), (cx + r * 0.8, cy - r * 0.8)], w)
    elif kind == "heart":
        rr = r * 1.15
        d.ellipse((cx - rr, cy - rr * 0.9, cx, cy + rr * 0.1), fill=255)
        d.ellipse((cx, cy - rr * 0.9, cx + rr, cy + rr * 0.1), fill=255)
        d.polygon([(cx - rr * 0.98, cy - rr * 0.2), (cx + rr * 0.98, cy - rr * 0.2), (cx, cy + rr * 1.0)], fill=255)
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rad = r * 1.25 if i % 2 == 0 else r * 0.55
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        d.polygon(pts, fill=255)
    elif kind == "spiral":
        pts = [(cx + (r * 1.15 * t / 3) * math.cos(t * 3.4), cy + (r * 1.15 * t / 3) * math.sin(t * 3.4)) for t in [i / 16 for i in range(49)]]
        d.line(pts, fill=255, width=int(w * 0.85))


def _parabola(x0, x1, s, bottom, y_at_ends, n=48):
    k = (bottom - y_at_ends) / ((x1 - x0) / 2) ** 2
    xm = (x0 + x1) / 2
    return [((x0 + (x1 - x0) * i / n) * s, (bottom - k * ((x0 + (x1 - x0) * i / n) - xm) ** 2) * s) for i in range(n + 1)]


def _mouth(d, kind, s, W):
    w = STROKE * s
    # the connecting curve always leaves the dots at the logo's attach x (≈0.145) heading down
    ax0, ax1, ay = 0.145, 0.855, 0.195
    if kind == "smile":
        _stroke(d, _parabola(ax0, ax1, s, BOTTOM, ay), w)
    elif kind == "laugh":       # deeper curve + open mouth: the area under a chord, bounded below by the curve itself
        pts = _parabola(ax0, ax1, s, BOTTOM + 0.03, ay)
        _stroke(d, pts, w)
        chord_y = 0.285 * s
        inner = [(x, y) for x, y in pts if 0.30 * s <= x <= 0.70 * s]
        d.polygon([(inner[0][0], chord_y), *inner, (inner[-1][0], chord_y)], fill=255)
    elif kind == "smirk":       # asymmetric: bottom shifted right, right side flatter
        pts = _parabola(ax0, ax1, s, BOTTOM - 0.02, ay)
        pts = [(x, y - 0.06 * s * ((x / s - 0.5) / 0.36) ** 1 if x / s > 0.5 else y) for x, y in pts]
        _stroke(d, pts, w)
    else:
        # "sad-family": arms come down from the dots to y=0.30, then a centre segment carries the expression
        yl = 0.305
        left = [(ax0 * s, ay * s), (0.30 * s, yl * s)]
        right = [(0.70 * s, yl * s), (ax1 * s, ay * s)]
        if kind == "flat":
            mid = [(0.30 * s, yl * s), (0.70 * s, yl * s)]
        elif kind == "frown":
            mid = [(x * s, (yl - 0.075 * (1 - ((x - 0.5) / 0.2) ** 2)) * s) for x in [0.30 + 0.4 * i / 24 for i in range(25)]]
        elif kind == "wavy":
            mid = [(x * s, (yl + 0.03 * math.sin((x - 0.30) / 0.4 * 2 * math.pi)) * s) for x in [0.30 + 0.4 * i / 32 for i in range(33)]]
        elif kind == "o":
            mid = None
            _stroke(d, left + [(0.40 * s, yl * s)], w); _stroke(d, [(0.60 * s, yl * s)] + right, w)
            rr = 0.10 * s
            d.ellipse((0.5 * s - rr, yl * s - rr, 0.5 * s + rr, yl * s + rr), outline=255, width=int(w))
        if mid:
            _stroke(d, left + mid + right, w)


def render(name, width):
    kind = FACES.get(name.replace("rumi-", ""), FACES["happy"])
    s = width * SS
    W, H = int(661 / 661 * s), int(255 / 661 * s) + int(0.12 * s)  # a little headroom for laugh/hearts
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    _mouth(d, kind[2], s, W)
    _eye(d, kind[0], EXL * s, EY * s, R * s, s, True)
    _eye(d, kind[1], EXR * s, EY * s, R * s, s, False)
    im = im.resize((W // SS, H // SS), Image.LANCZOS)
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(im)
    return out


if __name__ == "__main__":
    import numpy as np
    logo = Image.open(Path.home() / ".claude/skills/rumi-brand/assets/rumi-mark-white-smile.png").convert("RGBA")
    mine = render("happy", 661).crop((0, 0, 661, 255))
    a, b = np.array(logo)[:, :, 3] > 128, np.array(mine)[:, :, 3] > 128
    print(f"neutral vs logo IoU = {(a & b).sum() / (a | b).sum():.3f}")
    names = list(FACES)
    cols = 9; cell = 240
    sheet = Image.new("RGBA", (cols * cell, -(-len(names) // cols) * cell), (0, 31, 63, 255))
    for i, n in enumerate(names):
        f = render(n, 200)
        sheet.alpha_composite(f, ((i % cols) * cell + 20, (i // cols) * cell + 60))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("faces-sheet.png")
    sheet.save(out); print("sheet ->", out)
