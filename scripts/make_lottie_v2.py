#!/usr/bin/env python3
"""World of Rumi -> Lottie v2: real keyframes, real easing, research-backed timing.

usage: python3 scripts/make_lottie_v2.py [emotion ...]
Every loop is 3.0s (Telegram TGS cap), structured idle -> anticipation -> action -> settle -> idle.
Props are separate groups anchored at their pivot so they can swing/bob independently.
"""
import sys, pathlib, json, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rumi_rig import *

OUT = pathlib.Path(__file__).resolve().parent.parent / "lottie"
TONGUE, HAT, TEAR, LID, BUBBLE, WHITE = col("#E8736F"), col("#D6362B"), col("#6FA8DC"), col("#9AA3AD"), col("#B8C4D0"), col("#FFFFFF")


def breathe(r, amp=1.5, period_ms=3000):
    """Idle breath: 15-20 breaths/min -> one full cycle per 3s loop, sinusoidal via two SOFT keys."""
    p = r.face_pos(); p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(period_ms / 2), V(0, -amp), SOFT); p.add_keyframe(ms(period_ms), V(0, 0), SOFT)


def happy():
    r = Rig(); breathe(r)
    r.blink(ms(900))
    r.mouth_key(0, 1.0); r.mouth_key(ms(1700), 1.0, STD); r.mouth_key(ms(1950), 1.14, SOFT); r.mouth_key(ms(2500), 1.0, SOFT)
    return r


def tongue():
    r = Rig(); breathe(r, 1.0)
    # mouth opens a little as the tongue comes out (anticipation: tiny smile squeeze first)
    r.mouth_key(0, 1.0); r.mouth_key(ms(700), 1.0, STD); r.mouth_key(ms(820), 0.92, SOFT); r.mouth_key(ms(1050), 1.12, SOFT); r.mouth_key(ms(2200), 1.12, STD); r.mouth_key(ms(2500), 1.0, SOFT)
    r.blink("l", ms(1300), dash=True) if False else None
    g = r.group(behind=True)  # tongue slides out from behind the curve
    ellipse(g, 0, 0, 7, 9, TONGUE)
    g.transform.anchor_point.value = V(0, -9); g.transform.position.value = V(86, EY + 21)
    sc = g.transform.scale; sc.add_keyframe(0, V(100, 0), HOLD); sc.add_keyframe(ms(850), V(100, 0), DECEL)
    sc.add_keyframe(ms(1050), V(100, 112), SOFT); sc.add_keyframe(ms(1180), V(100, 100), SOFT)   # overshoot then settle
    sc.add_keyframe(ms(2200), V(100, 100), ACCEL); sc.add_keyframe(ms(2420), V(100, 0), HOLD)
    rot = g.transform.rotation   # wiggle while out (secondary action, starts 100ms after it lands)
    for i, t in enumerate(range(1300, 2100, 200)): rot.add_keyframe(ms(t), (-7 if i % 2 else 7), SOFT)
    rot.add_keyframe(ms(2200), 0, SOFT)
    return r


def santa():
    r = Rig(); breathe(r)
    g = r.group(); hx, hy = RX, EY - R + 2
    path(g, [((hx - 14, hy), (0, 0), (0, 0)), ((hx - 2, hy - 26), (0, 0), (8, -8)), ((hx + 20, hy - 18), (2, -8), (0, 0)), ((hx + 14, hy), (0, 0), (0, 0))], color=HAT, closed=True)
    path(g, [((hx - 16, hy - 1), (0, 0), (0, 0)), ((hx + 16, hy - 1), (0, 0), (0, 0)), ((hx + 16, hy + 5), (0, 0), (0, 0)), ((hx - 16, hy + 5), (0, 0), (0, 0))], color=WHITE, stroke=NAVY, width=1.2, closed=True)
    e = ellipse(g, hx + 20, hy - 18, 4.5, 4.5, WHITE); g.add_shape(objects.Stroke(NAVY, 1.2))
    g.transform.anchor_point.value = V(hx, hy + 2); g.transform.position.value = V(hx, hy + 2)
    rot = g.transform.rotation   # hat nods with a spring when the head bobs
    rot.add_keyframe(0, -6, STD); rot.add_keyframe(ms(1000), -6, DECEL)
    t = overshoot(rot, ms(1000), -6, 8, 320, 0.12); rot.add_keyframe(ms(2000), 8, DECEL); overshoot(rot, ms(2000), 8, -6, 320, 0.12)
    r.blink(ms(1400))
    return r


