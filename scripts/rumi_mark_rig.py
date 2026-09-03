"""Stateful Lottie rig for the World-of-Rumi logo mark (512 canvas, same geometry as logo_mark_pack.py).

Eyes and mouth are Parts: a group of variant shapes, one visible at a time. `part.set(state, t)` crossfades
(120 ms default) and, when leaving/entering the round dot, squashes the dot the way the reference
'listening' video does. Props are groups anchored at their pivot with motion recipes (pop, float, twinkle...).
Grammar: reaction = rest -> state -> rest inside a 3 s loop; status = state held, secondary motion loops.
"""
import math
from lottie import objects
from lottie.objects import easing
from lottie.nvector import NVector as V

FPS = 30
SIZE = 512
M, OX, OY = 330, (512 - 330) / 2, 190
R, EY, EXL, EXR, STROKE, BOTTOM = 0.095, 0.103, 0.10, 0.90, 0.023, 0.372
NAVY, BLUE, RED, CORAL, PINK, WHITE = "#0B2545", "#2F6BB3", "#7A1F1F", "#E8746A", "#F3A6B8", "#FFFFFF"


def col(h):
    h = h.lstrip("#"); return objects.Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def P(x, y): return V(OX + x * M, OY + y * M)
def U(v): return v * M                      # mark units -> px
RP, SW = U(R), U(STROKE)                    # dot radius px, stroke px
L, Rr = P(EXL, EY), P(EXR, EY)              # eye centres


def bez(x1, y1, x2, y2): return easing.Bezier(V(x1, y1), V(x2, y2))
STD, DECEL, ACCEL, SOFT, LIN, HOLD = bez(.4, 0, .2, 1), bez(0, 0, .2, 1), bez(.4, 0, 1, 1), bez(.45, 0, .55, 1), easing.Linear(), easing.Hold()
def ms(t): return round(t / 1000 * FPS)


# ---------- shape helpers ----------
def _sub(g):
    """Every shape gets its own subgroup: in Lottie a fill/stroke styles ALL shapes above it in the same group."""
    sg = objects.Group(); g.add_shape(sg); return sg


def path(g, pts, fill=None, stroke=None, width=SW, closed=False):
    g = _sub(g); p = g.add_shape(objects.Path()); b = objects.Bezier(); b.closed = closed
    for v, i, o in pts: b.add_point(V(*v), V(*i), V(*o))
    p.shape.value = b
    if fill: g.add_shape(objects.Fill(col(fill)))
    if stroke:
        st = g.add_shape(objects.Stroke(col(stroke), width)); st.line_cap = objects.LineCap.Round; st.line_join = objects.LineJoin.Round
    return p


def line(g, a, b, color=NAVY, width=SW): return path(g, [(a, (0, 0), (0, 0)), (b, (0, 0), (0, 0))], stroke=color, width=width)
def polyline(g, pts, color=NAVY, width=SW): return path(g, [(p, (0, 0), (0, 0)) for p in pts], stroke=color, width=width)


def ellipse(g, c, rx, ry=None, fill=NAVY, stroke=None, width=SW):
    g = _sub(g); e = g.add_shape(objects.Ellipse()); e.position.value = V(*c) if not isinstance(c, V) else c; e.size.value = V(2 * rx, 2 * (ry or rx))
    if fill: g.add_shape(objects.Fill(col(fill)))
    if stroke: g.add_shape(objects.Stroke(col(stroke), width))
    return e


def arc_pts(x0, y0, x1, y1, bulge):
    """Quadratic-ish arc from (x0,y0) to (x1,y1) bulging by `bulge` (px, +down) as one cubic (2 vertices)."""
    return [((x0, y0), (0, 0), ((x1 - x0) / 3, bulge * 1.33)), ((x1, y1), (-(x1 - x0) / 3, bulge * 1.33), (0, 0))]


