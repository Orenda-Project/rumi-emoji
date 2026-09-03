#!/usr/bin/env python3
"""One mark, many moods: a 20 s showreel for the README (Lottie + GIF + WebP).

usage: python3 scripts/make_showreel.py   -> lottie-mark/showreel.json, showreel.gif, showreel.webp
Sequence (each beat ~1.5 s, morph transitions): happy -> wink -> laugh -> love -> surprised -> confused ->
sad -> angry -> dizzy -> sleepy -> idea -> done -> happy.
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rumi_mark_rig import *
from make_lottie_mark import glyph_q, glyph_bang, checkmark as _ck, bulb as _bulb, sweat, anger_mark as _anger, hearts_float as _hearts, near_right
import make_lottie_mark as MK

OUT = pathlib.Path(__file__).resolve().parent.parent / "lottie-mark"
BEAT = 1500
beats = [  # (name, eyes, mouth, prop-fn)
    ("happy", "dot", "link", None), ("wink", ("dot", "arch"), "link", "sparkle"), ("laugh", "arch", "open", None),
    ("love", "heart", "link", "hearts"), ("surprised", "big", "o", None), ("confused", "dot", "zigzag", "q"),
    ("sad", "lid", "frown", "tear"), ("angry", "lid", "openfrown", "anger"), ("dizzy", "spiral", "wavy", None),
    ("sleepy", "lid", "o", "moon"), ("idea", "big", "o", "bulb"), ("done", "arch", "link", "check"),
]
total = BEAT * len(beats) + 1000
f = Face(total / 1000)
f.breathe(3, 3000)
for k in range(1, int(total / 3000) + 1): pass
p = f.pos  # breathe across the whole reel
p.add_keyframe(0, V(0, 0), SOFT)
for k in range(1, int(total // 1500) + 1): p.add_keyframe(ms(k * 1500), V(0, -3 if k % 2 else 0), SOFT)

def at(t0, fn):   # run a make_lottie_mark prop with its IN/OUTT window shifted to this beat
    MK.IN, MK.OUTT = t0 + 150, t0 + BEAT - 250; fn()

for i, (name, eyes, mouth, prop) in enumerate(beats):
    t0 = i * BEAT + 600
    if i == 0:
        f.blink(300)
    else:
        l, r = eyes if isinstance(eyes, tuple) else (eyes, eyes)
        f.eyes(l, t0, 130, "l"); f.eyes(r, t0 + 60, 130, "r"); f.mouth.set(mouth, t0, 150)
    if prop == "sparkle":
        g = f.prop(); c = P(EXR + .2, EY - .12)
        for a in (-60, -25, 10): line(g, (c.x, c.y), (c.x + 22 * math.cos(math.radians(a)), c.y + 22 * math.sin(math.radians(a))), NAVY, SW * .6)
        anchor(g, (c.x, c.y)); pop(g, t0 + 200, 160, 1.2, out_t=t0 + 900, out_dur=150)
    elif prop == "hearts": at(t0, lambda: _hearts(f, MK.IN + 100))
    elif prop == "q": at(t0, lambda: (lambda g: (glyph_q(g, near_right(1.7, -1.9)), pop(g, MK.IN + 100, 240, 1.15, out_t=MK.OUTT)))(f.prop()))
    elif prop == "tear": at(t0, lambda: MK.tear_fall(f, EXR + .06, EY + .30, MK.IN + 100, U(.09)))
    elif prop == "anger": at(t0, lambda: _anger(f, MK.IN + 100))
    elif prop == "bulb": at(t0, lambda: _bulb(f, MK.IN + 100))
    elif prop == "check": at(t0, lambda: _ck(f, MK.IN + 100))
    if name == "dizzy":
        for e, sgn in ((f.eyeL, 1), (f.eyeR, -1)): rr = e.spiral.transform.rotation; rr.add_keyframe(ms(t0), 0, LIN); rr.add_keyframe(ms(t0 + BEAT), 360 * sgn, LIN)
        for j, t in enumerate(range(t0, t0 + BEAT + 1, 250)): f.mouth.wavy_key(t, j * math.pi / 2)
    if name == "angry": shake(f.pos, t0 + 300, t0 + 900, 3.5, step=50, seed=6)
    if name == "laugh":
        for t in range(t0 + 250, t0 + 1100, 300): p.add_keyframe(ms(t), V(0, 0), SOFT); p.add_keyframe(ms(t + 150), V(0, -6), SOFT)
    if name == "sleepy":  # zZZ
        for k2, (sz, dx, tt) in enumerate(((5, 0, 200), (7, 9, 600), (10, 20, 1000))):
            g = f.prop(); c = near_right(1.4, -1.2); x = c[0] + dx
            polyline(g, [(x, c[1] - sz), (x + sz, c[1] - sz), (x, c[1]), (x + sz, c[1])], NAVY, 2 + k2 * .8); anchor(g, (x + sz / 2, c[1] - sz / 2))
            pos = g.transform.position; pos.add_keyframe(0, V(x + sz / 2, c[1] - sz / 2), HOLD); pos.add_keyframe(ms(t0 + tt), V(x + sz / 2, c[1] - sz / 2), DECEL); pos.add_keyframe(ms(t0 + tt + 900), V(x + sz / 2 + 4, c[1] - sz / 2 - 30), STD)
            fade(g, [(t0 + tt, 0), (t0 + tt + 150, 100), (t0 + tt + 700, 100), (t0 + tt + 900, 0)])
# back to rest at the end so the loop closes
tE = len(beats) * BEAT + 400
f.eyes("dot", tE, 130); f.mouth.set("link", tE, 150)
out = f.save(OUT / "showreel.json"); print("lottie", out.stat().st_size // 1024, "KB", total, "ms")

# ---- render GIF / WebP from the exported Lottie
from lottie.parsers.tgs import parse_tgs
from lottie.exporters.cairo import export_png
from PIL import Image
an = parse_tgs(str(out)); frames = []; step = 2   # 15 fps
S = pathlib.Path("/tmp/claude-1000/-home-oye-Documents-free-work-personal-agent-v2/86f75a27-a4bc-4707-a86e-5f7be5d06b93/scratchpad") if pathlib.Path("/tmp/claude-1000").exists() else pathlib.Path("/tmp")
for fr in range(0, int(an.out_point), step):
    with open(S / "_sr.png", "wb") as fh: export_png(an, fh, frame=fr)
    im = Image.open(S / "_sr.png").convert("RGBA").crop((56, 96, 456, 356))       # 400x260, tight to mark + props
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); frames.append(bg.convert("RGB").resize((640, 416), Image.LANCZOS))   # white: blends with GitHub light
frames[0].save(OUT / "showreel.gif", save_all=True, append_images=frames[1:], duration=int(1000 / 15), loop=0, optimize=True)
frames[0].save(OUT / "showreel.webp", save_all=True, append_images=frames[1:], duration=int(1000 / 15), loop=0, quality=80, method=6)
print("gif", (OUT / "showreel.gif").stat().st_size // 1024, "KB; webp", (OUT / "showreel.webp").stat().st_size // 1024, "KB;", len(frames), "frames")