def wink():
    r = Rig(); breathe(r, 1.0)
    e = r.eyes["r"].size
    e.add_keyframe(0, V(20, 20), STD); e.add_keyframe(ms(950), V(20, 20), ACCEL); e.add_keyframe(ms(1050), V(22, 22), SOFT)  # anticipation widen
    e.add_keyframe(ms(1150), V(28, 2.6), HOLD); e.add_keyframe(ms(1550), V(28, 2.6), DECEL); e.add_keyframe(ms(1680), V(20, 20), SOFT)
    r.mouth_key(0, 1.0); r.mouth_key(ms(1150), 1.0, STD); r.mouth_key(ms(1400), 1.2, SOFT); r.mouth_key(ms(2000), 1.0, SOFT)
    g = r.group()
    for ang, ln in ((-60, 9), (-25, 11), (10, 9)):
        x0 = RX + 14 * math.cos(math.radians(ang)); y0 = EY - 6 + 14 * math.sin(math.radians(ang))
        line(g, (x0, y0), (x0 + ln * math.cos(math.radians(ang)), y0 + ln * math.sin(math.radians(ang))), NAVY, 3)
    g.transform.anchor_point.value = V(RX + 14, EY - 6); g.transform.position.value = V(RX + 14, EY - 6)
    sc = g.transform.scale; sc.add_keyframe(0, V(0, 0), HOLD); sc.add_keyframe(ms(1200), V(0, 0), DECEL)
    sc.add_keyframe(ms(1330), V(112, 112), SOFT); sc.add_keyframe(ms(1430), V(100, 100), HOLD); sc.add_keyframe(ms(1650), V(100, 100), ACCEL); sc.add_keyframe(ms(1800), V(0, 0), HOLD)
    return r


def sad():
    r = Rig(); breathe(r, 1.0)
    r.mouth_key(0, -0.55); r.mouth_key(ms(3000), -0.55)   # frown held all loop; the story is the tear
    # eyes sag slightly (lids)
    r.eye_key("both", 0, 20, 17); r.eye_key("both", ms(3000), 20, 17)
    g = r.group(); teardrop(g, 0, 0, 9, TEAR)
    g.transform.anchor_point.value = V(0, -9); g.transform.position.value = V(RX + 10, EY + 8)
    sc = g.transform.scale; sc.add_keyframe(0, V(0, 0), HOLD); sc.add_keyframe(ms(600), V(0, 0), DECEL); sc.add_keyframe(ms(1100), V(100, 100), SOFT)  # tear forms slowly
    pos = g.transform.position; pos.add_keyframe(ms(1400), V(RX + 10, EY + 8), ACCEL); pos.add_keyframe(ms(2000), V(RX + 10, EY + 48), STD)  # then falls
    fade(g, ms(600), ms(1100), ms(1800), ms(2000))
    return r


def angry():
    r = Rig(color=RED)
    r.mouth_key(0, -0.5); r.mouth_key(ms(3000), -0.5)
    r.eye_key("both", 0, 20, 17); r.eye_key("both", ms(3000), 20, 17)
    g = r.group()
    line(g, (LX - 12, EY - 19), (LX + 10, EY - 14), RED, 5); line(g, (RX + 12, EY - 19), (RX - 10, EY - 14), RED, 5)
    # brows press down harder as anger builds (anticipation of the shake), then the whole face shakes, then settles
    bp = g.transform.position; bp.add_keyframe(0, V(0, 0), SOFT); bp.add_keyframe(ms(900), V(0, 3), SOFT); bp.add_keyframe(ms(1900), V(0, 3), SOFT); bp.add_keyframe(ms(2400), V(0, 0), SOFT)
    lp = r.layer.transform.position; base = V(0, 0)
    lp.add_keyframe(0, base, HOLD); lp.add_keyframe(ms(1000), base, easing.Linear())
    import random; random.seed(7)
    for i in range(12):  # 1000-1600ms: 12 shakes of 50ms, amplitude decays
        a = 2.4 * (1 - i / 14); lp.add_keyframe(ms(1000 + 50 * (i + 1)), V(random.uniform(-a, a), random.uniform(-a * 0.5, a * 0.5)), easing.Linear())
    lp.add_keyframe(ms(1700), base, SOFT)
    return r