def arc(g, x0, y0, x1, y1, bulge, color=NAVY, width=SW): return path(g, arc_pts(x0, y0, x1, y1, bulge), stroke=color, width=width)


def half_disc(g, c, r, fill=NAVY, top=False):
    """Filled half disc: bottom half (bowl) by default; top=True gives the dome."""
    k = 0.5523 * r; s = -1 if top else 1; cx, cy = c
    return path(g, [((cx - r, cy), (0, 0), (0, s * k)), ((cx, cy + s * r), (-k, 0), (k, 0)), ((cx + r, cy), (0, s * k), (0, 0))], fill=fill, closed=True)


def heart(g, c, r, fill=CORAL):
    cx, cy = c
    return path(g, [((cx, cy + r * 0.95), (r * 0.6, -r * 0.5), (-r * 0.6, -r * 0.5)), ((cx - r * 0.95, cy - r * 0.15), (0, r * 0.5), (0, -r * 0.7)),
                    ((cx - r * 0.45, cy - r * 0.85), (-r * 0.35, 0), (r * 0.35, 0)), ((cx, cy - r * 0.4), (-r * 0.15, -r * 0.25), (r * 0.15, -r * 0.25)),
                    ((cx + r * 0.45, cy - r * 0.85), (-r * 0.35, 0), (r * 0.35, 0)), ((cx + r * 0.95, cy - r * 0.15), (0, -r * 0.7), (0, r * 0.5))], fill=fill, closed=True)


def star(g, c, r, fill=NAVY, points=5, inner=0.45):
    g = _sub(g); s = g.add_shape(objects.Star()); s.position.value = V(*c); s.outer_radius.value = r; s.inner_radius.value = r * inner; s.points.value = points
    g.add_shape(objects.Fill(col(fill))); return s


def sparkle(g, c, r, fill=NAVY): return star(g, c, r, fill, 4, 0.25)


def drop(g, c, h, fill=BLUE):
    cx, cy = c
    return path(g, [((cx, cy - h), (0, 0), (h * 0.5, h * 0.55)), ((cx, cy + h * 0.5), (h * 0.55, -h * 0.1), (-h * 0.55, -h * 0.1)), ((cx, cy - h), (-h * 0.5, h * 0.55), (0, 0))], fill=fill, closed=True)


def rrect(g, c, w, h, r, fill=NAVY):
    g = _sub(g); rc = g.add_shape(objects.Rect()); rc.position.value = V(*c); rc.size.value = V(w, h); rc.rounded.value = r
    g.add_shape(objects.Fill(col(fill))); return rc


# ---------- animated helpers ----------
def fade(g, keys):
    """keys: list of (t_ms, opacity). Linear between, hold before first. One key -> static value."""
    o = g.transform.opacity
    if len(keys) == 1 and keys[0][0] == 0:
        o.value = keys[0][1]; return
    if keys[0][0] > 0: o.add_keyframe(0, keys[0][1], HOLD)
    for i, (t, v) in enumerate(keys): o.add_keyframe(ms(t), v, LIN)


def pop(g, t, dur=220, over=1.12, out_t=None, out_dur=180):
    """Scale 0 -> over -> 1 with anticipation-free pop; optional pop-out at out_t."""
    s = g.transform.scale
    s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(t), V(0, 0), DECEL)
    s.add_keyframe(ms(t + dur * 0.65), V(100 * over, 100 * over), SOFT); s.add_keyframe(ms(t + dur), V(100, 100), HOLD)
    if out_t:
        s.add_keyframe(ms(out_t), V(100, 100), ACCEL); s.add_keyframe(ms(out_t + out_dur), V(0, 0), HOLD)


def anchor(g, c): g.transform.anchor_point.value = V(*c); g.transform.position.value = V(*c)


