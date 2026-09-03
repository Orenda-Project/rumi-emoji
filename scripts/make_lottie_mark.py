#!/usr/bin/env python3
"""58 World-of-Rumi logo-mark emotions -> Lottie (matches emoji-mark-emotions/ 1:1, 512 canvas).

usage: python3 scripts/make_lottie_mark.py [name ...]     -> lottie-mark/rumi-mark-<name>.json
Grammar: REACTION = rest(0-800, blink) -> state in (800) -> hold + secondary -> out (2300) -> rest (3000).
         STATUS   = state held for the whole loop, secondary motion loops seamlessly.
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rumi_mark_rig import *

OUT = pathlib.Path(__file__).resolve().parent.parent / "lottie-mark"
IN, OUTT, END = 800, 2300, 3000


def react(f, eyes=None, mouth=None, blink_at=400, lift=None, eyes_dur=120, mouth_dur=140):
    """rest -> state -> rest. eyes: state or (left, right). Returns nothing; props go on top."""
    f.breathe()
    if blink_at: f.blink(blink_at)
    if eyes:
        l, r = eyes if isinstance(eyes, tuple) else (eyes, eyes)
        if l: f.eyes(l, IN, eyes_dur, "l"); f.eyes("dot", OUTT, eyes_dur, "l")
        if r: f.eyes(r, IN + 60, eyes_dur, "r"); f.eyes("dot", OUTT + 60, eyes_dur, "r")   # 60 ms offset = overlapping action
    if mouth:
        f.mouth.set(mouth, IN, mouth_dur); f.mouth.set("link", OUTT, mouth_dur)
    if lift is not None:
        f.mouth.link_key(0, 0); f.mouth.link_key(IN - 100, 0, STD); f.mouth.link_key(IN + 200, lift, SOFT); f.mouth.link_key(OUTT, lift, STD); f.mouth.link_key(OUTT + 300, 0, SOFT)


def status(f, eyes=None, mouth=None, blink_at=None):
    f.breathe(2)
    if eyes:
        l, r = eyes if isinstance(eyes, tuple) else (eyes, eyes)
        if l: f.eyeL.set(l, 0)
        if r: f.eyeR.set(r, 0)
    if mouth: f.mouth.set(mouth, 0)
    if blink_at: f.blink(blink_at)


# ---------- props (geometry from logo_mark_emotions.py) ----------
def glyph_q(g, c, size=1.1, color=NAVY):
    x, y = c; r = RP * size; w = SW * 1.2
    pts = [(x + .5 * r * math.cos(math.radians(a)), y - r * .6 + .5 * r * math.sin(math.radians(a))) for a in range(-180, 61, 20)]
    polyline(g, pts + [(x, y + r * .35)], width=w); ellipse(g, (x, y + r * .95), w * .7); anchor(g, (x, y))


def glyph_bang(g, c, size=1.2, color=NAVY):
    x, y = c; r = RP * size; w = SW * 1.2
    line(g, (x, y - r), (x, y + r * .35), color, w); ellipse(g, (x, y + r * .95), w * .7, fill=color); anchor(g, (x, y + r * .95))


def glyph_dots(f, c, t0, gap=180, size=1.0):
    x, y = c; r = RP * size; gs = []
    for i in (-1, 0, 1):
        g = f.prop(); ellipse(g, (x + i * r * .55, y), SW * .6); anchor(g, (x + i * r * .55, y)); pop(g, t0 + (i + 1) * gap, 160, out_t=OUTT); gs.append(g)
    return gs


def sweat(f, t0=IN + 150):
    g = f.prop(); c = P(EXR + .16, EY - .02); drop(g, (c.x, c.y), U(.08)); anchor(g, (c.x, c.y - U(.08)))
    pop(g, t0, 260, 1.0); p = g.transform.position; p.add_keyframe(ms(t0 + 300), V(c.x, c.y - U(.08)), ACCEL); p.add_keyframe(ms(t0 + 900), V(c.x, c.y + U(.10)), STD)
    fade(g, [(t0 + 700, 100), (t0 + 900, 0)])
    return g


def sparkles(f, spots=((EXR + .15, EY - .18, .5), (EXR + .28, EY - .04, .35), (EXL - .16, EY - .14, .4)), t0=IN + 100, loop_out=OUTT):
    for i, (x, y, s) in enumerate(spots):
        g = f.prop(); c = P(x, y); sparkle(g, (c.x, c.y), RP * s); anchor(g, (c.x, c.y))
        pop(g, t0 + i * 120, 220, 1.15, out_t=loop_out + i * 60 if loop_out else None)
        rot = g.transform.rotation; rot.add_keyframe(ms(t0), 0, LIN); rot.add_keyframe(ms(END), 90 * (1 if i % 2 else -1), LIN)
        sc = g.transform.scale  # twinkle: pulse while visible
        for k, t in enumerate(range(t0 + 400 + i * 120, (loop_out or END) - 100, 320)):
            sc.add_keyframe(ms(t), V(100, 100), SOFT); sc.add_keyframe(ms(t + 160), V(70, 70), SOFT)


def blush(f, t0=IN, t1=OUTT):
    for x in (EXL, EXR):
        g = f.prop(on_top=False); c = P(x, EY + .16); ellipse(g, (c.x, c.y), RP * .7, RP * .3, PINK); fade(g, [(t0, 0), (t0 + 300, 100), (t1, 100), (t1 + 250, 0)])


def hearts_float(f, t0=IN + 100):
    for i, (x, y, s) in enumerate(((EXR + .14, EY - .16, .55), (EXR + .26, EY - .30, .8))):
        g = f.prop(); c = P(x, y); heart(g, (c.x, c.y), RP * s); anchor(g, (c.x, c.y))
        for k, st in enumerate((t0 + i * 350, t0 + i * 350 + 900)):
            if st + 900 > OUTT: break
            pop(g, st, 200, 1.2, out_t=st + 700, out_dur=200)
        p = g.transform.position; p.add_keyframe(ms(t0), V(c.x, c.y + 14), LIN); p.add_keyframe(ms(OUTT), V(c.x, c.y - 26), LIN)


def anger_mark(f, t0=IN + 120):
    g = f.prop(); cx, cy = near_right(1.7, -1.9); r = RP * .7
    for a in (30, 100, 170, 240): line(g, (cx + r * .4 * math.cos(math.radians(a)), cy + r * .4 * math.sin(math.radians(a))), (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))), RED, SW * 1.1)
    anchor(g, (cx, cy)); pop(g, t0, 200, 1.3, out_t=OUTT)
    sc = g.transform.scale
    for t in range(t0 + 400, OUTT - 200, 400): sc.add_keyframe(ms(t), V(100, 100), SOFT); sc.add_keyframe(ms(t + 200), V(118, 118), SOFT)
    return g


def bulb(f, t0=IN + 100):
    g = f.prop(); cx, cy = near_right(1.6, -2.4); r = RP * .8
    ellipse(g, (cx, cy), r - SW * .4, fill=None, stroke=NAVY, width=SW * .8); rrect(g, (cx, cy + r * 1.07), r * .7, r * .55, 0)
    anchor(g, (cx, cy + r)); pop(g, t0, 240, 1.15, out_t=OUTT)
    rays = f.prop()
    for a in (-135, -90, -45): line(rays, (cx + r * 1.3 * math.cos(math.radians(a)), cy + r * 1.3 * math.sin(math.radians(a))), (cx + r * 1.7 * math.cos(math.radians(a)), cy + r * 1.7 * math.sin(math.radians(a))), NAVY, SW * .8)
    anchor(rays, (cx, cy)); pop(rays, t0 + 180, 200, 1.25, out_t=OUTT - 100)
    sc = rays.transform.scale
    for t in range(t0 + 600, OUTT - 300, 500): sc.add_keyframe(ms(t), V(100, 100), SOFT); sc.add_keyframe(ms(t + 250), V(85, 85), SOFT)


def checkmark(f, t0=IN + 100):
    g = f.prop(); cx, cy = near_right(1.6, -1.6); r = RP * .8
    polyline(g, [(cx - r, cy), (cx - r * .3, cy + r * .7), (cx + r, cy - r * .8)], BLUE, SW * 1.4)
    tr = g.shapes[-2].add_shape(objects.Trim()); tr.end.add_keyframe(0, 0, HOLD); tr.end.add_keyframe(ms(t0), 0, DECEL); tr.end.add_keyframe(ms(t0 + 280), 100, HOLD)  # draw-on
    anchor(g, (cx, cy)); s = g.transform.scale; s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(t0), V(100, 100), HOLD); s.add_keyframe(ms(t0 + 280), V(100, 100), SOFT); s.add_keyframe(ms(t0 + 400), V(112, 112), SOFT); s.add_keyframe(ms(t0 + 520), V(100, 100), HOLD)
    s.add_keyframe(ms(OUTT), V(100, 100), ACCEL); s.add_keyframe(ms(OUTT + 180), V(0, 0), HOLD)


def spinner(f):
    g = f.prop(); cx, cy = near_right(1.7, -1.8); r = RP * .75
    e = ellipse(g, (cx, cy), r, fill=None, stroke=NAVY, width=SW * 1.1); tr = g.shapes[-2].add_shape(objects.Trim()); tr.start.value = 0; tr.end.value = 80
    path(g, [((cx + r * .6, cy - r * 1.35), (0, 0), (0, 0)), ((cx + r * 1.4, cy - r * .9), (0, 0), (0, 0)), ((cx + r * .55, cy - r * .45), (0, 0), (0, 0))], fill=NAVY, closed=True)
    anchor(g, (cx, cy)); rot = g.transform.rotation; rot.add_keyframe(0, 0, LIN); rot.add_keyframe(ms(END), 360, LIN)


def hourglass(f):
    g = f.prop(); cx, cy = near_right(1.8, -1.9); r = RP * .8
    polyline(g, [(cx - r * .7, cy - r), (cx + r * .7, cy - r), (cx - r * .7, cy + r), (cx + r * .7, cy + r), (cx - r * .7, cy - r)], NAVY, SW * .9)
    sand = objects.Group(); g.shapes.insert(0, sand); path(sand, [((cx - r * .35, cy + r * .55), (0, 0), (0, 0)), ((cx + r * .35, cy + r * .55), (0, 0), (0, 0)), ((cx, cy + r * .05), (0, 0), (0, 0))], fill=NAVY, closed=True)
    anchor(g, (cx, cy)); rot = g.transform.rotation   # flips at 1.2 s with a spring, sand shrinks then refills
    rot.add_keyframe(0, 0, STD); rot.add_keyframe(ms(1200), 0, DECEL); overshoot(rot, ms(1200), 0, 180, 420, .06); rot.add_keyframe(ms(END), 180, HOLD)


def glasses(f, t0=None):
    g = f.prop(on_top=False)
    for x in (EXL, EXR):
        c = P(x, EY); ellipse(g, (c.x, c.y), RP * 1.55 - SW * .45, fill=None, stroke=NAVY, width=SW * .9)
    a, b = P(EXL + .15, EY), P(EXR - .15, EY); line(g, (a.x, a.y), (b.x, b.y), NAVY, SW * .9)
    if t0:  # slide down from above and settle
        anchor(g, (OX + .5 * M, L.y)); p = g.transform.position
        p.add_keyframe(0, V(OX + .5 * M, L.y - 60), HOLD); fade(g, [(t0, 0), (t0 + 60, 100), (OUTT, 100), (OUTT + 150, 0)])
        p.add_keyframe(ms(t0), V(OX + .5 * M, L.y - 60), DECEL); overshoot(p, ms(t0), V(OX + .5 * M, L.y - 60), V(OX + .5 * M, L.y), 320, .1)
        p.add_keyframe(ms(OUTT), V(OX + .5 * M, L.y), ACCEL); p.add_keyframe(ms(OUTT + 160), V(OX + .5 * M, L.y - 60), HOLD)
    return g


def shades(f, t0=IN):
    g = f.prop()
    for x in (EXL, EXR):
        c = P(x, EY); r = RP * 1.45; rrect(g, (c.x, c.y - r * .075), 2 * r, r * 1.35, r * .4)
    a, b = P(EXL + .14, EY - .03), P(EXR - .14, EY - .03); line(g, (a.x, a.y), (b.x, b.y))
    anchor(g, (OX + .5 * M, L.y)); p = g.transform.position
    p.add_keyframe(0, V(OX + .5 * M, L.y - 90), HOLD); fade(g, [(t0, 0), (t0 + 40, 100), (OUTT, 100), (OUTT + 200, 0)])
    p.add_keyframe(ms(t0), V(OX + .5 * M, L.y - 90), DECEL); overshoot(p, ms(t0), V(OX + .5 * M, L.y - 90), V(OX + .5 * M, L.y), 380, .08)
    p.add_keyframe(ms(OUTT), V(OX + .5 * M, L.y), ACCEL); p.add_keyframe(ms(OUTT + 200), V(OX + .5 * M, L.y - 90), HOLD)


def halo(f):
    g = f.prop(); c = P(.5, EY - .22); ellipse(g, (c.x, c.y), U(.28), U(.07), fill=None, stroke=NAVY, width=SW * .9); anchor(g, (c.x, c.y))
    pop(g, IN + 100, 260, 1.08, out_t=OUTT); p = g.transform.position
    for t in range(IN + 400, OUTT - 300, 600): p.add_keyframe(ms(t), V(c.x, c.y), SOFT); p.add_keyframe(ms(t + 300), V(c.x, c.y - 6), SOFT)


def horns(f):
    for x, sgn in ((EXL, -1), (EXR, 1)):
        g = f.prop(on_top=False); c = P(x, EY); r = RP
        path(g, [((c.x + sgn * r * .2, c.y - r * .8), (0, 0), (0, 0)), ((c.x + sgn * r, c.y - r * .6), (0, 0), (0, 0)), ((c.x + sgn * r * .8, c.y - r * 2), (0, 0), (0, 0))], fill=RED, closed=True)
        anchor(g, (c.x + sgn * r * .6, c.y - r * .7)); pop(g, IN + 60 + (0 if sgn < 0 else 80), 240, 1.2, out_t=OUTT)


def party_hat(f):
    g = f.prop(); c = P(EXR, EY); r = RP
    path(g, [((c.x - r * .95, c.y - r * .5), (0, 0), (0, 0)), ((c.x + r * .95, c.y - r * .5), (0, 0), (0, 0)), ((c.x + r * .3, c.y - r * 2.7), (0, 0), (0, 0))], fill=BLUE, closed=True)
    anchor(g, (c.x, c.y - r * .5)); pop(g, IN + 60, 260, 1.1, out_t=OUTT); rot = g.transform.rotation; wobble(rot, IN + 400, OUTT - 200, 6, 500)
    for i, (dx, dy) in enumerate(((-2.2, -2.0), (-1.4, -2.9), (1.6, -3.0), (2.4, -1.8))):
        d = f.prop(); ellipse(d, (c.x + dx * r, c.y + dy * r), r * .16, fill=CORAL); anchor(d, (c.x + dx * r, c.y + dy * r))
        pop(d, IN + 250 + i * 90, 200, 1.3, out_t=OUTT - 200 + i * 40)
        p = d.transform.position; p.add_keyframe(ms(IN + 250), V(c.x + dx * r, c.y + dy * r), LIN); p.add_keyframe(ms(OUTT), V(c.x + dx * r, c.y + dy * r + 26), LIN)


def headphones(f):
    g = f.prop(on_top=False); a, b = P(EXL - .08, EY - .02), P(EXR + .08, EY - .02); arc(g, a.x, a.y, b.x, b.y, -U(.26), width=SW * .9)
    for x in (EXL - .13, EXR + .13):
        c = P(x, EY); rrect(g, (c.x, c.y), RP * .55, RP * 1.1, RP * .25)


def coffee(f):
    g = f.prop(); c = P(EXR + .08, EY + .24); r = RP * 1.1
    rrect(g, (c.x - r * .1, c.y), r * 1.8, r * 1.8, r * .2); ellipse(g, (c.x + r * .95, c.y - .05 * r), r * .45, fill=None, stroke=NAVY, width=SW * .8)
    anchor(g, (c.x, c.y + r * .9)); rot = g.transform.rotation; wobble(rot, 300, END - 300, 2, 900)  # sip tilt
    for k, i in enumerate((-.4, .2)):
        s = f.prop(); line(s, (c.x + i * r, c.y - r * 1.9), (c.x + i * r + r * .15, c.y - r * 1.3), NAVY, SW * .6); anchor(s, (c.x + i * r, c.y - r * 1.6))
        p = s.transform.position; o = s.transform.opacity; base = V(c.x + i * r, c.y - r * 1.6)
        for st in range(k * 500, END, 1500):
            p.add_keyframe(ms(st), base, LIN); p.add_keyframe(ms(st + 1400), base + V(0, -22), LIN)
            o.add_keyframe(ms(st), 0, LIN); o.add_keyframe(ms(st + 300), 100, LIN); o.add_keyframe(ms(st + 1100), 100, LIN); o.add_keyframe(ms(st + 1400), 0, HOLD)


def music_note(f):
    g = f.prop(); cx, cy = near_right(1.8, -2.0); r = RP * .8
    ellipse(g, (cx, cy + r * .6), r * .45); line(g, (cx + r * .4, cy + r * .6), (cx + r * .4, cy - r * 1.2), NAVY, SW * .9); line(g, (cx + r * .4, cy - r * 1.2), (cx + r * 1.3, cy - r * .9), NAVY, SW)
    anchor(g, (cx, cy + r * .6)); rot = g.transform.rotation; wobble(rot, 0, END, 12, 750); p = g.transform.position
    p.add_keyframe(0, V(cx, cy + r * .6), SOFT); p.add_keyframe(ms(1500), V(cx, cy + r * .6 - 10), SOFT); p.add_keyframe(ms(END), V(cx, cy + r * .6), SOFT)


def rain_cloud(f):
    g = f.prop(); c = P(.5, EY - .30); r = RP * .75
    for (ox, oy, s) in ((-1.2, .2, .75), (-.4, -.3, 1.0), (.5, -.2, .9), (1.2, .25, .7)): ellipse(g, (c.x + ox * r, c.y + oy * r), s * r, fill=BLUE)
    rrect(g, (c.x, c.y + r * .55), r * 2.4, r * .7, 0, BLUE); anchor(g, (c.x, c.y)); pop(g, IN + 100, 300, 1.06, out_t=OUTT)
    for k, i in enumerate((-.8, 0, .8)):
        d = f.prop(); line(d, (c.x + i * r, c.y + r * 1.4), (c.x + i * r - r * .15, c.y + r * 2.0), BLUE, SW * .6); anchor(d, (c.x + i * r, c.y + r * 1.7))
        p = d.transform.position; o = d.transform.opacity; base = V(c.x + i * r, c.y + r * 1.7); o.add_keyframe(0, 0, HOLD)
        for st in range(IN + 400 + k * 200, OUTT - 500, 600):
            p.add_keyframe(ms(st), base, LIN); p.add_keyframe(ms(st + 500), base + V(-4, 24), LIN)
            o.add_keyframe(ms(st), 0, LIN); o.add_keyframe(ms(st + 100), 100, LIN); o.add_keyframe(ms(st + 400), 100, LIN); o.add_keyframe(ms(st + 500), 0, HOLD)


def burst(f):
    for x in (EXL, EXR):
        g = f.prop(); c = P(x, EY); r = RP
        for a in (-150, -110, -70, -30): line(g, (c.x + r * 1.6 * math.cos(math.radians(a)), c.y + r * 1.6 * math.sin(math.radians(a))), (c.x + r * 2.1 * math.cos(math.radians(a)), c.y + r * 2.1 * math.sin(math.radians(a))), NAVY, SW * .8)
        anchor(g, (c.x, c.y)); pop(g, IN + 140, 200, 1.3, out_t=OUTT)


def thermo(f):
    g = f.prop(); cx, cy = near_right(1.9, -1.4); r = RP * .9
    rrect(g, (cx, cy - r * .75), r * .6, r * 2.5, r * .3); merc = objects.Group(); g.shapes.insert(0, merc); ellipse(merc, (cx, cy + r * .75), r * .6, fill=RED)
    anchor(merc, (cx, cy + r * .75)); s = merc.transform.scale
    for t in range(0, END, 1000): s.add_keyframe(ms(t), V(100, 100), SOFT); s.add_keyframe(ms(t + 500), V(112, 112), SOFT)
    anchor(g, (cx, cy)); rot = g.transform.rotation; wobble(rot, 0, END, 3, 700)


def mask(f):
    g = f.prop(); c = P(.5, EY + .20); w, h = U(.30), U(.11)
    rrect(g, (c.x, c.y), 2 * w, 2 * h, h * .5, BLUE)
    for sgn in (-1, 1): line(g, (c.x + sgn * w, c.y - h * .5), (c.x + sgn * (w + RP * .9), c.y - h * 1.2), BLUE, SW * .7)
    anchor(g, (c.x, c.y)); p = g.transform.position   # slides up from below, then breathes with the face (mask puffs)
    p.add_keyframe(0, V(c.x, c.y + 70), HOLD); fade(g, [(IN, 0), (IN + 50, 100), (OUTT, 100), (OUTT + 200, 0)])
    p.add_keyframe(ms(IN), V(c.x, c.y + 70), DECEL); overshoot(p, ms(IN), V(c.x, c.y + 70), V(c.x, c.y), 360, .08)
    p.add_keyframe(ms(OUTT), V(c.x, c.y), ACCEL); p.add_keyframe(ms(OUTT + 200), V(c.x, c.y + 70), HOLD)
    s = g.transform.scale
    for t in range(IN + 500, OUTT - 300, 800): s.add_keyframe(ms(t), V(100, 100), SOFT); s.add_keyframe(ms(t + 400), V(104, 108), SOFT)


def moon(f):
    g = f.prop(); cx, cy = near_right(1.9, -2.2); r = RP * .75
    e = ellipse(g, (cx, cy), r * .72, fill=None, stroke=NAVY, width=r * .55); tr = g.shapes[-2].add_shape(objects.Trim()); tr.start.value = 12; tr.end.value = 70   # crescent = 58% of a thick ring
    anchor(g, (cx, cy)); rot = g.transform.rotation; rot.add_keyframe(0, -8, SOFT); rot.add_keyframe(ms(1500), 8, SOFT); rot.add_keyframe(ms(END), -8, SOFT)


def tear_fall(f, x, y, t0, size=U(.09)):
    g = f.prop(); c = P(x, y); drop(g, (c.x, c.y), size); anchor(g, (c.x, c.y - size)); base = V(c.x, c.y - size)
    s = g.transform.scale; s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(t0), V(0, 0), DECEL); s.add_keyframe(ms(t0 + 500), V(100, 100), SOFT)
    p = g.transform.position; p.add_keyframe(ms(t0 + 700), base, ACCEL); p.add_keyframe(ms(t0 + 1300), base + V(0, 90), STD)
    fade(g, [(t0 + 1100, 100), (t0 + 1300, 0)])


# ---------- the 58 emotions ----------
def happy_family(f, eyes, mouth, **k): react(f, eyes, mouth, **k)

E = {}
def emo(name):
    def deco(fn): E[name] = fn; return fn
    return deco

@emo("neutral")
def _(f): status(f, "dot", "flat", blink_at=1400); f.mouth.set("flat", 0)
@emo("content")
def _(f): status(f, "dot", "small", blink_at=1100)
@emo("laugh")
def _(f):
    react(f, "arch", "open"); od = f.mouth.open; s = od.transform.scale
    for i, t in enumerate(range(IN + 200, IN + 1100, 300)): s.add_keyframe(ms(t), V(100, 100), SOFT); s.add_keyframe(ms(t + 150), V(104, 118), SOFT)
    p = f.pos
    for t in range(IN + 200, IN + 1100, 300): p.add_keyframe(ms(t), V(0, 0), SOFT); p.add_keyframe(ms(t + 150), V(0, -6), SOFT)
@emo("lol")
def _(f): react(f, None, "teeth"); p = f.pos; [ (p.add_keyframe(ms(t), V(0, 0), SOFT), p.add_keyframe(ms(t + 130), V(0, -5), SOFT)) for t in range(IN + 150, OUTT - 300, 260)]
@emo("wink")
def _(f):
    react(f, (None, "arch"), None, blink_at=None); f.blink(300, "lr")
    g = f.prop(); c = P(EXR + .2, EY - .12)
    for a in (-60, -25, 10): line(g, (c.x, c.y), (c.x + 22 * math.cos(math.radians(a)), c.y + 22 * math.sin(math.radians(a))), NAVY, SW * .6)
    anchor(g, (c.x, c.y)); pop(g, IN + 150, 160, 1.2, out_t=IN + 700, out_dur=150)
@emo("blush")
def _(f): react(f, None, None, lift=.01); blush(f)
@emo("shy")
def _(f): react(f, "small", "small"); blush(f, IN + 100)
@emo("proud")
def _(f): react(f, "lid", None, lift=.02); sparkles(f); p = f.pos; p.add_keyframe(ms(IN), V(0, 0), SOFT); p.add_keyframe(ms(IN + 300), V(0, -8), SOFT); p.add_keyframe(ms(OUTT), V(0, -8), SOFT); p.add_keyframe(ms(OUTT + 300), V(0, 0), SOFT)
@emo("smug")
def _(f): react(f, "lid", "smirk", eyes_dur=200)
@emo("cool")
def _(f): react(f, None, None, lift=.015); shades(f)
@emo("love")
def _(f):
    react(f, "heart", None, lift=.02)
    for e in (f.eyeL, f.eyeR):
        s = e.heart.transform.scale
        for t in range(IN + 300, OUTT - 200, 600): s.add_keyframe(ms(t), V(100, 100), SOFT); s.add_keyframe(ms(t + 150), V(115, 115), SOFT); s.add_keyframe(ms(t + 300), V(100, 100), SOFT)
@emo("in-love")
def _(f): react(f, None, None, lift=.015); hearts_float(f)
@emo("starstruck")
def _(f):
    react(f, "star", "open")
    for e in (f.eyeL, f.eyeR): r = e.star.transform.rotation; r.add_keyframe(ms(IN), 0, LIN); r.add_keyframe(ms(OUTT), 72, LIN)
@emo("party")
def _(f): react(f, "arch", "open"); party_hat(f); p = f.pos; [(p.add_keyframe(ms(t), V(0, 0), SOFT), p.add_keyframe(ms(t + 200), V(0, -7), SOFT)) for t in range(IN + 200, OUTT - 300, 400)]
@emo("angel")
def _(f): react(f, None, None, lift=.01); halo(f)
@emo("devil")
def _(f): react(f, "lid", "smirk"); horns(f)
@emo("cheeky")
def _(f):
    react(f, (None, "arch"), "tongue"); t = f.mouth.tongue.transform.rotation; wobble(t, IN + 300, OUTT - 200, 9, 360)
@emo("sparkle-eyes")
def _(f): react(f, "ring", None, lift=.015); sparkles(f)
@emo("surprised")
def _(f): react(f, "big", "o", eyes_dur=90); p = f.pos; p.add_keyframe(ms(IN - 60), V(0, 0), ACCEL); p.add_keyframe(ms(IN + 90), V(0, -9), SOFT); p.add_keyframe(ms(IN + 400), V(0, -4), SOFT)
@emo("shocked")
def _(f): react(f, "big", "open", eyes_dur=90); shake(f.pos, IN + 100, IN + 500, 3)
@emo("mind-blown")
def _(f): react(f, "big", "open", eyes_dur=90); burst(f); shake(f.pos, IN + 120, IN + 700, 4, seed=5)
@emo("confused")
def _(f):
    react(f, None, "zigzag"); g = f.prop(); glyph_q(g, near_right(1.7, -1.9)); pop(g, IN + 150, 240, 1.15, out_t=OUTT); wobble(g.transform.rotation, IN + 500, OUTT - 200, 8, 500)
    wobble(f.mouth.zigzag.transform.position, IN + 300, OUTT - 200, 3, 240, base=V(0, 0)) if False else None
@emo("skeptical")
def _(f): react(f, ("lid", None), "flat", eyes_dur=200)
@emo("suspicious")
def _(f):
    react(f, "lid", "flat", eyes_dur=200)
    for e, sgn in ((f.eyeL, 1), (f.eyeR, -1)): r = e.lid.transform.rotation; r.add_keyframe(ms(IN), 0, STD); r.add_keyframe(ms(IN + 300), 14 * sgn, SOFT); r.add_keyframe(ms(OUTT), 14 * sgn, STD); r.add_keyframe(ms(OUTT + 200), 0, SOFT)
    p = f.eyeL.g.transform.position; p.add_keyframe(ms(IN + 400), V(0, 0), SOFT); p.add_keyframe(ms(IN + 900), V(6, 0), SOFT); p.add_keyframe(ms(IN + 1300), V(6, 0), SOFT); p.add_keyframe(ms(OUTT), V(0, 0), SOFT)
    p = f.eyeR.g.transform.position; p.add_keyframe(ms(IN + 400), V(0, 0), SOFT); p.add_keyframe(ms(IN + 900), V(6, 0), SOFT); p.add_keyframe(ms(IN + 1300), V(6, 0), SOFT); p.add_keyframe(ms(OUTT), V(0, 0), SOFT)
@emo("hmm")
def _(f): react(f, None, "flat"); glyph_dots(f, near_right(2.0, -1.4), IN + 150)
@emo("idea")
def _(f): react(f, "big", "o", eyes_dur=90); bulb(f); p = f.pos; p.add_keyframe(ms(IN), V(0, 0), DECEL); p.add_keyframe(ms(IN + 150), V(0, -8), SOFT); p.add_keyframe(ms(IN + 450), V(0, 0), SOFT)
@emo("curious")
def _(f):
    react(f, None, "small"); g = f.prop(); glyph_q(g, near_right(1.7, -1.9)); pop(g, IN + 150, 240, 1.15, out_t=OUTT)
    for e in (f.eyeL, f.eyeR): p = e.g.transform.position; p.add_keyframe(ms(IN), V(0, 0), STD); p.add_keyframe(ms(IN + 250), V(4, -4), SOFT); p.add_keyframe(ms(OUTT), V(4, -4), STD); p.add_keyframe(ms(OUTT + 250), V(0, 0), SOFT)
@emo("blank")
def _(f): status(f, "ring", "flat"); p = f.pos; p.add_keyframe(0, V(0, 0), HOLD)  # dead still: no breathe
@emo("alert")
def _(f): react(f, "big", "flat", eyes_dur=80); g = f.prop(); glyph_bang(g, near_right(1.6, -1.9)); pop(g, IN + 60, 180, 1.3, out_t=OUTT); shake(f.pos, IN, IN + 350, 3, step=40)
@emo("worried")
def _(f): react(f, None, "openfrown"); sweat(f)
@emo("nervous")
def _(f): react(f, None, "zigzag"); sweat(f, IN + 300); shake(f.eyeL.g.transform.position, IN + 200, OUTT, 1.6, step=70, seed=2); shake(f.eyeR.g.transform.position, IN + 200, OUTT, 1.6, step=70, seed=9)
@emo("scared")
def _(f):
    react(f, "big", "wavy", eyes_dur=90); sweat(f, IN + 200); shake(f.pos, IN + 100, OUTT, 2.2, step=60, seed=4)
    for i, t in enumerate(range(IN, OUTT, 250)): f.mouth.wavy_key(t, i * math.pi)
@emo("disappointed")
def _(f): react(f, "lid", "frown", eyes_dur=220, mouth_dur=260); p = f.pos; p.add_keyframe(ms(IN), V(0, 0), SOFT); p.add_keyframe(ms(IN + 500), V(0, 10), SOFT); p.add_keyframe(ms(OUTT), V(0, 10), SOFT); p.add_keyframe(ms(OUTT + 400), V(0, 0), SOFT)
@emo("annoyed")
def _(f): react(f, "lid", "flat", eyes_dur=160); anger_mark(f)
@emo("furious")
def _(f):
    react(f, "lid", "openfrown", eyes_dur=120)
    for e, sgn in ((f.eyeL, -1), (f.eyeR, 1)): r = e.lid.transform.rotation; r.add_keyframe(ms(IN), 0, STD); r.add_keyframe(ms(IN + 200), -22 * sgn, SOFT); r.add_keyframe(ms(OUTT), -22 * sgn, STD); r.add_keyframe(ms(OUTT + 200), 0, SOFT)
    anger_mark(f); shake(f.pos, IN + 250, IN + 900, 3.5, step=50, seed=6)
@emo("grumpy")
def _(f):
    react(f, "lid", "frown", eyes_dur=220, mouth_dur=260)
    for e, sgn in ((f.eyeL, -1), (f.eyeR, 1)): r = e.lid.transform.rotation; r.add_keyframe(ms(IN), 0, STD); r.add_keyframe(ms(IN + 300), -18 * sgn, SOFT); r.add_keyframe(ms(OUTT), -18 * sgn, STD); r.add_keyframe(ms(OUTT + 250), 0, SOFT)
@emo("pleading")
def _(f):
    react(f, "big", "openfrown", eyes_dur=140); tear_fall(f, EXL - .06, EY + .30, IN + 300, U(.09))
    for e in (f.eyeL, f.eyeR): s = e.variants["big"].transform.scale; anchor(e.variants["big"], e.c); [(s.add_keyframe(ms(t), V(100, 100), SOFT), s.add_keyframe(ms(t + 300), V(104, 104), SOFT)) for t in range(IN + 300, OUTT - 300, 600)]
@emo("heartbroken")
def _(f): react(f, None, "frown", mouth_dur=260); rain_cloud(f); p = f.pos; p.add_keyframe(ms(IN), V(0, 0), SOFT); p.add_keyframe(ms(IN + 600), V(0, 8), SOFT); p.add_keyframe(ms(OUTT), V(0, 8), SOFT); p.add_keyframe(ms(OUTT + 400), V(0, 0), SOFT)
@emo("bored")
def _(f):
    status(f, "lid", "flat"); p = f.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(1500), V(0, 4), SOFT); p.add_keyframe(ms(END), V(0, 0), SOFT)
    for e in (f.eyeL, f.eyeR): pp = e.g.transform.position; pp.add_keyframe(ms(900), V(0, 0), SOFT); pp.add_keyframe(ms(1300), V(-7, 0), SOFT); pp.add_keyframe(ms(1900), V(-7, 0), SOFT); pp.add_keyframe(ms(2300), V(0, 0), SOFT)
@emo("tired")
def _(f):
    status(f, "lid", "wavy"); moon(f)
    for i, t in enumerate(range(0, END + 1, 375)): f.mouth.wavy_key(t, i * math.pi / 2)
    for e in (f.eyeL, f.eyeR): s = e.lid.transform.scale; s.add_keyframe(0, V(100, 100), SOFT); s.add_keyframe(ms(1400), V(100, 82), SOFT); s.add_keyframe(ms(1800), V(100, 82), SOFT); s.add_keyframe(ms(2200), V(100, 100), SOFT)
@emo("yawn")
def _(f):
    react(f, "closed", "open", eyes_dur=260, mouth_dur=320); s = f.mouth.open.transform.scale; s.add_keyframe(ms(IN), V(70, 70), DECEL); s.add_keyframe(ms(IN + 500), V(100, 100), SOFT); s.add_keyframe(ms(OUTT - 200), V(100, 100), ACCEL); s.add_keyframe(ms(OUTT), V(70, 70), HOLD)
    p = f.pos; p.add_keyframe(ms(IN), V(0, 0), SOFT); p.add_keyframe(ms(IN + 500), V(0, -6), SOFT); p.add_keyframe(ms(OUTT), V(0, 2), SOFT); p.add_keyframe(ms(OUTT + 400), V(0, 0), SOFT)
@emo("dead")
def _(f):
    react(f, "x", "none", eyes_dur=60)
    for e in (f.eyeL, f.eyeR): s = e.variants["x"].transform.scale; s.add_keyframe(ms(IN), V(140, 140), DECEL); s.add_keyframe(ms(IN + 200), V(100, 100), SOFT)
    p = f.pos; p.add_keyframe(ms(IN), V(0, 0), DECEL); p.add_keyframe(ms(IN + 250), V(0, 14), SOFT); p.add_keyframe(ms(OUTT), V(0, 14), STD); p.add_keyframe(ms(OUTT + 300), V(0, 0), SOFT)
@emo("dizzy")
def _(f):
    react(f, "spiral", "wavy")
    for e, sgn in ((f.eyeL, 1), (f.eyeR, -1)): r = e.spiral.transform.rotation; r.add_keyframe(ms(IN), 0, LIN); r.add_keyframe(ms(OUTT), 360 * sgn, LIN)
    for i, t in enumerate(range(IN, OUTT + 1, 250)): f.mouth.wavy_key(t, i * math.pi / 2)
    p = f.pos
    for i, t in enumerate(range(IN, OUTT, 400)): p.add_keyframe(ms(t), V(0, 0), SOFT); p.add_keyframe(ms(t + 200), V(6 if i % 2 else -6, 0), SOFT)
@emo("sick")
def _(f):
    status(f, "closed", "wavy"); thermo(f)
    for i, t in enumerate(range(0, END + 1, 300)): f.mouth.wavy_key(t, i * math.pi / 2)
    shake(f.pos, 900, 1700, 1.8, step=80, seed=8)
@emo("masked")
def _(f): react(f, None, None, lift=.01, blink_at=500); mask(f); f.blink(1600)
@emo("speechless")
def _(f):
    react(f, None, "dots", blink_at=300)
    for i, g in enumerate(f.mouth.dotgroups): s = g.transform.scale; s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(IN + i * 200), V(0, 0), DECEL); s.add_keyframe(ms(IN + i * 200 + 150), V(120, 120), SOFT); s.add_keyframe(ms(IN + i * 200 + 260), V(100, 100), HOLD)
@emo("zipped")
def _(f):
    react(f, None, "zip", blink_at=400)
    for i, g in enumerate(f.mouth.zipteeth): s = g.transform.scale; anchor(g, (OX + .5 * M + (i - 3) * RP * .5, OY + (EY + .22) * M)); s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(IN + 100 + i * 60), V(0, 0), DECEL); s.add_keyframe(ms(IN + 220 + i * 60), V(100, 100), HOLD)
@emo("working")
def _(f):
    status(f, "dot", "flat", blink_at=1300); glasses(f)
    for e in (f.eyeL, f.eyeR):
        p = e.g.transform.position
        for i, t in enumerate(range(0, END, 600)): p.add_keyframe(ms(t), V(-5 if i % 2 else 5, 0), STD); p.add_keyframe(ms(t + 200), V(5 if i % 2 else -5, 0), HOLD)
@emo("reading")
def _(f):
    status(f, "look", "flat"); glasses(f)
    for e in (f.eyeL, f.eyeR):
        p = e.pupil.position; base = p.value
        for i, t in enumerate(range(0, END, 750)): p.add_keyframe(ms(t), base + V(-8, 0), STD); p.add_keyframe(ms(t + 550), base + V(8, 0), HOLD)
@emo("done")
def _(f): react(f, "arch", None, lift=.02); checkmark(f); p = f.pos; p.add_keyframe(ms(IN), V(0, 0), DECEL); p.add_keyframe(ms(IN + 180), V(0, -8), SOFT); p.add_keyframe(ms(IN + 480), V(0, 0), SOFT)
@emo("loading")
def _(f): status(f, "dot", "flat", blink_at=1900); spinner(f)
@emo("waiting")
def _(f):
    status(f, "dot", "flat", blink_at=2200); hourglass(f)
    for e in (f.eyeL, f.eyeR): p = e.g.transform.position; p.add_keyframe(ms(600), V(0, 0), SOFT); p.add_keyframe(ms(1000), V(6, -4), SOFT); p.add_keyframe(ms(1700), V(6, -4), SOFT); p.add_keyframe(ms(2100), V(0, 0), SOFT)
@emo("error")
def _(f):
    react(f, "x", "flat", eyes_dur=60); g = f.prop(); glyph_bang(g, near_right(1.7, -1.9), 1.2, RED); pop(g, IN + 40, 160, 1.35, out_t=OUTT); shake(f.pos, IN, IN + 400, 4, step=40, seed=11)
    for e in (f.eyeL, f.eyeR): s = e.variants["x"].transform.scale; s.add_keyframe(ms(IN), V(150, 150), DECEL); s.add_keyframe(ms(IN + 180), V(100, 100), SOFT)
@emo("focus")
def _(f): status(f, "small", "flat"); p = f.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(1500), V(0, -1.5), SOFT); p.add_keyframe(ms(END), V(0, 0), SOFT)
@emo("coffee")
def _(f): status(f, "lid", None); coffee(f)
@emo("vibing")
def _(f):
    status(f, "closed", None); headphones(f); p = f.pos
    for i, t in enumerate(range(0, END, 500)): p.add_keyframe(ms(t), V(0, 0), SOFT); p.add_keyframe(ms(t + 250), V(3 if i % 2 else -3, -5), SOFT)
    f.mouth.link_key(0, 0); f.mouth.link_key(ms(1500) and 1500, .012, SOFT); f.mouth.link_key(END, 0, SOFT)
@emo("singing")
def _(f):
    status(f, "closed", "open"); music_note(f); s = f.mouth.open.transform.scale
    for i, t in enumerate(range(0, END, 500)): s.add_keyframe(ms(t), V(70, 70), SOFT); s.add_keyframe(ms(t + 250), V(70, 95), SOFT)
    p = f.pos
    for i, t in enumerate(range(0, END, 1000)): p.add_keyframe(ms(t), V(0, 0), SOFT); p.add_keyframe(ms(t + 500), V(-3 if i % 2 else 3, -3), SOFT)
@emo("sleepy")
def _(f):
    status(f, "lid", "o"); moon(f); p = f.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(1500), V(0, 5), SOFT); p.add_keyframe(ms(END), V(0, 0), SOFT)
    for e in (f.eyeL, f.eyeR): s = e.lid.transform.scale; s.add_keyframe(0, V(100, 100), SOFT); s.add_keyframe(ms(1500), V(100, 70), SOFT); s.add_keyframe(ms(END), V(100, 100), SOFT)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    names = sys.argv[1:] or list(E)
    for n in names:
        f = Face(); E[n](f); p = f.save(OUT / f"rumi-mark-{n}.json"); print("built", p.name, p.stat().st_size // 1024, "KB")
    print(len(names), "->", OUT)
