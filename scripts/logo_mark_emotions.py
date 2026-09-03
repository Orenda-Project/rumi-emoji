#!/usr/bin/env python3
"""World of Rumi — extended emotions in the logo-mark style (minimal: dots + curve + at most one prop).

    python3 scripts/logo_mark_emotions.py     # -> emoji-mark-emotions/512, /128, preview-mark-emotions.png
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
from logo_mark_pack import (prop_tongue as LP_tongue, P, arc, stroke, dot, logo_curve, frown, tear, eyes, mark, prop_zzz,
                            NAVY, BLUE, RED, CORAL, WHITE, CREAM, SS, SIZE, M, R, EY, EXL, EXR, STROKE, BOTTOM)

OUT = Path(__import__("os").environ.get("RUMI_MARK_OUT", Path.cwd() / "emoji-mark-emotions"))
r_ = lambda: R * M * SS
W_ = lambda: STROKE * M * SS
PINK = "#F3A6B8"


# ---------- eyes ----------
def eye_big(d, x):   cx, cy = P(x, EY); dot(d, cx, cy, r_() * 1.35)
def eye_small(d, x): cx, cy = P(x, EY); dot(d, cx, cy, r_() * 0.6)
def eye_lid(d, x, tilt=0):
    cx, cy = P(x, EY); r = r_(); dot(d, cx, cy, r)
    d.polygon([(cx - r - 2, cy - r - 2), (cx + r + 2, cy - r - 2), (cx + r + 2, cy - r * 0.1 + tilt * r), (cx - r - 2, cy - r * 0.1 - tilt * r)], fill=(0, 0, 0, 0))
def eye_x(d, x):
    cx, cy = P(x, EY); r = r_() * 0.9
    stroke(d, [(cx - r, cy - r), (cx + r, cy + r)], W_() * 1.3); stroke(d, [(cx + r, cy - r), (cx - r, cy + r)], W_() * 1.3)
def eye_arch(d, x):                                         # ^ happy-closed
    cx, cy = P(x, EY); r = r_()
    stroke(d, [P(*q) for q in arc(x - 0.095, EY + 0.02, x + 0.095, EY + 0.02, -0.075)], W_() * 1.3)
def eye_closed(d, x):                                       # ︶ resting line
    stroke(d, [P(*q) for q in arc(x - 0.09, EY, x + 0.09, EY, 0.05)], W_() * 1.3)
def eye_heart(d, x, fill=CORAL):
    cx, cy = P(x, EY); r = r_() * 1.25
    dot(d, cx - r * 0.45, cy - r * 0.3, r * 0.55, fill); dot(d, cx + r * 0.45, cy - r * 0.3, r * 0.55, fill)
    d.polygon([(cx - r * 0.98, cy - r * 0.1), (cx + r * 0.98, cy - r * 0.1), (cx, cy + r * 0.95)], fill=fill)
def eye_star(d, x):
    cx, cy = P(x, EY); r = r_() * 1.4
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(math.radians(-90 + 36 * i)),
            cy + (r if i % 2 == 0 else r * 0.45) * math.sin(math.radians(-90 + 36 * i))) for i in range(10)]
    d.polygon(pts, fill=NAVY)
def eye_spiral(d, x):
    cx, cy = P(x, EY); r = r_()
    pts = [(cx + r * (t / 3.5) * math.cos(t), cy + r * (t / 3.5) * math.sin(t)) for t in [i * 0.15 for i in range(70)]]
    d.line(pts, fill=NAVY, width=int(W_() * 0.9), joint="curve")
def eye_look(d, x, dx=0.45, dy=0):
    cx, cy = P(x, EY); r = r_()
    dot(d, cx, cy, r); dot(d, cx, cy, r - W_() * 0.9, (0, 0, 0, 0)); dot(d, cx + dx * r, cy + dy * r, r * 0.42)
def eye_ring(d, x):                                         # hollow ring (blank stare)
    cx, cy = P(x, EY); r = r_(); dot(d, cx, cy, r); dot(d, cx, cy, r - W_() * 0.9, (0, 0, 0, 0))


def both(fn, **k): fn(EXL, **k); fn(EXR, **k)


# ---------- mouths ----------
def m_flat(d, hw=0.16):     stroke(d, [P(0.5 - hw, EY + 0.22), P(0.5 + hw, EY + 0.22)], W_())
def m_o(d, rr=0.045):       cx, cy = P(0.5, EY + 0.22); dot(d, cx, cy, rr * M * SS)
def m_open(d, hw=0.16):     # filled D grin, flat top
    cx, cy = P(0.5, EY + 0.17); h = hw * M * SS; d.chord((cx - h, cy - h, cx + h, cy + h), 0, 180, fill=NAVY)
def m_openfrown(d, hw=0.09):
    cx, cy = P(0.5, EY + 0.24); h = hw * M * SS; d.chord((cx - h, cy - h, cx + h, cy + h), 180, 360, fill=NAVY)
def m_zigzag(d):
    hw, amp, n = 0.17, 0.03, 4
    pts = [P(0.5 - hw + 2 * hw * i / (2 * n), EY + 0.22 + (amp if i % 2 else -amp)) for i in range(2 * n + 1)]
    d.line(pts, fill=NAVY, width=int(W_()), joint="curve"); stroke(d, pts[:1], W_()); stroke(d, pts[-1:], W_())
def m_smirk(d):             stroke(d, [P(*q) for q in arc(0.36, EY + 0.24, 0.66, EY + 0.17, 0.06)], W_())
def m_wavy(d):
    pts = [P(0.34 + 0.32 * t, EY + 0.22 + 0.03 * math.sin(t * math.pi * 3)) for t in [i / 40 for i in range(41)]]
    stroke(d, pts, W_())
def m_smile_small(d):       stroke(d, [P(*q) for q in arc(0.40, EY + 0.19, 0.60, EY + 0.19, 0.06)], W_())
def m_teeth(d):             # grin with a tooth line
    m_open(d); cx, cy = P(0.5, EY + 0.17); h = 0.16 * M * SS
    d.rectangle((cx - h * 0.95, cy, cx + h * 0.95, cy + h * 0.3), fill=WHITE)
def m_tongue_side(d):
    m_open(d, 0.13); (x, y), w, h = P(0.56, 0.27), 0.08 * M * SS, 0.10 * M * SS
    d.rounded_rectangle((x - w / 2, y, x + w / 2, y + h), radius=w / 2, fill=CORAL)


def curve_pts(lift=0.0, n=48):                 # the logo curve as points (same formula as logo_mark_pack.logo_curve)
    x0, x1, ay = 0.145, 0.855, 0.195
    k = (BOTTOM - lift - ay) / ((x1 - x0) / 2) ** 2
    return [P(x0 + (x1 - x0) * i / n, BOTTOM - lift - k * ((x0 + (x1 - x0) * i / n) - 0.5) ** 2) for i in range(n + 1)]
def m_biggrin(d, drop=0.16, teeth=False):      # big grin: lens between the logo curve and a deeper eye-to-eye arc
    top, bot = curve_pts(), curve_pts(lift=-drop)
    d.polygon(top + bot[::-1], fill=NAVY)
    stroke(d, bot, STROKE * M * SS)
    if teeth:
        cx, cy = P(0.5, BOTTOM + drop * 0.45); hw = 0.17 * M * SS
        d.rectangle((cx - hw, cy - 0.02 * M * SS, cx + hw, cy + 0.02 * M * SS), fill=WHITE)


# ---------- props (max one per face, off to a side) ----------
def near_right(dx=1.6, dy=-1.6):
    cx, cy = P(EXR, EY); r = r_(); return cx + dx * r, cy + dy * r
def text_glyph(d, s, pos, size=1.0, fill=NAVY):            # ?, !, ... drawn as strokes, no fonts
    x, y = pos; r = r_() * size; w = W_() * 1.2
    if s == "?":
        stroke(d, [(x + 0.5 * r * math.cos(math.radians(a)), y - r * 0.6 + 0.5 * r * math.sin(math.radians(a))) for a in range(-180, 60, 8)], w)
        stroke(d, [(x + 0.5 * r * math.cos(math.radians(60)), y - r * 0.6 + 0.5 * r * math.sin(math.radians(60))), (x, y + r * 0.35)], w)
        dot(d, x, y + r * 0.95, w * 0.7, fill)
    elif s == "!":
        stroke(d, [(x, y - r), (x, y + r * 0.35)], w); dot(d, x, y + r * 0.95, w * 0.7, fill)
    elif s == "...":
        for i in (-1, 0, 1): dot(d, x + i * r * 0.55, y, w * 0.6, fill)
def p_sweat(d):    tear(d, EXR + 0.16, EY - 0.02, 0.08)
def p_blush(d):
    for x in (EXL, EXR):
        cx, cy = P(x, EY + 0.16); d.ellipse((cx - r_() * 0.7, cy - r_() * 0.3, cx + r_() * 0.7, cy + r_() * 0.3), fill=PINK)
def p_hearts(d):
    for (x, y, s) in ((EXR + 0.14, EY - 0.16, 0.55), (EXR + 0.26, EY - 0.30, 0.8)):
        cx, cy = P(x, y); r = r_() * s
        dot(d, cx - r * 0.45, cy - r * 0.3, r * 0.5, CORAL); dot(d, cx + r * 0.45, cy - r * 0.3, r * 0.5, CORAL)
        d.polygon([(cx - r * 0.92, cy - r * 0.15), (cx + r * 0.92, cy - r * 0.15), (cx, cy + r * 0.85)], fill=CORAL)
def p_sparkles(d):
    for (x, y, s) in ((EXR + 0.15, EY - 0.18, 0.5), (EXR + 0.28, EY - 0.04, 0.35), (EXL - 0.16, EY - 0.14, 0.4)):
        cx, cy = P(x, y); r = r_() * s
        d.polygon([(cx, cy - r), (cx + r * 0.25, cy - r * 0.25), (cx + r, cy), (cx + r * 0.25, cy + r * 0.25), (cx, cy + r), (cx - r * 0.25, cy + r * 0.25), (cx - r, cy), (cx - r * 0.25, cy - r * 0.25)], fill=NAVY)
def p_anger(d):    # 💢 mark: four short spokes
    cx, cy = near_right(1.7, -1.9); r = r_() * 0.7
    for a in (30, 100, 170, 240): stroke(d, [(cx + r * 0.4 * math.cos(math.radians(a)), cy + r * 0.4 * math.sin(math.radians(a))), (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))], W_() * 1.1, RED)
def p_bulb(d):
    cx, cy = near_right(1.6, -2.4); r = r_() * 0.8
    dot(d, cx, cy, r); dot(d, cx, cy, r - W_() * 0.8, (0, 0, 0, 0))
    d.rectangle((cx - r * 0.35, cy + r * 0.8, cx + r * 0.35, cy + r * 1.35), fill=NAVY)
    for a in (-135, -90, -45): stroke(d, [(cx + r * 1.3 * math.cos(math.radians(a)), cy + r * 1.3 * math.sin(math.radians(a))), (cx + r * 1.7 * math.cos(math.radians(a)), cy + r * 1.7 * math.sin(math.radians(a)))], W_() * 0.8)
def p_check(d):
    cx, cy = near_right(1.6, -1.6); r = r_() * 0.8
    stroke(d, [(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.8)], W_() * 1.4, BLUE)
def p_spinner(d):
    cx, cy = near_right(1.7, -1.8); r = r_() * 0.75
    stroke(d, [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-90, 200, 8)], W_() * 1.1)
    d.polygon([(cx + r * 0.6, cy - r * 1.35), (cx + r * 1.4, cy - r * 0.9), (cx + r * 0.55, cy - r * 0.45)], fill=NAVY)
def p_hourglass(d):
    cx, cy = near_right(1.8, -1.9); r = r_() * 0.8
    d.line([(cx - r * 0.7, cy - r), (cx + r * 0.7, cy - r), (cx - r * 0.7, cy + r), (cx + r * 0.7, cy + r), (cx - r * 0.7, cy - r)], fill=NAVY, width=int(W_() * 0.9), joint="curve")
    d.polygon([(cx - r * 0.35, cy + r * 0.55), (cx + r * 0.35, cy + r * 0.55), (cx, cy + r * 0.05)], fill=NAVY)
def p_glasses(d):
    for x in (EXL, EXR):
        cx, cy = P(x, EY); r = r_() * 1.55; dot(d, cx, cy, r); dot(d, cx, cy, r - W_() * 0.9, (0, 0, 0, 0)); dot(d, cx, cy, r_())
    stroke(d, [P(EXL + 0.15, EY), P(EXR - 0.15, EY)], W_() * 0.9)
def p_shades(d):
    for x in (EXL, EXR):
        cx, cy = P(x, EY); r = r_() * 1.45
        d.rounded_rectangle((cx - r, cy - r * 0.75, cx + r, cy + r * 0.6), radius=r * 0.4, fill=NAVY)
    stroke(d, [P(EXL + 0.14, EY - 0.03), P(EXR - 0.14, EY - 0.03)], W_())
def p_halo(d):
    cx, cy = P(0.5, EY - 0.22); rx, ry = 0.28 * M * SS, 0.07 * M * SS
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=NAVY, width=int(W_() * 0.9))
def p_horns(d):
    for x, sgn in ((EXL, -1), (EXR, 1)):
        cx, cy = P(x, EY); r = r_()
        d.polygon([(cx + sgn * r * 0.2, cy - r * 0.8), (cx + sgn * r * 1.0, cy - r * 0.6), (cx + sgn * r * 0.8, cy - r * 2.0)], fill=RED)
def p_party(d):
    cx, cy = P(EXR, EY); r = r_()
    d.polygon([(cx - r * 0.95, cy - r * 0.5), (cx + r * 0.95, cy - r * 0.5), (cx + r * 0.3, cy - r * 2.7)], fill=BLUE)
    for (dx, dy) in ((-2.2, -2.0), (-1.4, -2.9), (1.6, -3.0), (2.4, -1.8)): dot(d, cx + dx * r, cy + dy * r, r * 0.16, CORAL)
def p_headphones(d):
    stroke(d, [P(*q) for q in arc(EXL - 0.02, EY - 0.05, EXR + 0.02, EY - 0.05, -0.24)], W_() * 1.1)
    for x in (EXL - 0.02, EXR + 0.02):
        cx, cy = P(x, EY - 0.04); d.rounded_rectangle((cx - r_() * 0.45, cy - r_() * 0.8, cx + r_() * 0.45, cy + r_() * 0.4), radius=r_() * 0.3, fill=NAVY)
def p_coffee(d):
    cx, cy = P(EXR + 0.08, EY + 0.24); r = r_() * 1.1
    d.rounded_rectangle((cx - r, cy - r * 0.9, cx + r * 0.8, cy + r * 0.9), radius=r * 0.2, fill=NAVY)
    d.ellipse((cx + r * 0.5, cy - r * 0.5, cx + r * 1.4, cy + r * 0.4), outline=NAVY, width=int(W_() * 0.8))
    for i in (-0.4, 0.2): stroke(d, [(cx + i * r, cy - r * 1.9), (cx + i * r + r * 0.15, cy - r * 1.3)], W_() * 0.6)
def p_music(d):
    cx, cy = near_right(1.8, -2.0); r = r_() * 0.8
    dot(d, cx, cy + r * 0.6, r * 0.45); stroke(d, [(cx + r * 0.4, cy + r * 0.6), (cx + r * 0.4, cy - r * 1.2)], W_() * 0.9)
    stroke(d, [(cx + r * 0.4, cy - r * 1.2), (cx + r * 1.3, cy - r * 0.9)], W_() * 1.0)
def p_cloud(d):
    cx, cy = P(0.5, EY - 0.30); r = r_() * 0.75
    for (ox, oy, s) in ((-1.2, 0.2, 0.75), (-0.4, -0.3, 1.0), (0.5, -0.2, 0.9), (1.2, 0.25, 0.7)): dot(d, cx + ox * r, cy + oy * r, s * r, BLUE)
    d.rectangle((cx - r * 1.2, cy + r * 0.2, cx + r * 1.2, cy + r * 0.9), fill=BLUE)
    for i in (-0.8, 0, 0.8): stroke(d, [(cx + i * r, cy + r * 1.4), (cx + i * r - r * 0.15, cy + r * 2.0)], W_() * 0.6, BLUE)
def p_burst(d):
    for x in (EXL, EXR):
        cx, cy = P(x, EY); r = r_()
        for a in (-150, -110, -70, -30) if x == EXL else (-150, -110, -70, -30):
            stroke(d, [(cx + r * 1.6 * math.cos(math.radians(a)), cy + r * 1.6 * math.sin(math.radians(a))), (cx + r * 2.1 * math.cos(math.radians(a)), cy + r * 2.1 * math.sin(math.radians(a)))], W_() * 0.8)
def p_thermo(d):
    cx, cy = near_right(1.9, -1.4); r = r_() * 0.9
    d.rounded_rectangle((cx - r * 0.3, cy - r * 2.0, cx + r * 0.3, cy + r * 0.5), radius=r * 0.3, fill=NAVY); dot(d, cx, cy + r * 0.75, r * 0.6, RED)
def p_mask(d):
    cx, cy = P(0.5, EY + 0.20); w, h = 0.30 * M * SS, 0.11 * M * SS
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), radius=h * 0.5, fill=BLUE)
    for sgn in (-1, 1): stroke(d, [(cx + sgn * w, cy - h * 0.5), (cx + sgn * (w + r_() * 0.9), cy - h * 1.2)], W_() * 0.7, BLUE)
def p_zip(d):
    m_flat(d, 0.18); cx, cy = P(0.5, EY + 0.22)
    for i in range(-3, 4): stroke(d, [(cx + i * r_() * 0.5, cy - W_() * 0.9), (cx + i * r_() * 0.5, cy + W_() * 0.9)], W_() * 0.55)
def p_tear_l(d):   tear(d, EXL - 0.06, EY + 0.30)
def p_moon(d):
    cx, cy = near_right(1.9, -2.2); r = r_() * 0.75
    dot(d, cx, cy, r); dot(d, cx + r * 0.45, cy - r * 0.3, r * 0.85, (0, 0, 0, 0))


# ---------- the emotions ----------
def face(eyes_fn, mouth_fn=None, prop=None, link=False):
    def draw(d):
        if link: logo_curve(d)
        eyes_fn(d)
        if mouth_fn: mouth_fn(d)
        if prop: prop(d)
    return draw

E = lambda fn, **k: (lambda d: (fn(d, EXL, **k), fn(d, EXR, **k)))
DOTS = lambda d: eyes(d)

EMOTIONS = {
    # calm / positive
    "neutral":      face(DOTS, m_flat),
    "content":      face(DOTS, m_smile_small),
    "laugh":        face(E(eye_arch), m_open),
    "lol":          face(DOTS, m_biggrin, None, link=True),
    "wink":         face(lambda d: (dot(d, *P(EXL, EY), r_()), eye_arch(d, EXR)), None, None, link=True),
    "blush":        face(DOTS, None, p_blush, link=True),
    "shy":          face(E(eye_small), m_smile_small, p_blush),
    "proud":        face(E(eye_lid), None, p_sparkles, link=True),
    "smug":         face(E(eye_lid), m_smirk),
    "cool":         face(lambda d: None, None, p_shades, link=True),
    "love":         face(E(eye_heart), None, None, link=True),
    "in-love":      face(DOTS, None, p_hearts, link=True),
    "starstruck":   face(E(eye_star), m_open),
    "party":        face(E(eye_arch), m_open, p_party),
    "angel":        face(DOTS, None, p_halo, link=True),
    "devil":        face(E(eye_lid), m_smirk, p_horns),
    "cheeky":       face(lambda d: (dot(d, *P(EXL, EY), r_()), eye_arch(d, EXR)), LP_tongue, None, link=True),
    "sparkle-eyes": face(E(eye_ring), None, p_sparkles, link=True),
    # surprise / thinking
    "surprised":    face(E(eye_big), m_o),
    "shocked":      face(E(eye_big), m_open, None),
    "mind-blown":   face(E(eye_big), m_open, p_burst),
    "confused":     face(DOTS, m_zigzag, lambda d: text_glyph(d, "?", near_right(1.7, -1.9), 1.1)),
    "skeptical":    face(lambda d: (eye_lid(d, EXL), dot(d, *P(EXR, EY), r_())), m_flat),
    "suspicious":   face(E(eye_lid, tilt=0.3), m_flat),
    "hmm":          face(DOTS, m_flat, lambda d: text_glyph(d, "...", near_right(2.0, -1.4), 1.0)),
    "idea":         face(E(eye_big), m_o, p_bulb),
    "curious":      face(DOTS, m_smile_small, lambda d: text_glyph(d, "?", near_right(1.7, -1.9), 1.1)),
    "blank":        face(E(eye_ring), m_flat),
    "alert":        face(E(eye_big), m_flat, lambda d: text_glyph(d, "!", near_right(1.6, -1.9), 1.2)),
    # negative
    "worried":      face(DOTS, m_openfrown, p_sweat),
    "nervous":      face(DOTS, m_zigzag, p_sweat),
    "scared":       face(E(eye_big), m_wavy, p_sweat),
    "disappointed": face(E(eye_lid), lambda d: frown(d)),
    "annoyed":      face(E(eye_lid), m_flat, p_anger),
    "furious":      face(E(eye_lid, tilt=-0.5), m_openfrown, p_anger),
    "grumpy":       face(E(eye_lid, tilt=-0.4), lambda d: frown(d)),
    "pleading":     face(E(eye_big), m_openfrown, p_tear_l),
    "heartbroken":  face(DOTS, lambda d: frown(d), p_cloud),
    "bored":        face(E(eye_lid), m_flat),
    "tired":        face(E(eye_lid), m_wavy, p_moon),
    "yawn":         face(E(eye_closed), lambda d: m_open(d, 0.12)),
    "dead":         face(E(eye_x)),
    "dizzy":        face(E(eye_spiral), m_wavy),
    "sick":         face(E(eye_closed), m_wavy, p_thermo),
    "masked":       face(DOTS, None, p_mask),
    "speechless":   face(DOTS, None, lambda d: text_glyph(d, "...", P(0.5, EY + 0.22), 1.0)),
    "zipped":       face(DOTS, None, p_zip),
    # work states
    "working":      face(DOTS, m_flat, p_glasses),
    "reading":      face(E(eye_look, dx=0, dy=0.45), m_flat, p_glasses),
    "done":         face(E(eye_arch), None, p_check, link=True),
    "loading":      face(DOTS, m_flat, p_spinner),
    "waiting":      face(DOTS, m_flat, p_hourglass),
    "error":        face(E(eye_x), m_flat, lambda d: text_glyph(d, "!", near_right(1.7, -1.9), 1.2, RED)),
    "focus":        face(E(eye_small), m_flat),
    "coffee":       face(E(eye_lid), None, p_coffee, link=True),
    "vibing":       face(E(eye_closed), None, p_headphones, link=True),
    "singing":      face(E(eye_closed), lambda d: m_open(d, 0.11), p_music),
    "sleepy":       face(E(eye_lid), m_o, p_moon),
}


def render(name):
    im = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    EMOTIONS[name](ImageDraw.Draw(im))
    return im.resize((SIZE, SIZE), Image.LANCZOS)


if __name__ == "__main__":
    for sub in ("512", "128"): (OUT / sub).mkdir(parents=True, exist_ok=True)
    cols, cell = 8, 220
    sheet = Image.new("RGBA", (cols * cell, -(-len(EMOTIONS) // cols) * cell + 40), CREAM)
    dr = ImageDraw.Draw(sheet)
    for i, name in enumerate(EMOTIONS):
        im = render(name)
        im.save(OUT / "512" / f"rumi-mark-{name}.png"); im.resize((128, 128), Image.LANCZOS).save(OUT / "128" / f"rumi-mark-{name}.png")
        x, y = (i % cols) * cell, (i // cols) * cell + 40
        sheet.alpha_composite(im.resize((cell - 30, cell - 30), Image.LANCZOS), (x + 15, y + 5))
        dr.text((x + 15, y + cell - 18), name, fill=NAVY)
    dr.text((20, 12), f"THE WORLD OF RUMI - {len(EMOTIONS)} emotions, logo-mark style", fill=NAVY)
    sheet.save(OUT.parent / "preview-mark-emotions.png")
    assert all((OUT / "512" / f"rumi-mark-{n}.png").stat().st_size > 800 for n in EMOTIONS)
    print(f"{len(EMOTIONS)} emotions -> {OUT}  preview -> preview-mark-emotions.png")