def chef():
    r = Rig(); breathe(r)
    g = r.group(); hx, hy = LX, EY - R + 1
    path(g, [((hx - 13, hy), (0, 0), (0, 0)), ((hx - 13, hy - 9), (0, 0), (-8, -14)), ((hx - 4, hy - 23), (-6, 2), (2, -8)), ((hx + 6, hy - 23), (-2, -8), (6, 2)),
             ((hx + 13, hy - 9), (8, -14), (0, 0)), ((hx + 13, hy), (0, 0), (0, 0))], color=WHITE, stroke=NAVY, width=2, closed=True)
    g.transform.anchor_point.value = V(hx, hy); g.transform.position.value = V(hx, hy)
    rot = g.transform.rotation; rot.add_keyframe(0, 0, SOFT); rot.add_keyframe(ms(1500), -4, SOFT); rot.add_keyframe(ms(3000), 0, SOFT)
    w = r.group(); wx, wy = LX - 18, EY + 24
    line(w, (0, 0), (0, -20), NAVY, 3); ellipse_stroke = w.add_shape(objects.Ellipse()); ellipse_stroke.position.value = V(0, -28); ellipse_stroke.size.value = V(12, 18)
    st = w.add_shape(objects.Stroke(NAVY, 2)); line(w, (0, -20), (0, -37), NAVY, 2)
    w.transform.anchor_point.value = V(0, 0); w.transform.position.value = V(wx, wy)
    rot = w.transform.rotation   # stir: 3 strokes, each with overshoot, 900-2100ms, then rest
    rot.add_keyframe(0, -18, STD); rot.add_keyframe(ms(900), -18, DECEL)
    t = ms(900)
    for tgt in (22, -18, 22):
        t = overshoot(rot, t, rot.get_value(t), tgt, 380, 0.1)
    rot.add_keyframe(ms(2500), 22, DECEL); overshoot(rot, ms(2500), 22, -18, 400, 0.08)
    r.blink(ms(2300))
    return r


def tie():
    r = Rig(); breathe(r, 1.0)
    tx, ty = 80, EY + 30
    c = r.group()
    path(c, [((tx - 14, ty - 6), (0, 0), (0, 0)), ((tx - 4, ty + 2), (0, 0), (0, 0)), ((tx - 5, ty - 8), (0, 0), (0, 0))], color=WHITE, stroke=NAVY, width=2, closed=True)
    path(c, [((tx + 14, ty - 6), (0, 0), (0, 0)), ((tx + 4, ty + 2), (0, 0), (0, 0)), ((tx + 5, ty - 8), (0, 0), (0, 0))], color=WHITE, stroke=NAVY, width=2, closed=True)
    k = r.group()
    path(k, [((-5, 0), (0, 0), (0, 0)), ((5, 0), (0, 0), (0, 0)), ((3, 8), (0, 0), (0, 0)), ((-3, 8), (0, 0), (0, 0))], color=NAVY, closed=True)
    path(k, [((-3, 8), (0, 0), (0, 0)), ((3, 8), (0, 0), (0, 0)), ((5, 26), (0, 0), (0, 0)), ((0, 32), (0, 0), (0, 0)), ((-5, 26), (0, 0), (0, 0))], color=NAVY, closed=True)
    k.transform.anchor_point.value = V(0, 0); k.transform.position.value = V(tx, ty)
    rot = k.transform.rotation   # pendulum: follow-through lags the breath by ~100ms
    rot.add_keyframe(ms(100), 0, SOFT); rot.add_keyframe(ms(850), 7, SOFT); rot.add_keyframe(ms(1600), -7, SOFT); rot.add_keyframe(ms(2350), 5, SOFT); rot.add_keyframe(ms(3000), 0, SOFT)
    r.blink(ms(1900))
    return r