def overshoot(prop, t0, a, b, dur=260, amount=0.08):
    prop.add_keyframe(t0, a, DECEL); prop.add_keyframe(t0 + ms(dur * .6), b + (b - a) * amount, SOFT)
    prop.add_keyframe(t0 + ms(dur * .8), b - (b - a) * amount * .5, SOFT); prop.add_keyframe(t0 + ms(dur), b, SOFT)


def wobble(prop, t0, t1, amp, period=300, base=0):
    n = int((t1 - t0) / period * 2)
    for i in range(n + 1): prop.add_keyframe(ms(t0 + i * period / 2), base + (amp if i % 2 else -amp) * (1 if i else 0), SOFT)
    prop.add_keyframe(ms(t1), base, SOFT)


def shake(prop, t0, t1, amp, step=50, base=V(0, 0), seed=3):
    import random; rnd = random.Random(seed)
    prop.add_keyframe(ms(t0), base, LIN); n = int((t1 - t0) / step)
    for i in range(1, n): a = amp * (1 - i / (n + 2)); prop.add_keyframe(ms(t0 + i * step), base + V(rnd.uniform(-a, a), rnd.uniform(-a * .5, a * .5)), LIN)
    prop.add_keyframe(ms(t1), base, SOFT)


# ---------- Part: one-of-N variants ----------
class Part:
    def __init__(self, layer, on_top=True):
        self.g = objects.Group()
        (layer.shapes.insert(0, self.g) if on_top else layer.add_shape(self.g))
        self.variants = {}; self.timeline = []   # (t_ms, state, dur)

    def variant(self, name):
        g = objects.Group(); self.g.add_shape(g); self.variants[name] = g; return g

    def set(self, state, t=0, dur=120):
        self.timeline.append((t, state, dur))

    def bake(self, end_ms):
        tl = sorted(self.timeline, key=lambda e: e[0])          # stable: baseline (t=-1) first, then in call order
        # collapse same-time entries: the LAST call at a given time wins (emotion overrides baseline)
        merged = []
        for t, st, dur in tl:
            if merged and merged[-1][0] == max(t, 0): merged[-1] = (max(t, 0), st, dur)
            else: merged.append((max(t, 0), st, dur))
        for name, g in self.variants.items():
            keys = [(0, 100 if merged[0][1] == name else 0)]; cur = merged[0][1]
            for t, st, dur in merged[1:]:
                was, cur = cur, st
                if (was == name) != (st == name):
                    keys.append((t, 100 if was == name else 0)); keys.append((t + dur, 100 if st == name else 0))
            fade(g, keys)


class Eye(Part):
    def __init__(self, layer, c, side):
        super().__init__(layer); self.c = c; self.side = side; cx, cy = c; r = RP
        self.dot = ellipse(self.variant("dot"), c, r)
        ellipse(self.variant("big"), c, r * 1.35); ellipse(self.variant("small"), c, r * .6)
        ellipse(self.variant("ring"), c, r - SW * .45, fill=None, stroke=NAVY, width=SW * .9)
        lid = self.variant("lid"); half_disc(lid, c, r); anchor(lid, c); self.lid = lid
        arc(self.variant("arch"), cx - U(.095), cy + U(.02), cx + U(.095), cy + U(.02), -U(.075), width=SW * 1.3)
        arc(self.variant("closed"), cx - U(.09), cy, cx + U(.09), cy, U(.05), width=SW * 1.3)
        x = self.variant("x"); rr = r * .9; line(x, (cx - rr, cy - rr), (cx + rr, cy + rr), width=SW * 1.3); line(x, (cx + rr, cy - rr), (cx - rr, cy + rr), width=SW * 1.3); anchor(x, c)
        h = self.variant("heart"); heart(h, c, r * 1.25); anchor(h, c); self.heart = h
        s = self.variant("star"); star(s, c, r * 1.4); anchor(s, c); self.star = s
        sp = self.variant("spiral"); pts = [(cx + r * (t / 4.2) * math.cos(t), cy + r * (t / 4.2) * math.sin(t)) for t in [i * .3 for i in range(32)]]
        polyline(sp, pts, width=SW * .9); anchor(sp, c); self.spiral = sp
        lk = self.variant("look"); ellipse(lk, c, r - SW * .45, fill=None, stroke=NAVY, width=SW * .9); self.pupil = ellipse(lk, (cx, cy + r * .45), r * .42)
        self.set("dot", -1)

    def blink(self, t, close=100, hold=50, open_=100):
        s = self.dot.size; d = 2 * RP
        s.add_keyframe(ms(t), V(d, d), ACCEL); s.add_keyframe(ms(t + close), V(d * 1.1, d * .12), HOLD)
        s.add_keyframe(ms(t + close + hold), V(d * 1.1, d * .12), DECEL); s.add_keyframe(ms(t + close + hold + open_), V(d, d), STD)

    def squash_out(self, t, dur=120):   # leaving the dot state: flatten while fading (reference look)
        s = self.dot.size; d = 2 * RP
        s.add_keyframe(ms(t), V(d, d), ACCEL); s.add_keyframe(ms(t + dur), V(d * 1.25, d * .35), HOLD)

    def squash_in(self, t, dur=140):
        s = self.dot.size; d = 2 * RP
        s.add_keyframe(ms(t), V(d * 1.25, d * .35), DECEL); s.add_keyframe(ms(t + dur * .7), V(d * 1.06, d * 1.06), SOFT); s.add_keyframe(ms(t + dur), V(d, d), HOLD)


