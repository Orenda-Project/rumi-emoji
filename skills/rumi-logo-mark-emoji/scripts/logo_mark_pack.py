#!/usr/bin/env python3
"""World of Rumi — logo-mark emoji pack (reference: reference/faces/world-of-rumi-logo-mark-2026-09-03.jpg).

The emoji IS the logo: two navy dots joined by the smile curve, no body, props hang off the mark.
Navy on transparent so it sits on cream/white Slack + WhatsApp backgrounds.

    python3 scripts/logo_mark_pack.py            # -> emoji-mark/512, emoji-mark/128, preview-mark.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

NAVY, BLUE, RED, CORAL, WHITE, CREAM = "#0B2545", "#2F6BB3", "#7A1F1F", "#E8746A", "#FFFFFF", "#F3F1EC"
SS, SIZE = 4, 512
M = 330                                  # mark width in a 512 canvas
OX, OY = (SIZE - M) / 2, 190             # mark origin (eye row at y = OY + EY*M)
R, EY, EXL, EXR, STROKE, BOTTOM = 0.095, 0.103, 0.10, 0.90, 0.023, 0.372   # from rumi_face.py (logo-measured)
OUT = Path(__import__("os").environ.get("RUMI_MARK_OUT", Path.cwd() / "emoji-mark"))


def P(x, y):                         # mark-units -> canvas px (supersampled)
    return ((OX + x * M) * SS, (OY + y * M) * SS)


def arc(x0, y0, x1, y1, bulge, n=48):
    return [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + bulge * 4 * t * (1 - t)) for t in (i / n for i in range(n + 1))]


def stroke(d, pts, w, fill=NAVY):
    d.line(pts, fill=fill, width=int(w), joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=fill)


def dot(d, cx, cy, r, fill=NAVY):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def logo_curve(d, fill=NAVY, lift=0.0):
    x0, x1, ay = 0.145, 0.855, 0.195
    k = (BOTTOM - lift - ay) / ((x1 - x0) / 2) ** 2
    pts = [P(x0 + (x1 - x0) * i / 48, BOTTOM - lift - k * ((x0 + (x1 - x0) * i / 48) - 0.5) ** 2) for i in range(49)]
    stroke(d, pts, STROKE * M * SS, fill)


def frown(d, fill=NAVY):
    hw = 0.20
    pts = [P(x, y) for x, y in arc(0.5 - hw, EY + 0.19, 0.5 + hw, EY + 0.19, -0.075)]
    stroke(d, pts, STROKE * M * SS, fill)


def tear(d, x, y, h=0.09, fill=BLUE):
    (cx, cy), hp = P(x, y), h * M * SS
    d.polygon([(cx, cy - hp), (cx - hp * 0.42, cy + hp * 0.15), (cx + hp * 0.42, cy + hp * 0.15)], fill=fill)
    dot(d, cx, cy + hp * 0.15, hp * 0.42, fill)


def eyes(d, fill=NAVY, lid=False):
    for x in (EXL, EXR):
        cx, cy = P(x, EY)
        dot(d, cx, cy, R * M * SS, fill)
        if lid:                                          # sleeping: top half sliced off
            d.rectangle((cx - R * M * SS - 2, cy - R * M * SS - 2, cx + R * M * SS + 2, cy), fill=(0, 0, 0, 0))


def mark(d):
    logo_curve(d); eyes(d)


# ----- props (all positioned in mark units) -----
def prop_tongue(d):
    (x, y), w, h = P(0.72, 0.30), 0.11 * M * SS, 0.15 * M * SS
    d.rounded_rectangle((x - w / 2, y - h * 0.15, x + w / 2, y + h), radius=w / 2, fill=CORAL)


def prop_santa(d):
    cx, cy = P(EXR, EY); r = R * M * SS * 1.3; cy -= r * 0.1
    top = (cx + r * 1.1, cy - r * 2.6)
    d.polygon([(cx - r * 1.05, cy - r * 0.45), (cx + r * 1.05, cy - r * 0.45), top], fill="#C8332B")
    stroke(d, [(cx - r * 1.05, cy - r * 0.45), (cx + r * 1.05, cy - r * 0.45)], r * 0.45, WHITE)
    stroke(d, [(cx - r * 1.05, cy - r * 0.45), (cx + r * 1.05, cy - r * 0.45)], r * 0.45 + 4 * SS, NAVY)  # outline
    stroke(d, [(cx - r * 1.05, cy - r * 0.45), (cx + r * 1.05, cy - r * 0.45)], r * 0.45, WHITE)
    dot(d, top[0], top[1], r * 0.28, NAVY); dot(d, top[0], top[1], r * 0.2, WHITE)


def prop_sparkle(d):
    cx, cy = P(EXR, EY); r = R * M * SS
    for ang, ln in ((-70, 1.0), (-30, 0.9), (10, 0.8)):
        import math
        a = math.radians(ang)
        p0 = (cx + r * 1.45 * math.cos(a), cy + r * 1.45 * math.sin(a))
        p1 = (cx + r * (1.45 + 0.55 * ln) * math.cos(a), cy + r * (1.45 + 0.55 * ln) * math.sin(a))
        stroke(d, [p0, p1], r * 0.16)


def prop_chef(d):
    cx, cy = P(EXR, EY); r = R * M * SS
    # hat: puffy top + band, white with navy outline
    band = (cx - r * 0.95, cy - r * 1.5, cx + r * 0.95, cy - r * 0.55)
    d.rounded_rectangle(band, radius=r * 0.15, fill=NAVY); d.rounded_rectangle(
        (band[0] + 3 * SS, band[1] + 3 * SS, band[2] - 3 * SS, band[3] - 3 * SS), radius=r * 0.12, fill=WHITE)
    for dx in (-0.75, 0, 0.75):
        dot(d, cx + dx * r, cy - r * 1.9, r * 0.6, NAVY); dot(d, cx + dx * r, cy - r * 1.9, r * 0.6 - 3 * SS, WHITE)
    d.rectangle((band[0] + 3 * SS, cy - r * 1.9, band[2] - 3 * SS, band[1] + 3 * SS), fill=WHITE)
    # whisk, leaning on the left dot
    lx, ly = P(EXR, EY)
    h0, h1 = (lx + r * 1.3, ly + r * 0.6), (lx + r * 2.1, ly - r * 1.3)
    stroke(d, [h0, h1], r * 0.18)
    for off in (-0.35, 0, 0.35):
        pts = arc(h1[0], h1[1], h1[0] + r * 1.0, h1[1] - r * 1.3, off * r * 1.4)
        stroke(d, pts, r * 0.11)


def prop_tie(d):
    cx, cy = P(0.5, BOTTOM); r = R * M * SS * 1.35
    d.polygon([(cx - r * 0.42, cy - r * 0.1), (cx + r * 0.42, cy - r * 0.1), (cx + r * 0.25, cy + r * 0.4), (cx - r * 0.25, cy + r * 0.4)], fill=NAVY)
    d.polygon([(cx - r * 0.25, cy + r * 0.4), (cx + r * 0.25, cy + r * 0.4), (cx + r * 0.5, cy + r * 1.7), (cx, cy + r * 2.1), (cx - r * 0.5, cy + r * 1.7)], fill=NAVY)
    # collar wings
    for sgn in (-1, 1):
        d.polygon([(cx + sgn * r * 0.45, cy - r * 0.35), (cx + sgn * r * 1.3, cy - r * 0.9), (cx + sgn * r * 1.15, cy + r * 0.05)], fill=WHITE)
        d.line([(cx + sgn * r * 0.45, cy - r * 0.35), (cx + sgn * r * 1.3, cy - r * 0.9), (cx + sgn * r * 1.15, cy + r * 0.05), (cx + sgn * r * 0.45, cy - r * 0.35)], fill=NAVY, width=int(r * 0.12), joint="curve")


def prop_thought(d):
    cx, cy = P(EXR, EY); r = R * M * SS * 1.25
    dot(d, cx + r * 0.85, cy - r * 1.35, r * 0.14); dot(d, cx + r * 1.25, cy - r * 1.8, r * 0.2)
    bx, by, bw, bh = cx + r * 1.9, cy - r * 2.45, r * 1.0, r * 0.75
    for (ox, oy, rr) in ((-0.55, 0.05, 0.5), (0, -0.25, 0.6), (0.55, 0.05, 0.5), (-0.3, 0.35, 0.45), (0.3, 0.35, 0.45)):
        dot(d, bx + ox * bw, by + oy * bh, rr * bh, NAVY)
    for (ox, oy, rr) in ((-0.55, 0.05, 0.5), (0, -0.25, 0.6), (0.55, 0.05, 0.5), (-0.3, 0.35, 0.45), (0.3, 0.35, 0.45)):
        dot(d, bx + ox * bw, by + oy * bh, rr * bh - 2.5 * SS, WHITE)


def prop_zzz(d):
    cx, cy = P(EXR, EY); r = R * M * SS
    for i, (dx, dy, sz) in enumerate(((0.4, -1.4, 0.55), (1.15, -2.0, 0.75), (2.0, -2.8, 1.0))):
        s = r * sz; x, y = cx + dx * r, cy + dy * r
        stroke(d, [(x - s / 2, y - s / 2), (x + s / 2, y - s / 2), (x - s / 2, y + s / 2), (x + s / 2, y + s / 2)], r * 0.14)


def prop_grin(d):
    logo_curve(d, lift=0.085)          # inner arc, shallower -> open smile outline


def face_happy(d): mark(d)
def face_tongue(d): mark(d); prop_tongue(d)
def face_santa(d): mark(d); prop_santa(d)
def face_sparkle(d): mark(d); prop_sparkle(d)
def face_sad(d): eyes(d); frown(d, BLUE); tear(d, EXR + 0.06, EY + 0.30)
def face_angry(d):
    eyes(d, RED); frown(d, RED); r = R * M * SS
    for x, sgn in ((EXL, 1), (EXR, -1)):
        cx, cy = P(x, EY)
        stroke(d, [(cx - sgn * r * 1.1, cy - r * 1.55), (cx + sgn * r * 1.1, cy - r * 1.05)], r * 0.36, RED)
def face_chef(d): mark(d); prop_chef(d)
def face_tie(d): mark(d); prop_tie(d)
def face_crying(d):
    eyes(d); frown(d)
    for x in (EXL - 0.07, EXL - 0.02, EXR + 0.02, EXR + 0.07):
        tear(d, x, EY + 0.28 + (0.05 if x in (EXL - 0.02, EXR + 0.02) else 0))
def face_thought(d): mark(d); prop_thought(d)
def face_sleeping(d): logo_curve(d); eyes(d, lid=True); prop_zzz(d)
def face_grin(d): mark(d); prop_grin(d)

PACK = {  # slack/whatsapp name -> drawer   (order = reference sheet, left->right, top->bottom)
    "rumi-mark": face_happy, "rumi-mark-tongue": face_tongue, "rumi-mark-santa": face_santa,
    "rumi-mark-sparkle": face_sparkle, "rumi-mark-sad": face_sad, "rumi-mark-angry": face_angry,
    "rumi-mark-chef": face_chef, "rumi-mark-tie": face_tie, "rumi-mark-crying": face_crying,
    "rumi-mark-thinking": face_thought, "rumi-mark-sleeping": face_sleeping, "rumi-mark-grin": face_grin,
}


def render(name):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    PACK[name](ImageDraw.Draw(im))
    return im.resize((SIZE, SIZE), Image.LANCZOS)


if __name__ == "__main__":
    for sub in ("512", "128"): (OUT / sub).mkdir(parents=True, exist_ok=True)
    cols, cell = 6, 260
    sheet = Image.new("RGBA", (cols * cell, -(-len(PACK) // cols) * cell + 40), CREAM)
    dr = ImageDraw.Draw(sheet)
    for i, name in enumerate(PACK):
        im = render(name)
        im.save(OUT / "512" / f"{name}.png"); im.resize((128, 128), Image.LANCZOS).save(OUT / "128" / f"{name}.png")
        x, y = (i % cols) * cell, (i // cols) * cell + 40
        sheet.alpha_composite(im.resize((cell - 40, cell - 40), Image.LANCZOS), (x + 20, y + 10))
        dr.text((x + 20, y + cell - 22), name, fill=NAVY)
    dr.text((20, 12), "THE WORLD OF RUMI - logo-mark pack", fill=NAVY)
    sheet.save(OUT.parent / "preview-mark.png")
    assert all((OUT / "512" / f"{n}.png").stat().st_size > 1000 for n in PACK)   # ponytail: the one check
    print(f"{len(PACK)} emoji -> {OUT}  preview -> preview-mark.png")