def crying():
    r = Rig()
    r.mouth_key(0, -0.6); r.mouth_key(ms(3000), -0.6)
    r.eye_key("both", 0, 20, 16); r.eye_key("both", ms(3000), 20, 16)
    p = r.face_pos()  # sob: small bob every 400ms with a hold between
    for i, t in enumerate(range(0, 3000, 400)):
        p.add_keyframe(ms(t), V(0, 0), DECEL); p.add_keyframe(ms(t + 120), V(0, 2.5), SOFT); p.add_keyframe(ms(t + 260), V(0, 0), SOFT)
    for x, offset in ((LX - 7, 0), (RX + 7, 500), (LX - 7, 1500), (RX + 7, 2000)):
        g = r.group(); teardrop(g, 0, 0, 8, TEAR)
        y0 = EY + 12; pos = g.transform.position
        pos.add_keyframe(0, V(x, y0), HOLD); pos.add_keyframe(ms(offset), V(x, y0), ACCEL); pos.add_keyframe(ms(offset + 700), V(x, y0 + 44), STD)
        fade(g, ms(offset), ms(offset + 150), ms(offset + 550), ms(offset + 700))
    return r


def thinking():
    r = Rig(); breathe(r, 1.0)
    # eyes drift up-right (looking at the bubble) with a small tilt, then return
    for e in r.eyes.values():
        pp = e.position; base = pp.value
        pp.add_keyframe(0, base, STD); pp.add_keyframe(ms(500), base, DECEL); pp.add_keyframe(ms(800), base + V(3, -3), SOFT); pp.add_keyframe(ms(2300), base + V(3, -3), STD); pp.add_keyframe(ms(2650), base, SOFT)
    r.mouth_key(0, 0.55); r.mouth_key(ms(500), 0.55, STD); r.mouth_key(ms(800), 0.35, SOFT); r.mouth_key(ms(2300), 0.35, STD); r.mouth_key(ms(2650), 0.55, SOFT)
    bx, by = RX + 24, EY - 22
    for j, (dx, dy, rr, t0) in enumerate(((-16, 14, 2, 700), (-11, 9, 3, 850), (0, 0, 13, 1000))):
        g = r.group()
        if j < 2: ellipse(g, 0, 0, rr, rr, BUBBLE)
        else:
            path(g, [((-15, 4), (0, -6), (0, 6)), ((-6, 11), (-6, 0), (6, 0)), ((7, 11), (-6, 0), (6, 0)), ((16, 3), (0, 6), (0, -6)), ((9, -8), (6, 0), (-5, -3)),
                     ((0, -11), (5, 0), (-5, 0)), ((-9, -7), (4, -4), (-5, 1))], color=WHITE, stroke=BUBBLE, width=2.5, closed=True)
        g.transform.anchor_point.value = V(0, 0); g.transform.position.value = V(bx + dx, by + dy)
        sc = g.transform.scale; sc.add_keyframe(0, V(0, 0), HOLD); sc.add_keyframe(ms(t0), V(0, 0), DECEL); sc.add_keyframe(ms(t0 + 180), V(112, 112), SOFT); sc.add_keyframe(ms(t0 + 280), V(100, 100), HOLD)
        sc.add_keyframe(ms(2300 + j * 60), V(100, 100), ACCEL); sc.add_keyframe(ms(2500 + j * 60), V(0, 0), HOLD)
    return r