class Mouth(Part):
    def __init__(self, layer):
        super().__init__(layer, on_top=False)
        cx = OX + .5 * M; y = OY + (EY + .22) * M
        self.link = path(self.variant("link"), self.link_pts(0), stroke=NAVY)            # the logo curve
        line(self.variant("flat"), (cx - U(.16), y), (cx + U(.16), y))
        arc(self.variant("small"), cx - U(.10), OY + (EY + .19) * M, cx + U(.10), OY + (EY + .19) * M, U(.06))
        arc(self.variant("frown"), cx - U(.20), OY + (EY + .19) * M, cx + U(.20), OY + (EY + .19) * M, -U(.075))
        arc(self.variant("smirk"), cx - U(.14), OY + (EY + .24) * M, cx + U(.16), OY + (EY + .17) * M, U(.06))
        ellipse(self.variant("o"), (cx, y), U(.045))
        od = self.variant("open"); half_disc(od, (cx, OY + (EY + .17) * M), U(.16)); anchor(od, (cx, OY + (EY + .17) * M)); self.open = od
        of = self.variant("openfrown"); half_disc(of, (cx, OY + (EY + .24) * M), U(.09), top=True); anchor(of, (cx, OY + (EY + .24) * M))
        zz = self.variant("zigzag"); hw, amp, n = U(.17), U(.03), 4
        polyline(zz, [(cx - hw + 2 * hw * i / (2 * n), y + (amp if i % 2 else -amp)) for i in range(2 * n + 1)]); anchor(zz, (cx, y)); self.zigzag = zz
        wv = self.variant("wavy"); self.wavy = path(wv, self.wavy_pts(0), stroke=NAVY)
        th = self.variant("teeth"); half_disc(th, (cx, OY + (EY + .17) * M), U(.16)); rrect(th, (cx, OY + (EY + .17) * M + U(.16) * .15), U(.16) * 1.9, U(.16) * .3, 0, WHITE)
        tg = self.variant("tongue"); half_disc(tg, (cx, OY + (EY + .17) * M), U(.13)); self.tongue = objects.Group(); tg.shapes.insert(0, self.tongue)
        rrect(self.tongue, (OX + .56 * M, OY + .27 * M + U(.05)), U(.08), U(.10), U(.04), CORAL); anchor(self.tongue, (OX + .56 * M, OY + .27 * M))
        dd = self.variant("dots"); self.dotgroups = []
        for i in (-1, 0, 1): g = objects.Group(); ellipse(g, (cx + i * RP * .55, y), SW * .6); anchor(g, (cx + i * RP * .55, y)); dd.add_shape(g); self.dotgroups.append(g)
        zp = self.variant("zip"); line(zp, (cx - U(.18), y), (cx + U(.18), y))
        self.zipteeth = []
        for i in range(-3, 4): g = objects.Group(); line(g, (cx + i * RP * .5, y - SW * .9), (cx + i * RP * .5, y + SW * .9), width=SW * .55); zp.add_shape(g); self.zipteeth.append(g)
        self.variant("none")
        self.set("link", -1)

    @staticmethod
    def link_pts(lift):
        x0, x1 = OX + .145 * M, OX + .855 * M; ay = OY + .195 * M; yb = OY + (BOTTOM - lift) * M
        return [((x0, ay), (0, 0), ((x1 - x0) / 3, (yb - ay) * 1.33)), ((x1, ay), (-(x1 - x0) / 3, (yb - ay) * 1.33), (0, 0))]

    def link_key(self, t, lift, ease=STD):
        b = objects.Bezier()
        for v, i, o in self.link_pts(lift): b.add_point(V(*v), V(*i), V(*o))
        self.link.shape.add_keyframe(ms(t), b, ease)

    @staticmethod
    def wavy_pts(phase):
        cx = OX + .5 * M; y = OY + (EY + .22) * M; pts = []
        for k in range(5):
            t = k / 4; x = cx - U(.16) + U(.32) * t; yy = y + U(.03) * math.sin(t * math.pi * 3 + phase)
            pts.append(((x, yy), (-U(.03), 0), (U(.03), 0)))
        return pts

    def wavy_key(self, t, phase, ease=SOFT):
        b = objects.Bezier()
        for v, i, o in self.wavy_pts(phase): b.add_point(V(*v), V(*i), V(*o))
        self.wavy.shape.add_keyframe(ms(t), b, ease)


