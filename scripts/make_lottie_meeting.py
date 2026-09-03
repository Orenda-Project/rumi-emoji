#!/usr/bin/env python3
"""Meeting presence set for the Rumi mark: the states a call bot needs, as Lottie + GIF.

usage: python3 scripts/make_lottie_meeting.py [name ...]   -> lottie-meeting/rumi-meet-<name>.json + .gif
Presence states are longer loops (4 s) than chat reactions (3 s) because they sit on screen.
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rumi_mark_rig import *
import make_lottie_mark as MK

OUT = pathlib.Path(__file__).resolve().parent.parent / "lottie-meeting"
E = {}
def emo(name, seconds=4.0):
    def deco(fn): E[name] = (fn, seconds); return fn
    return deco


def hand(f, side=1, t_in=900, t_out=2400, wave=None, rise=False):
    """Small rounded hand near the right dot: palm + 4 fingers, anchored at the wrist."""
    g = f.prop(); cx, cy = near_right(2.1, -0.2); r = RP * .9
    rrect(g, (cx, cy), r * 1.3, r * 1.5, r * .35)
    for k, (dx, h) in enumerate(((-.48, 1.0), (-.16, 1.25), (.16, 1.2), (.48, .95))): rrect(g, (cx + dx * r, cy - r * .75 - h * r * .5), r * .3, h * r, r * .15)
    rrect(g, (cx - r * .85, cy - r * .1), r * .3, r * .8, r * .15)   # thumb
    anchor(g, (cx, cy + r * .75))
    if rise:
        p = g.transform.position; base = V(cx, cy + r * .75)
        p.add_keyframe(0, base + V(0, 90), HOLD); p.add_keyframe(ms(t_in), base + V(0, 90), DECEL); overshoot(p, ms(t_in), base + V(0, 90), base, 380, .1)
        p.add_keyframe(ms(t_out), base, ACCEL); p.add_keyframe(ms(t_out + 220), base + V(0, 90), HOLD)
        fade(g, [(t_in, 0), (t_in + 40, 100), (t_out, 100), (t_out + 220, 0)])
    else:
        pop(g, t_in, 240, 1.12, out_t=t_out)
    if wave:
        rot = g.transform.rotation; amp, period = wave
        rot.add_keyframe(ms(t_in), -amp, SOFT); t = t_in + 200
        k = 0
        while t < t_out - 100: rot.add_keyframe(ms(t), amp if k % 2 == 0 else -amp, SOFT); t += period; k += 1
        rot.add_keyframe(ms(t_out), 0, SOFT)
    return g


@emo("listening", 4.0)
def _(f):
    f.breathe(3, 4000); f.blink(500)
    f.eyes("closed", 1400, 170, "l"); f.eyes("closed", 1400, 170, "r")                       # dots squash, then bow into contented arcs
    f.mouth.link_key(0, 0); f.mouth.link_key(1350, 0, STD); f.mouth.link_key(1650, .012, SOFT); f.mouth.link_key(2700, .012, STD); f.mouth.link_key(3050, 0, SOFT)
    f.eyes("dot", 2650, 170, "l"); f.eyes("dot", 2850, 170, "r")                            # reopen left first, right 200 ms later
    g = f.prop(); c = P(EXR + .19, EY - .13)                                                   # twinkle on the lagging eye
    for a in (-65, -30, 5): line(g, (c.x, c.y), (c.x + 20 * math.cos(math.radians(a)), c.y + 20 * math.sin(math.radians(a))), NAVY, SW * .55)
    anchor(g, (c.x, c.y)); pop(g, 2760, 140, 1.25, out_t=2980, out_dur=120)


@emo("speaking", 4.0)
def _(f):
    f.breathe(2, 4000); f.blink(2300)
    f.mouth.set("open", 250, 140); f.mouth.set("link", 3650, 160)
    s = f.mouth.open.transform.scale
    # talking rhythm: syllables 140-220 ms with varying openness, a short pause mid-sentence
    t = 450; import random; rnd = random.Random(11)
    while t < 3500:
        if 1900 < t < 2150: t = 2150; s.add_keyframe(ms(2000), V(100, 25), SOFT); continue
        d = rnd.choice((140, 160, 200, 220)); o = rnd.choice((55, 75, 100, 90, 45))
        s.add_keyframe(ms(t), V(100, o), SOFT); s.add_keyframe(ms(t + d * .55), V(100, 22), SOFT); t += d
    s.add_keyframe(ms(3550), V(100, 30), SOFT)
    p = f.pos
    for i, tt in enumerate(range(400, 3400, 600)): p.add_keyframe(ms(tt), V(0, 0), SOFT); p.add_keyframe(ms(tt + 300), V(3 if i % 2 else -3, -3), SOFT)


@emo("thinking", 6.0)
def _(f):
    f.breathe(2, 3000); f.blink(4200)
    for e in (f.eyeL, f.eyeR):
        p = e.g.transform.position; p.add_keyframe(0, V(0, 0), STD); p.add_keyframe(ms(600), V(5, -5), SOFT); p.add_keyframe(ms(5200), V(5, -5), STD); p.add_keyframe(ms(5800), V(0, 0), SOFT)
    f.mouth.set("smirk", 500, 200); f.mouth.set("link", 5300, 220)
    bx, by = near_right(1.3, -3.0); r = RP * 1.0
    g = f.prop()
    path(g, [((bx - r * 1.5, by + r * .4), (0, -r * .6), (0, r * .6)), ((bx - r * .6, by + r * 1.1), (-r * .6, 0), (r * .6, 0)), ((bx + r * .7, by + r * 1.1), (-r * .6, 0), (r * .6, 0)), ((bx + r * 1.6, by + r * .3), (0, r * .6), (0, -r * .6)),
             ((bx + r * .9, by - r * .8), (r * .6, 0), (-r * .5, -r * .3)), ((bx, by - r * 1.1), (r * .5, 0), (-r * .5, 0)), ((bx - r * .9, by - r * .7), (r * .4, -r * .4), (-r * .5, .1 * r))], fill=WHITE, stroke=NAVY, width=SW * .8, closed=True)
    anchor(g, (bx, by + r)); pop(g, 700, 260, 1.1, out_t=5200)
    for i in (-1, 0, 1):   # dots pulse in sequence for as long as the bubble is up
        d = f.prop(); ellipse(d, (bx + i * r * .55, by + r * .15), r * .17); anchor(d, (bx + i * r * .55, by + r * .15))
        s = d.transform.scale; s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(950), V(0, 0), DECEL); s.add_keyframe(ms(1100), V(100, 100), HOLD)
        for t in range(1200, 4400, 600): s.add_keyframe(ms(t + (i + 1) * 150), V(100, 100), SOFT); s.add_keyframe(ms(t + (i + 1) * 150 + 150), V(150, 150), SOFT); s.add_keyframe(ms(t + (i + 1) * 150 + 300), V(100, 100), SOFT)
        s.add_keyframe(ms(5200), V(100, 100), ACCEL); s.add_keyframe(ms(5380), V(0, 0), HOLD)
    # small trailing bubbles
    for j, (dx, dy, rr) in enumerate(((-1.9, 1.9, .28), (-2.6, 2.7, .18))):
        b = f.prop(); ellipse(b, (bx + dx * r, by + dy * r), r * rr, fill=WHITE, stroke=NAVY, width=SW * .7); anchor(b, (bx + dx * r, by + dy * r)); pop(b, 800 - j * 150, 200, 1.15, out_t=5150 + j * 60)


@emo("nod", 3.0)
def _(f):
    f.blink(300); p = f.pos
    p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(900), V(0, 0), DECEL)
    for i, t in enumerate((900, 1400)): p.add_keyframe(ms(t + 180), V(0, 16 if i == 0 else 12), SOFT); p.add_keyframe(ms(t + 420), V(0, 0), SOFT)
    p.add_keyframe(ms(3000), V(0, 0), SOFT)
    f.mouth.link_key(0, 0); f.mouth.link_key(900, 0, STD); f.mouth.link_key(1200, -.02, SOFT); f.mouth.link_key(1900, -.02, STD); f.mouth.link_key(2300, 0, SOFT)   # smile deepens


@emo("shake-no", 3.0)
def _(f):
    f.blink(300); f.mouth.set("flat", 800, 160); f.mouth.set("link", 2300, 180)
    p = f.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(850), V(0, 0), DECEL)
    for i, t in enumerate(range(850, 1900, 175)): p.add_keyframe(ms(t + 175), V(-14 if i % 2 == 0 else 14, 0), SOFT)
    p.add_keyframe(ms(2200), V(0, 0), SOFT); p.add_keyframe(ms(3000), V(0, 0), SOFT)


@emo("wave-hello", 3.0)
def _(f):
    f.breathe(2, 3000); f.eyes("arch", 850, 140); f.eyes("dot", 2500, 140)
    f.mouth.link_key(0, 0); f.mouth.link_key(800, 0, STD); f.mouth.link_key(1050, -.015, SOFT); f.mouth.link_key(2400, -.015, STD); f.mouth.link_key(2700, 0, SOFT)
    hand(f, t_in=800, t_out=2450, wave=(22, 260))


@emo("wave-bye", 3.0)
def _(f):
    f.breathe(2, 3000); f.eyes("closed", 900, 160); f.eyes("dot", 2550, 160)
    f.mouth.set("small", 900, 180); f.mouth.set("link", 2500, 180)
    hand(f, t_in=850, t_out=2450, wave=(16, 420))


@emo("raise-hand", 3.0)
def _(f):
    f.breathe(2, 3000); f.blink(300); f.mouth.set("small", 850, 160); f.mouth.set("link", 2400, 160)
    for e in (f.eyeL, f.eyeR): p = e.g.transform.position; p.add_keyframe(ms(850), V(0, 0), STD); p.add_keyframe(ms(1100), V(4, -3), SOFT); p.add_keyframe(ms(2300), V(4, -3), STD); p.add_keyframe(ms(2550), V(0, 0), SOFT)
    hand(f, t_in=850, t_out=2400, rise=True)


@emo("muted", 4.0)
def _(f):
    f.breathe(2, 4000); f.blink(1700); f.mouth.set("flat", 0)
    g = f.prop(); cx, cy = near_right(1.9, -1.9); r = RP * 1.0
    rrect(g, (cx, cy - r * .5), r * .9, r * 1.7, r * .45); path(g, [((cx - r * .7, cy - r * .1), (0, 0), (0, r * .9)), ((cx + r * .7, cy - r * .1), (0, r * .9), (0, 0))], stroke=NAVY, width=SW * .7)
    line(g, (cx, cy + r * .75), (cx, cy + r * 1.3), NAVY, SW * .7); line(g, (cx - r * .5, cy + r * 1.3), (cx + r * .5, cy + r * 1.3), NAVY, SW * .7)
    anchor(g, (cx, cy)); pop(g, 400, 240, 1.1)
    s = f.prop(); line(s, (cx - r * 1.1, cy - r * 1.5), (cx + r * 1.1, cy + r * 1.4), RED, SW * .9)
    tr = s.shapes[-2].add_shape(objects.Trim()); tr.end.add_keyframe(0, 0, HOLD); tr.end.add_keyframe(ms(750), 0, DECEL); tr.end.add_keyframe(ms(950), 100, HOLD)
    anchor(s, (cx, cy)); sc = s.transform.scale; sc.add_keyframe(0, V(0, 0), HOLD); sc.add_keyframe(ms(750), V(100, 100), HOLD)


@emo("connecting", 3.0)
def _(f):
    f.breathe(2, 3000); f.blink(1900); f.mouth.set("dots", 0)
    for i, g in enumerate(f.mouth.dotgroups):   # ... pulses in sequence, forever
        s = g.transform.scale
        for t in range(0, 3000, 900): s.add_keyframe(ms(t + i * 150), V(100, 100), SOFT); s.add_keyframe(ms(t + i * 150 + 150), V(160, 160), SOFT); s.add_keyframe(ms(t + i * 150 + 300), V(100, 100), SOFT)
    MK.spinner(f)


@emo("reconnecting", 3.0)
def _(f):
    f.breathe(1.5, 3000); f.mouth.set("wavy", 0)
    for i, t in enumerate(range(0, 3001, 375)): f.mouth.wavy_key(t, i * math.pi / 2)
    f.eyes("small", 0)
    g = f.prop(); cx, cy = near_right(1.7, -1.8); r = RP * .75
    ellipse(g, (cx, cy), r, fill=None, stroke=NAVY, width=SW * 1.1); tr = g.shapes[-2].add_shape(objects.Trim()); tr.start.value = 0; tr.end.value = 65
    path(g, [((cx + r * .6, cy - r * 1.35), (0, 0), (0, 0)), ((cx + r * 1.4, cy - r * .9), (0, 0), (0, 0)), ((cx + r * .55, cy - r * .45), (0, 0), (0, 0))], fill=NAVY, closed=True)
    anchor(g, (cx, cy)); rot = g.transform.rotation   # stutters: spins, sticks, jumps
    rot.add_keyframe(0, 0, LIN); rot.add_keyframe(ms(900), 200, HOLD); rot.add_keyframe(ms(1400), 200, DECEL); rot.add_keyframe(ms(1500), 230, LIN); rot.add_keyframe(ms(2400), 330, HOLD); rot.add_keyframe(ms(2700), 330, LIN); rot.add_keyframe(ms(3000), 360, LIN)
    MK.sweat(f, 1500)


@emo("recording", 3.0)
def _(f):
    f.breathe(2, 3000); f.blink(1300)
    g = f.prop(); cx, cy = near_right(2.0, -2.2); ellipse(g, (cx, cy), RP * .45, fill=RED); anchor(g, (cx, cy))
    s = g.transform.scale; o = g.transform.opacity
    for t in range(0, 3000, 1000): s.add_keyframe(ms(t), V(100, 100), SOFT); s.add_keyframe(ms(t + 500), V(130, 130), SOFT); o.add_keyframe(ms(t), 100, SOFT); o.add_keyframe(ms(t + 500), 55, SOFT)
    s.add_keyframe(ms(3000), V(100, 100), SOFT); o.add_keyframe(ms(3000), 100, SOFT)
    h = f.prop(); ellipse(h, (cx, cy), RP * .45, fill=None, stroke=RED, width=SW * .5); anchor(h, (cx, cy))   # expanding ring
    hs = h.transform.scale; ho = h.transform.opacity
    for t in range(0, 3000, 1000): hs.add_keyframe(ms(t), V(100, 100), DECEL); hs.add_keyframe(ms(t + 900), V(260, 260), LIN); ho.add_keyframe(ms(t), 70, LIN); ho.add_keyframe(ms(t + 900), 0, HOLD)


def render_gif(json_path, gif_path, fps=15):
    from lottie.parsers.tgs import parse_tgs
    from lottie.exporters.cairo import export_png
    from PIL import Image
    an = parse_tgs(str(json_path)); frames = []; step = max(1, round(FPS / fps)); tmp = gif_path.with_suffix(".tmp.png")
    for fr in range(0, int(an.out_point), step):
        with open(tmp, "wb") as fh: export_png(an, fh, frame=fr)
        im = Image.open(tmp).convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); frames.append(bg.convert("RGB"))
    tmp.unlink()
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for n in (sys.argv[1:] or list(E)):
        fn, sec = E[n]; f = Face(sec); fn(f); p = f.save(OUT / f"rumi-meet-{n}.json")
        render_gif(p, OUT / f"rumi-meet-{n}.gif"); print("built", n, p.stat().st_size // 1024, "KB json,", (OUT / f"rumi-meet-{n}.gif").stat().st_size // 1024, "KB gif")