def sleeping():
    r = Rig()
    p = r.face_pos(); p.add_keyframe(0, V(0, 2), SOFT); p.add_keyframe(ms(1500), V(0, 0), SOFT); p.add_keyframe(ms(3000), V(0, 2), SOFT)  # slow deep breath
    # sleepy eyes = the dot clipped flat at the top (a bowl), as on the PIMS/Rumi Slack avatar. Hide the round dots, draw bowls.
    r.eye_key("both", 0, 0, 0); r.eye_key("both", ms(3000), 0, 0)
    k = 0.5523 * R
    for x in (LX, RX):
        bowl = r.face.shapes.insert(0, objects.Group()) or r.face.shapes[0]
        path(bowl, [((x - R, EY - 2), (0, 0), (0, 0)), ((x + R, EY - 2), (0, 0), (0, k)), ((x, EY + R), (k, 0), (-k, 0)), ((x - R, EY - 2), (0, k), (0, 0))], color=NAVY, closed=True)
    r.mouth_key(0, 0.45); r.mouth_key(ms(1500), 0.5, SOFT); r.mouth_key(ms(3000), 0.45, SOFT)
    for k, (sz, dx, t0) in enumerate(((5, 0, 200), (7, 9, 900), (10, 20, 1600))):  # zZZ rise 800ms, staggered
        g = r.group()
        path(g, [((0, -sz), (0, 0), (0, 0)), ((sz, -sz), (0, 0), (0, 0)), ((0, 0), (0, 0), (0, 0)), ((sz, 0), (0, 0), (0, 0))], stroke=NAVY, width=1.6 + k * 0.6)
        g.transform.anchor_point.value = V(sz / 2, -sz / 2); pos = g.transform.position; x = 100 + dx
        pos.add_keyframe(0, V(x, EY - 10), HOLD); pos.add_keyframe(ms(t0), V(x, EY - 10), DECEL); pos.add_keyframe(ms(t0 + 1100), V(x + 4, EY - 34), STD)
        fade(g, ms(t0), ms(t0 + 200), ms(t0 + 800), ms(t0 + 1100))
    return r


def laugh():
    r = Rig()
    # mouth: brand smile -> big open laugh (second curve below) bouncing 3x at 150ms, hold, close
    r.mouth_key(0, 1.0); r.mouth_key(ms(600), 1.0, ACCEL); r.mouth_key(ms(700), 0.9, SOFT); r.mouth_key(ms(850), 1.35, SOFT); r.mouth_key(ms(2200), 1.35, STD); r.mouth_key(ms(2600), 1.0, SOFT)
    r.eye_key("both", 0); r.eye_key("both", ms(700), ease=ACCEL); r.eye_key("both", ms(850), 22, 8, SOFT); r.eye_key("both", ms(2200), 22, 8, STD); r.eye_key("both", ms(2600), 20, 20, SOFT)
    g = r.group(behind=True); lower = path(g, [((LX + 6, EY + 10), (0, 0), (10, 30)), ((RX - 6, EY + 10), (-10, 30), (0, 0))], stroke=NAVY, width=SW)
    def low(d): b = objects.Bezier(); b.add_point(V(LX + 6, EY + 10), V(0, 0), V(10, d)); b.add_point(V(RX - 6, EY + 10), V(-10, d), V(0, 0)); return b
    lower.shape.add_keyframe(0, low(0), HOLD); lower.shape.add_keyframe(ms(700), low(0), DECEL); lower.shape.add_keyframe(ms(850), low(36), SOFT); lower.shape.add_keyframe(ms(2200), low(36), STD); lower.shape.add_keyframe(ms(2600), low(0), HOLD)
    go = g.transform.opacity; go.add_keyframe(0, 0, HOLD); go.add_keyframe(ms(720), 100, HOLD); go.add_keyframe(ms(2250), 100, ACCEL); go.add_keyframe(ms(2420), 0, HOLD)
    p = r.face_pos()  # ha-ha-ha: 3 bounces of 150ms starting when the mouth opens, then settle
    p.add_keyframe(0, V(0, 0), HOLD); p.add_keyframe(ms(850), V(0, 0), DECEL)
    for i in range(3):
        t = 850 + i * 300; p.add_keyframe(ms(t + 150), V(0, -4 + i), SOFT); p.add_keyframe(ms(t + 300), V(0, 0), SOFT)
    p.add_keyframe(ms(2000), V(0, 0), SOFT)
    return r


EMOTIONS = dict(happy=happy, tongue=tongue, santa=santa, wink=wink, sad=sad, angry=angry, chef=chef, tie=tie, crying=crying, thinking=thinking, sleeping=sleeping, laugh=laugh)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for n in (sys.argv[1:] or EMOTIONS):
        p = EMOTIONS[n]().save(OUT / f"rumi-{n}.json"); print("built", p.name, p.stat().st_size // 1024, "KB")
