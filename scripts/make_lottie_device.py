#!/usr/bin/env python3
"""Device face set for Rumi (desk body / voice app): turn-taking core, system conditions, level-driven ramps.

usage: python3 scripts/make_lottie_device.py [name ...]   -> lottie-device/rumi-dev-<name>.json + .gif
Kinds: loop (base state), oneshot (play once, ends at rest), ramp (frame = level: app seeks 0..59 by audio level).
Spec: docs/face-states.md
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rumi_mark_rig import *
import make_lottie_mark as MK
from make_lottie_meeting import render_gif

OUT = pathlib.Path(__file__).resolve().parent.parent / "lottie-device"
E = {}
def emo(name, seconds, kind="loop"):
    def deco(fn): E[name] = (fn, seconds, kind); return fn
    return deco


def dim(f, pct): f.layer.transform.opacity.value = pct


def manual_mouth(f, stroke_vis=100, fill_vis=0):
    m = f.mouth; m.timeline = None
    m.stroke_group.transform.opacity.value = stroke_vis; m.fm.group.transform.opacity.value = fill_vis
    m.fm.group.transform.scale.value = V(100, 100)
    for g in (m.teethbar, m.tongue, m.dg, m.zg): g.transform.opacity.value = 0
    return m


# ---------------- turn-taking core ----------------
@emo("asleep", 6.0)
def _(f):
    dim(f, 60); f.eyes("closed", 0); f.mouth.set("small", 0)
    p = f.pos; p.add_keyframe(0, V(0, 2), SOFT); p.add_keyframe(ms(3000), V(0, -1), SOFT); p.add_keyframe(ms(6000), V(0, 2), SOFT)


@emo("wake", 2.0, "oneshot")
def _(f):
    # starts asleep, snaps awake within 150 ms, bobs up with a spring, settles into the resting mark
    o = f.layer.transform.opacity; o.add_keyframe(0, 60, DECEL); o.add_keyframe(ms(150), 100, HOLD)
    f.eyes("closed", 0); f.eyes("dot", 60, 110); f.mouth.set("small", 0); f.mouth.set("link", 80, 160)
    p = f.pos; p.add_keyframe(0, V(0, 2), DECEL); overshoot(p, ms(60), V(0, 2), V(0, -10), 320, .15); p.add_keyframe(ms(700), V(0, -10), SOFT); p.add_keyframe(ms(1300), V(0, 0), SOFT)
    f.blink(1400)


@emo("listening-level", 2.0, "ramp")
def _(f):
    # frame 0 = silence, frame 59 = loud: arcs bow deeper and the smile lifts with the user's voice level
    f.eyes("closed", 0); m = manual_mouth(f)
    m.sm.key(0, normalize(m.link_pts(0), NM, False), LIN); m.sm.key(1967, normalize(m.link_pts(.03), NM, False), LIN)
    for e in (f.eyeL, f.eyeR):
        g = e.morph_group; sc = g.transform.scale; sc.add_keyframe(0, V(100, 100), LIN); sc.add_keyframe(ms(1967), V(112, 135), LIN)


@emo("didnt-catch", 2.5, "oneshot")
def _(f):
    f.blink(200); f.mouth.set("small", 500, 160); f.mouth.set("link", 1900, 160)
    p = f.pos; r = f.layer.transform.rotation; s = f.layer.transform.scale; f.layer.transform.anchor_point.value = V(256, 240); f.layer.transform.position.value = V(256, 240)
    p.add_keyframe(0, V(256, 240), STD); p.add_keyframe(ms(500), V(256, 240), DECEL); p.add_keyframe(ms(800), V(256, 250), SOFT); p.add_keyframe(ms(1800), V(256, 250), STD); p.add_keyframe(ms(2200), V(256, 240), SOFT)
    r.add_keyframe(ms(500), 0, DECEL); r.add_keyframe(ms(800), 7, SOFT); r.add_keyframe(ms(1800), 7, STD); r.add_keyframe(ms(2200), 0, SOFT)
    s.add_keyframe(ms(500), V(100, 100), DECEL); s.add_keyframe(ms(800), V(105, 105), SOFT); s.add_keyframe(ms(1800), V(105, 105), STD); s.add_keyframe(ms(2200), V(100, 100), SOFT)
    g = f.prop(); MK.glyph_q(g, near_right(1.6, -1.9), .9); pop(g, 750, 220, 1.15, out_t=1800)


@emo("processing", 3.0)
def _(f):
    f.breathe(2, 3000)
    for e in (f.eyeL, f.eyeR): p = e.g.transform.position; p.add_keyframe(0, V(4, -4), SOFT); p.add_keyframe(ms(1500), V(-4, -4), SOFT); p.add_keyframe(ms(3000), V(4, -4), SOFT)
    f.mouth.set("dots", 0)
    for i, g in enumerate(f.mouth.dotgroups):
        s = g.transform.scale
        for t in range(0, 3000, 750): s.add_keyframe(ms(t + i * 120), V(100, 100), SOFT); s.add_keyframe(ms(t + i * 120 + 130), V(165, 165), SOFT); s.add_keyframe(ms(t + i * 120 + 260), V(100, 100), SOFT)


@emo("still-working", 4.0)
def _(f):
    # after ~3 s of processing: calmer, so a long wait doesn't read as stuck
    f.breathe(2, 4000); f.eyes("lid", 0); f.mouth.set("dots", 0)
    for i, g in enumerate(f.mouth.dotgroups):
        o = g.transform.opacity
        for t in range(0, 4000, 1300): o.add_keyframe(ms(t + i * 200), 100, SOFT); o.add_keyframe(ms(t + i * 200 + 250), 35, SOFT); o.add_keyframe(ms(t + i * 200 + 500), 100, SOFT)


@emo("speaking-level", 2.0, "ramp")
def _(f):
    # frame 0 = mouth closed (flat line), frame 59 = fully open: seek by Rumi's own audio envelope
    f.blink(0) if False else None
    m = manual_mouth(f, stroke_vis=100, fill_vis=100)
    m.sm.key(0, "flat", LIN); m.sm.key(1967, "flat", LIN)
    m.stroke_group.transform.opacity.add_keyframe(0, 100, LIN); m.stroke_group.transform.opacity.add_keyframe(ms(300), 0, HOLD)
    sc = m.fm.group.transform.scale; sc.add_keyframe(0, V(100, 0), LIN); sc.add_keyframe(ms(1967), V(100, 100), LIN)


@emo("done-settle", 1.5, "oneshot")
def _(f):
    f.eyes("arch", 0); f.eyes("dot", 300, 160); f.mouth.set("open", 0); f.mouth.set("link", 250, 180)
    p = f.pos; p.add_keyframe(0, V(0, -4), DECEL); p.add_keyframe(ms(400), V(0, 3), SOFT); p.add_keyframe(ms(900), V(0, 0), SOFT)


# ---------------- system conditions ----------------
@emo("no-network", 3.0)
def _(f):
    f.breathe(2, 3000); f.eyes("small", 0); f.mouth.set("flat", 0); f.blink(1600)
    g = f.prop(); cx, cy = near_right(1.9, -2.0); r = RP * 1.0
    for rr in (1.0, .66, .33): path(g, arc_abs(cx - r * rr, cy + r * .6 - r * rr * .55, cx + r * rr, cy + r * .6 - r * rr * .55, -r * rr * .45, 5), stroke=NAVY, width=SW * .8)
    ellipse(g, (cx, cy + r * .7), SW * .55); anchor(g, (cx, cy))
    s = f.prop(); line(s, (cx - r * 1.1, cy - r * .9), (cx + r * 1.1, cy + r * 1.1), RED, SW * .9); anchor(s, (cx, cy))
    o = s.transform.opacity
    for t in range(0, 3000, 1000): o.add_keyframe(ms(t), 100, SOFT); o.add_keyframe(ms(t + 500), 30, SOFT)
    o.add_keyframe(ms(3000), 100, SOFT)


def battery(f, fill_color):
    """Battery outline + a fill Rect. Returns (group, set_fill(t_ms, pct, ease)) so callers animate the level."""
    g = f.prop(); cx, cy = near_right(1.9, -2.0); w, h = RP * 2.0, RP * 1.0; iw, ih = w - SW * 1.6, h - SW * 1.6; x0 = cx - iw / 2
    rc = rrect(g, (cx, cy), iw, ih, h * .08, fill_color)                        # fill (on top: first in list)
    rrect(g, (cx, cy), w - SW * .8, h - SW * .8, h * .12, WHITE)               # white inside
    rrect(g, (cx, cy), w, h, h * .2); rrect(g, (cx + w / 2 + h * .12, cy), h * .22, h * .45, h * .08)   # body + cap (behind)
    def set_fill(t, pct, ease=LIN):
        rc.size.add_keyframe(ms(t), V(iw * pct, ih), ease); rc.position.add_keyframe(ms(t), V(x0 + iw * pct / 2, cy), ease)
    return g, set_fill


@emo("charging", 3.0)
def _(f):
    f.breathe(2, 3000); f.mouth.set("small", 0); f.blink(2000)
    g, set_fill = battery(f, "#2E8B57")
    set_fill(0, .15); set_fill(2400, 1.0); set_fill(2750, 1.0, HOLD); set_fill(2800, .15, HOLD)
    b = f.prop(); cx, cy = near_right(1.9, -2.0); path(b, [((cx + 3, cy - 11), (0, 0), (0, 0)), ((cx - 4, cy + 1), (0, 0), (0, 0)), ((cx + 1, cy + 1), (0, 0), (0, 0)), ((cx - 3, cy + 11), (0, 0), (0, 0)), ((cx + 5, cy - 2), (0, 0), (0, 0)), ((cx, cy - 2), (0, 0), (0, 0))], fill=WHITE, stroke=NAVY, width=1.2, closed=True)


@emo("low-battery", 3.0)
def _(f):
    f.breathe(1.5, 3000); f.eyes("lid", 0); f.mouth.set("flat", 0)
    g, set_fill = battery(f, RED); set_fill(0, .12, HOLD)
    o = g.transform.opacity
    for t in range(0, 3000, 1000): o.add_keyframe(ms(t), 100, SOFT); o.add_keyframe(ms(t + 500), 45, SOFT)
    o.add_keyframe(ms(3000), 100, SOFT)
    p = f.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(1500), V(0, 5), SOFT); p.add_keyframe(ms(3000), V(0, 0), SOFT)


@emo("updating", 4.0)
def _(f):
    f.breathe(2, 4000); f.eyes("closed", 0); f.mouth.set("small", 0)
    g = f.prop(); cx, cy = near_right(1.9, -2.1); r = RP * .8
    ellipse(g, (cx, cy), r, fill=None, stroke=NAVY, width=SW * .9); tr = g.shapes[-2].add_shape(objects.Trim()); tr.end.add_keyframe(0, 0, LIN); tr.end.add_keyframe(ms(3600), 100, HOLD); tr.end.add_keyframe(ms(3990), 100, HOLD)
    ellipse(g, (cx, cy), r, fill=None, stroke="#DDE3EA", width=SW * .9)   # track, behind
    anchor(g, (cx, cy)); g.transform.rotation.value = -90


@emo("booting", 2.5, "oneshot")
def _(f):
    m = manual_mouth(f); m.sm.key(0, "link", LIN)
    tr = m.stroke_group.add_shape(objects.Trim()); tr.end.add_keyframe(0, 0, HOLD); tr.end.add_keyframe(ms(600), 0, DECEL); tr.end.add_keyframe(ms(1300), 100, HOLD)
    for k, e in enumerate((f.eyeL, f.eyeR)):
        sc = e.morph_group.transform.scale; sc.add_keyframe(0, V(0, 0), HOLD); sc.add_keyframe(ms(150 + k * 180), V(0, 0), DECEL); sc.add_keyframe(ms(330 + k * 180), V(118, 118), SOFT); sc.add_keyframe(ms(450 + k * 180), V(100, 100), HOLD)
    f.blink(1700)


@emo("shutdown", 2.0, "oneshot")
def _(f):
    m = manual_mouth(f); m.sm.key(0, "link", LIN)
    tr = m.stroke_group.add_shape(objects.Trim()); tr.start.add_keyframe(0, 0, HOLD); tr.start.add_keyframe(ms(500), 0, ACCEL); tr.start.add_keyframe(ms(1200), 100, HOLD)
    for k, e in enumerate((f.eyeL, f.eyeR)):
        e.m.key(0, "dot", STD); e.m.key(700 + k * 120, "dot", ACCEL); e.m.key(850 + k * 120, "blink", HOLD)
        sc = e.morph_group.transform.scale; sc.add_keyframe(ms(1100 + k * 120), V(100, 100), ACCEL); sc.add_keyframe(ms(1400 + k * 120), V(0, 100), HOLD)
    o = f.layer.transform.opacity; o.add_keyframe(ms(1500), 100, LIN); o.add_keyframe(ms(1950), 0, HOLD)


def volume(f, up):
    f.blink(150)
    f.mouth.link_key(0, 0); f.mouth.link_key(250, 0, STD); f.mouth.link_key(500, -.015 if up else .02, SOFT); f.mouth.link_key(850, -.015 if up else .02, STD); f.mouth.link_key(1150, 0, SOFT)
    cx, cy = near_right(1.6, -1.6); r = RP * .9
    for k, rr in enumerate((.45, .8, 1.15)):
        g = f.prop(); path(g, arc_abs(cx + r * rr * .7, cy - r * rr * .8, cx + r * rr * .7, cy + r * rr * .8, 0, 5), stroke=NAVY, width=SW * .8)
        pts = g.shapes[-2].shapes[0].shape.value   # bend the vertical line into a right-facing arc
        import lottie.objects as LO; b = LO.Bezier()
        for j in range(5):
            t = j / 4; x = cx + r * rr * .55 + r * rr * .45 * math.sin(math.pi * t); y = cy - r * rr * .8 + r * rr * 1.6 * t
            b.add_point(V(x, y), V(0, -r * rr * .3 if 0 < j < 4 else 0), V(0, r * rr * .3 if 0 < j < 4 else 0))
        g.shapes[-2].shapes[0].shape.value = b
        anchor(g, (cx, cy)); order = k if up else 2 - k
        pop(g, 300 + order * 120, 180, 1.15, out_t=950 - (2 - order) * 60 if not up else 950 + order * 0, out_dur=150) if up else pop(g, 250, 140, 1.0, out_t=450 + order * 130, out_dur=150)


@emo("volume-up", 1.3, "oneshot")
def _(f): volume(f, True)
@emo("volume-down", 1.3, "oneshot")
def _(f): volume(f, False)


@emo("dnd", 4.0)
def _(f):
    dim(f, 70); f.breathe(1.5, 4000); f.eyes("lid", 0); f.mouth.set("flat", 0)
    g = f.prop(); cx, cy = near_right(1.9, -2.2); r = RP * .75
    ellipse(g, (cx, cy), r * .72, fill=None, stroke=NAVY, width=r * .55); tr = g.shapes[-2].add_shape(objects.Trim()); tr.start.value = 12; tr.end.value = 70
    anchor(g, (cx, cy)); rot = g.transform.rotation; rot.add_keyframe(0, -6, SOFT); rot.add_keyframe(ms(2000), 6, SOFT); rot.add_keyframe(ms(4000), -6, SOFT)


@emo("timer-running", 3.0)
def _(f):
    f.breathe(2, 3000); f.blink(1200)
    g = f.prop(); cx, cy = near_right(1.9, -2.1); r = RP * .8
    ellipse(g, (cx, cy), r, fill=None, stroke=NAVY, width=SW * .8); line(g, (cx, cy - r - 4), (cx, cy - r - 8), NAVY, SW * .8)
    h = f.prop(); line(h, (cx, cy), (cx, cy - r * .7), NAVY, SW * .7); anchor(h, (cx, cy)); rot = h.transform.rotation; rot.add_keyframe(0, 0, LIN); rot.add_keyframe(ms(3000), 360, LIN)


@emo("timer-done", 2.0, "oneshot")
def _(f):
    f.eyes("big", 100, 90); f.eyes("dot", 1500, 140); f.mouth.set("o", 100, 120); f.mouth.set("link", 1500, 160)
    g = f.prop(); cx, cy = near_right(1.9, -2.1); r = RP * .9
    path(g, [((cx - r * .8, cy + r * .5), (0, 0), (0, 0)), ((cx - r * .6, cy - r * .3), (0, 0), (0, r * .9)), ((cx + r * .6, cy - r * .3), (0, r * .9), (0, 0)), ((cx + r * .8, cy + r * .5), (0, 0), (0, 0))], fill=NAVY, closed=True)
    ellipse(g, (cx, cy + r * .75), r * .2); anchor(g, (cx, cy - r * .3)); pop(g, 80, 200, 1.2, out_t=1500)
    rot = g.transform.rotation
    for i, t in enumerate(range(250, 1300, 110)): rot.add_keyframe(ms(t), 18 if i % 2 == 0 else -18, SOFT)
    rot.add_keyframe(ms(1400), 0, SOFT)
    shake(f.pos, 300, 900, 2.5, step=55, seed=4)


@emo("nudge", 2.5, "oneshot")
def _(f):
    f.blink(150); f.mouth.link_key(0, 0); f.mouth.link_key(700, 0, STD); f.mouth.link_key(1000, -.012, SOFT); f.mouth.link_key(1700, -.012, STD); f.mouth.link_key(2100, 0, SOFT)
    for e in (f.eyeL, f.eyeR):   # glance toward the user, hold, back
        p = e.g.transform.position; p.add_keyframe(ms(600), V(0, 0), STD); p.add_keyframe(ms(850), V(-7, 2), SOFT); p.add_keyframe(ms(1700), V(-7, 2), STD); p.add_keyframe(ms(2000), V(0, 0), SOFT)
    p = f.pos; p.add_keyframe(ms(600), V(0, 0), DECEL); p.add_keyframe(ms(800), V(-6, -4), SOFT); p.add_keyframe(ms(1700), V(-6, -4), STD); p.add_keyframe(ms(2050), V(0, 0), SOFT)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for n in (sys.argv[1:] or list(E)):
        fn, sec, kind = E[n]; f = Face(sec); fn(f); p = f.save(OUT / f"rumi-dev-{n}.json")
        render_gif(p, OUT / f"rumi-dev-{n}.gif"); print("built", n, kind, p.stat().st_size // 1024, "KB")