class Face:
    def __init__(self, seconds=3.0):
        self.an = objects.Animation(round(seconds * FPS), FPS); self.an.width = self.an.height = SIZE
        self.end = round(seconds * 1000)
        self.layer = objects.ShapeLayer(); self.an.add_layer(self.layer); self.layer.out_point = self.an.out_point
        self.mouth = Mouth(self.layer); self.eyeL = Eye(self.layer, (L.x, L.y), "l"); self.eyeR = Eye(self.layer, (Rr.x, Rr.y), "r")
        self.props = []

    @property
    def pos(self): return self.layer.transform.position

    def breathe(self, amp=3, period=3000, phase=0):
        p = self.pos; base = V(0, 0)
        p.add_keyframe(0, base, SOFT); p.add_keyframe(ms(period / 2), base + V(0, -amp), SOFT); p.add_keyframe(ms(period), base, SOFT)

    def eyes(self, state, t=0, dur=120, which="lr"):
        for e in (self.eyeL, self.eyeR):
            if e.side in which:
                prev = e.timeline[-1][1] if e.timeline else None
                if prev == "dot" and state != "dot": e.squash_out(t, dur)
                if prev != "dot" and state == "dot": e.squash_in(t, dur)
                e.set(state, t, dur)

    def blink(self, t, which="lr"):
        for e in (self.eyeL, self.eyeR):
            if e.side in which: e.blink(t)

    def prop(self, on_top=True):
        g = objects.Group(); (self.layer.shapes.insert(0, g) if on_top else self.layer.add_shape(g)); self.props.append(g); return g

    def save(self, path):
        for part in (self.mouth, self.eyeL, self.eyeR): part.bake(self.end)
        from lottie.exporters.core import export_lottie
        with open(path, "w") as fh: export_lottie(self.an, fh)
        return path


def near_right(dx=1.6, dy=-1.6): return (Rr.x + dx * RP, Rr.y + dy * RP)
