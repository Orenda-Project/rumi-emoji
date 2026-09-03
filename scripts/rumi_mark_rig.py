"""Stateful, MORPHING Lottie rig for the World-of-Rumi logo mark (512 canvas, geometry = logo_mark_pack.py).

Eyes: one filled path with 12 vertices that morphs between states (dot, big, small, lid, arch, closed, heart, star, x,
blink). Ring / spiral / look are stroke-based and crossfade instead.
Mouth: one 9-vertex stroked path that morphs between link-curve, flat, small, frown, smirk, wavy, zigzag; filled mouths
(open, openfrown, o) are a 12-vertex closed path that opens from the flattened curve, like a real mouth.
Props are anchored groups with recipes (pop, fade, overshoot, wobble, shake, Trim draw-on).
"""
import math
from lottie import objects
from lottie.objects import easing
from lottie.nvector import NVector as V

FPS = 30
SIZE = 512
M, OX, OY = 330, (512 - 330) / 2, 190
R, EY, EXL, EXR, STROKE, BOTTOM = 0.095, 0.103, 0.10, 0.90, 0.023, 0.372
NAVY, BLUE, RED, CORAL, PINK, WHITE = "#001F3F", "#2F6BB3", "#7A1F1F", "#E8746A", "#F3A6B8", "#FFFFFF"
NE, NM = 12, 9      # vertex counts: eye (closed), mouth stroke (open)


def col(h):
    h = h.lstrip("#"); return objects.Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def P(x, y): return V(OX + x * M, OY + y * M)
def U(v): return v * M
RP, SW = U(R), U(STROKE)
L, Rr = P(EXL, EY), P(EXR, EY)


def bez(x1, y1, x2, y2): return easing.Bezier(V(x1, y1), V(x2, y2))
STD, DECEL, ACCEL, SOFT, LIN, HOLD = bez(.4, 0, .2, 1), bez(0, 0, .2, 1), bez(.4, 0, 1, 1), bez(.45, 0, .55, 1), easing.Linear(), easing.Hold()
def ms(t): return round(t / 1000 * FPS)


# ---------- geometry as (v, i, o) tuples, relative tangents ----------
def to_bezier(pts, closed):
    b = objects.Bezier(); b.closed = closed
    for v, i, o in pts: b.add_point(V(*v), V(*i), V(*o))
    return b


def _split(p0, c1, c2, p1, t=0.5):
    """de Casteljau split of one cubic (absolute control points) -> two cubics."""
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a = lerp(p0, c1); b = lerp(c1, c2); c = lerp(c2, p1); d = lerp(a, b); e = lerp(b, c); m = lerp(d, e)
    return (p0, a, d, m), (m, e, c, p1)


def normalize(pts, n, closed):
    """Resample a (v,i,o) path to exactly n vertices by splitting its longest segments (exact, curvature-preserving)."""
    segs = []   # absolute cubics
    cnt = len(pts) if closed else len(pts) - 1
    for k in range(cnt):
        v0, _, o0 = pts[k]; v1, i1, _ = pts[(k + 1) % len(pts)]
        segs.append((v0, (v0[0] + o0[0], v0[1] + o0[1]), (v1[0] + i1[0], v1[1] + i1[1]), v1))
    need = n - len(pts)
    while need > 0:
        # split the longest segment (chord length) -> keeps distribution even
        k = max(range(len(segs)), key=lambda j: math.dist(segs[j][0], segs[j][3]))
        a, b = _split(*segs[k]); segs[k:k + 1] = [a, b]; need -= 1
    assert need == 0, f"path has more than {n} vertices"
    out = []
    for k, (p0, c1, c2, p1) in enumerate(segs):
        prev = segs[k - 1] if (closed or k > 0) else None
        i = (prev[2][0] - p0[0], prev[2][1] - p0[1]) if prev else (0, 0)
        out.append((p0, i, (c1[0] - p0[0], c1[1] - p0[1])))
    if not closed:
        p0, c1, c2, p1 = segs[-1]; out.append((p1, (c2[0] - p1[0], c2[1] - p1[1]), (0, 0)))
    return out


def rotate_start(pts):
    """Start closed paths at the left-most vertex so morph correspondences line up."""
    k = min(range(len(pts)), key=lambda j: (pts[j][0][0], pts[j][0][1])); return pts[k:] + pts[:k]


def circle_pts(c, rx, ry=None, n=NE):
    ry = rx if ry is None else ry; cx, cy = c; k = 4 / 3 * math.tan(math.pi / (2 * n))
    out = []
    for j in range(n):
        a = math.pi + 2 * math.pi * j / n          # start at the left, go via the bottom (y down)
        ca, sa = math.cos(a), math.sin(a)
        out.append(((cx + rx * ca, cy + ry * sa), (rx * k * sa, -ry * k * ca), (-rx * k * sa, ry * k * ca)))
    return out


def arc_abs(x0, y0, x1, y1, bulge, n=8):
    """Sampled quadratic-ish arc as a polyline with smooth tangents, n vertices."""
    pts = []
    for j in range(n):
        t = j / (n - 1); x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t + bulge * 4 * t * (1 - t)
        dx = (x1 - x0) / (n - 1) / 3; dy = ((y1 - y0) + bulge * 4 * (1 - 2 * t)) / (n - 1) / 3
        pts.append(((x, y), (-dx, -dy), (dx, dy)))
    pts[0] = (pts[0][0], (0, 0), pts[0][2]); pts[-1] = (pts[-1][0], pts[-1][1], (0, 0)); return pts


def band_pts(x0, y0, x1, y1, bulge, w):
    """Closed thick 'stroke' band around an arc (outer edge L->R, inner edge R->L)."""
    top = arc_abs(x0, y0 - w / 2, x1, y1 - w / 2, bulge, 6); bot = arc_abs(x1, y1 + w / 2, x0, y0 + w / 2, bulge, 6)
    return [(v, (0, 0), (0, 0)) for v, _, _ in top] + [(v, (0, 0), (0, 0)) for v, _, _ in bot]


def half_disc_pts(c, r, top=False):
    cx, cy = c; s = -1 if top else 1; k = 0.5523 * r
    pts = [((cx - r, cy), (0, 0), (0, s * k)), ((cx, cy + s * r), (-k, 0), (k, 0)), ((cx + r, cy), (0, s * k), (0, 0))]
    return pts


def heart_pts(c, r):
    cx, cy = c
    return [((cx, cy + r * .95), (r * .6, -r * .5), (-r * .6, -r * .5)), ((cx - r * .95, cy - r * .15), (0, r * .5), (0, -r * .7)),
            ((cx - r * .45, cy - r * .85), (-r * .35, 0), (r * .35, 0)), ((cx, cy - r * .4), (-r * .15, -r * .25), (r * .15, -r * .25)),
            ((cx + r * .45, cy - r * .85), (-r * .35, 0), (r * .35, 0)), ((cx + r * .95, cy - r * .15), (0, -r * .7), (0, r * .5))]


def star_pts(c, r, inner=.45):
    cx, cy = c
    return [((cx + (r if j % 2 == 0 else r * inner) * math.cos(math.radians(-90 + 36 * j)), cy + (r if j % 2 == 0 else r * inner) * math.sin(math.radians(-90 + 36 * j))), (0, 0), (0, 0)) for j in range(10)]


def x_pts(c, r, w):
    """12-vertex X polygon (two crossed bars of width w)."""
    cx, cy = c; a = r * .9; h = w / 2 * math.sqrt(2)
    raw = [(-a, -a + h), (-a + h, -a), (0, -h), (a - h, -a), (a, -a + h), (h, 0), (a, a - h), (a - h, a), (0, h), (-a + h, a), (-a, a - h), (-h, 0)]
    return [((cx + x, cy + y), (0, 0), (0, 0)) for x, y in raw]


def polyline_pts(pts): return [(p, (0, 0), (0, 0)) for p in pts]


# ---------- shape helpers (each in its own subgroup: a style applies to every shape above it in a group) ----------
def _sub(g): sg = objects.Group(); g.add_shape(sg); return sg


def path(g, pts, fill=None, stroke=None, width=SW, closed=False):
    g = _sub(g); p = g.add_shape(objects.Path()); p.shape.value = to_bezier(pts, closed)
    if fill: g.add_shape(objects.Fill(col(fill)))
    if stroke:
        st = g.add_shape(objects.Stroke(col(stroke), width)); st.line_cap = objects.LineCap.Round; st.line_join = objects.LineJoin.Round
    return p


def line(g, a, b, color=NAVY, width=SW): return path(g, polyline_pts([a, b]), stroke=color, width=width)
def polyline(g, pts, color=NAVY, width=SW): return path(g, polyline_pts(pts), stroke=color, width=width)


def ellipse(g, c, rx, ry=None, fill=NAVY, stroke=None, width=SW):
    g = _sub(g); e = g.add_shape(objects.Ellipse()); e.position.value = V(*c) if not isinstance(c, V) else c; e.size.value = V(2 * rx, 2 * (ry or rx))
    if fill: g.add_shape(objects.Fill(col(fill)))
    if stroke: g.add_shape(objects.Stroke(col(stroke), width))
    return e


def arc(g, x0, y0, x1, y1, bulge, color=NAVY, width=SW): return path(g, arc_abs(x0, y0, x1, y1, bulge, 2) if False else arc_abs(x0, y0, x1, y1, bulge, 5), stroke=color, width=width)
def half_disc(g, c, r, fill=NAVY, top=False): return path(g, half_disc_pts(c, r, top), fill=fill, closed=True)
def heart(g, c, r, fill=CORAL): return path(g, heart_pts(c, r), fill=fill, closed=True)


def star(g, c, r, fill=NAVY, points=5, inner=0.45):
    g = _sub(g); s = g.add_shape(objects.Star()); s.position.value = V(*c); s.outer_radius.value = r; s.inner_radius.value = r * inner; s.points.value = points
    g.add_shape(objects.Fill(col(fill))); return s


def sparkle(g, c, r, fill=NAVY): return star(g, c, r, fill, 4, 0.25)


def drop(g, c, h, fill=BLUE):
    cx, cy = c
    return path(g, [((cx, cy - h), (0, 0), (h * .5, h * .55)), ((cx, cy + h * .5), (h * .55, -h * .1), (-h * .55, -h * .1)), ((cx, cy - h), (-h * .5, h * .55), (0, 0))], fill=fill, closed=True)


def rrect(g, c, w, h, r, fill=NAVY):
    g = _sub(g); rc = g.add_shape(objects.Rect()); rc.position.value = V(*c); rc.size.value = V(w, h); rc.rounded.value = r
    g.add_shape(objects.Fill(col(fill))); return rc


# ---------- animated helpers ----------
def fade(g, keys):
    o = g.transform.opacity
    if len(keys) == 1 and keys[0][0] == 0: o.value = keys[0][1]; return
    if keys[0][0] > 0: o.add_keyframe(0, keys[0][1], HOLD)
    for t, v in keys: o.add_keyframe(ms(t), v, LIN)


def pop(g, t, dur=220, over=1.12, out_t=None, out_dur=180):
    s = g.transform.scale
    s.add_keyframe(0, V(0, 0), HOLD); s.add_keyframe(ms(t), V(0, 0), DECEL)
    s.add_keyframe(ms(t + dur * .65), V(100 * over, 100 * over), SOFT); s.add_keyframe(ms(t + dur), V(100, 100), HOLD)
    if out_t: s.add_keyframe(ms(out_t), V(100, 100), ACCEL); s.add_keyframe(ms(out_t + out_dur), V(0, 0), HOLD)


def anchor(g, c): g.transform.anchor_point.value = V(*c); g.transform.position.value = V(*c)


def overshoot(prop, t0, a, b, dur=260, amount=.08):
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


# ---------- Morphing parts ----------
class MorphPath:
    """One Path whose shape morphs between named states (all normalised to n vertices)."""
    def __init__(self, g, shapes, initial, n, closed, fill=None, stroke=None, width=SW):
        self.shapes = {k: (rotate_start(normalize(v, n, closed)) if closed else normalize(v, n, closed)) for k, v in shapes.items()}
        self.path = path(g, self.shapes[initial], fill=fill, stroke=stroke, width=width, closed=closed)
        self.group = g.shapes[-2]     # the subgroup path() just created (before the trailing TransformShape)
        self.closed = closed; self.cur = initial; self.keys = []   # (t_ms, state or pts, ease)

    def key(self, t, state, ease=STD):
        self.keys.append((t, state, ease))

    def bake(self):
        if not self.keys: return
        prop = self.path.shape
        for t, st, ease in sorted(self.keys, key=lambda k: k[0]):
            pts = self.shapes[st] if isinstance(st, str) else st
            prop.add_keyframe(ms(max(t, 0)), to_bezier(pts, self.closed), ease)


class Eye:
    MORPH = ("dot", "big", "small", "lid", "arch", "closed", "heart", "star", "x", "blink", "squash")
    def __init__(self, layer, c, side):
        self.c = c; self.side = side; cx, cy = c; r = RP
        self.g = objects.Group(); layer.shapes.insert(0, self.g)   # origin stays (0,0): emotions nudge e.g.transform.position relatively
        shapes = {
            "dot": circle_pts(c, r), "big": circle_pts(c, r * 1.35), "small": circle_pts(c, r * .6),
            "blink": circle_pts(c, r * 1.1, r * .06), "squash": circle_pts(c, r * 1.25, r * .35),
            "lid": half_disc_pts(c, r), "heart": heart_pts(c, r * 1.25), "star": star_pts(c, r * 1.4), "x": x_pts(c, r, SW * 1.3),
            "arch": band_pts(cx - U(.095), cy + U(.02), cx + U(.095), cy + U(.02), -U(.075), SW * 1.3),
            "closed": band_pts(cx - U(.09), cy, cx + U(.09), cy, U(.05), SW * 1.3),
        }
        self.m = MorphPath(self.g, shapes, "dot", NE, True, fill=NAVY)
        self.morph_group = self.m.group; anchor(self.morph_group, c)
        # stroke-based states crossfade
        self.variants = {}
        rg = self._variant("ring"); ellipse(rg, c, r - SW * .45, fill=None, stroke=NAVY, width=SW * .9)
        sp = self._variant("spiral"); pts = [(cx + r * (t / 4.2) * math.cos(t), cy + r * (t / 4.2) * math.sin(t)) for t in [i * .3 for i in range(32)]]
        polyline(sp, pts, width=SW * .9); anchor(sp, c); self.spiral = sp
        lk = self._variant("look"); ellipse(lk, c, r - SW * .45, fill=None, stroke=NAVY, width=SW * .9); self.pupil = ellipse(lk, (cx, cy + r * .45), r * .42)
        self.timeline = [(-1, "dot", 0)]
        # aliases used by make_lottie_mark.py transform animations (they act on the whole morph path)
        self.lid = self.heart = self.star = self.morph_group
        self.variants["x"] = self.variants["big"] = self.morph_group

    def _variant(self, name):
        g = objects.Group(); self.g.add_shape(g); self.variants[name] = g; anchor(g, self.c); return g

    def set(self, state, t=0, dur=120): self.timeline.append((t, state, dur))

    def blink(self, t, close=100, hold=50, open_=100):
        self.m.key(t, "dot", ACCEL); self.m.key(t + close, "blink", HOLD); self.m.key(t + close + hold, "blink", DECEL); self.m.key(t + close + hold + open_, "dot", STD)

    def bake(self):
        tl = sorted(self.timeline, key=lambda e: e[0]); merged = []
        for t, st, dur in tl:
            if merged and merged[-1][0] == max(t, 0): merged[-1] = (max(t, 0), st, dur)
            else: merged.append((max(t, 0), st, dur))
        # morph keys + crossfade keys for stroke variants
        vis = {n: [(0, 100 if merged[0][1] == n else 0)] for n in ("ring", "spiral", "look")}
        mvis = [(0, 100 if merged[0][1] in self.MORPH else 0)]
        cur = merged[0][1]
        if cur in self.MORPH: self.m.key(0, cur, STD)
        for t, st, dur in merged[1:]:
            was, cur = cur, st
            a, b = was in self.MORPH, st in self.MORPH
            if a and b:
                self.m.key(t, was, ACCEL if st in ("arch", "closed", "lid") else STD)
                if was == "dot" and st in ("arch", "closed", "lid"):      # the reference look: flatten, then bend
                    self.m.key(t + dur * .5, "squash", DECEL); self.m.key(t + dur * 1.2, st, SOFT)
                elif st == "dot" and was in ("arch", "closed", "lid"):
                    self.m.key(t + dur * .6, "squash", DECEL); self.m.key(t + dur * 1.3, "dot", SOFT)
                else: self.m.key(t + dur, st, STD)
            else:
                if a: self.m.key(t, was, STD)
                if b: self.m.key(t, st, STD)
                mvis.append((t, 100 if a else 0)); mvis.append((t + dur, 100 if b else 0))
                for n in vis: 
                    if (was == n) != (st == n): vis[n].append((t, 100 if was == n else 0)); vis[n].append((t + dur, 100 if st == n else 0))
        fade(self.morph_group, mvis)
        for n, g in self.variants.items():
            if n in vis: fade(g, vis[n])
        self.m.bake()


class Mouth:
    STROKE = ("link", "flat", "small", "frown", "smirk", "wavy", "zigzag", "none", "tiny")
    FILL = ("open", "openfrown", "o", "teeth", "tongue")
    def __init__(self, layer):
        self.g = objects.Group(); layer.add_shape(self.g)
        cx = OX + .5 * M; y = OY + (EY + .22) * M; self.cx, self.y = cx, y
        s = {
            "link": self.link_pts(0), "flat": polyline_pts([(cx - U(.16), y), (cx + U(.16), y)]),
            "tiny": polyline_pts([(cx - 2, y), (cx + 2, y)]), "none": polyline_pts([(cx - 2, y), (cx + 2, y)]),
            "small": arc_abs(cx - U(.10), OY + (EY + .19) * M, cx + U(.10), OY + (EY + .19) * M, U(.06), 5),
            "frown": arc_abs(cx - U(.20), OY + (EY + .19) * M, cx + U(.20), OY + (EY + .19) * M, -U(.075), 5),
            "smirk": arc_abs(cx - U(.14), OY + (EY + .24) * M, cx + U(.16), OY + (EY + .17) * M, U(.06), 5),
            "wavy": self.wavy_pts(0), "zigzag": polyline_pts([(cx - U(.17) + 2 * U(.17) * i / 8, y + (U(.03) if i % 2 else -U(.03))) for i in range(9)]),
        }
        self.sm = MorphPath(self.g, s, "link", NM, False, stroke=NAVY)
        self.stroke_group = self.sm.group
        # filled mouth: opens downward from the flat line (anchor at the top edge)
        top = OY + (EY + .17) * M
        fs = {"open": half_disc_pts((cx, top), U(.16)), "teeth": half_disc_pts((cx, top), U(.16)), "tongue": half_disc_pts((cx, top), U(.13)),
              "openfrown": half_disc_pts((cx, OY + (EY + .24) * M + U(.09)), U(.09), top=True), "o": circle_pts((cx, y), U(.045))}
        self.fg = objects.Group(); self.g.shapes.insert(0, self.fg)
        self.fm = MorphPath(self.fg, fs, "open", NE, True, fill=NAVY); anchor(self.fm.group, (cx, top))
        self.open = self.fm.group
        # composites that ride on the filled mouth
        self.teethbar = objects.Group(); self.fg.shapes.insert(0, self.teethbar); rrect(self.teethbar, (cx, top + U(.16) * .15), U(.16) * 1.9, U(.16) * .3, 0, WHITE)
        self.tongue = objects.Group(); self.fg.shapes.insert(0, self.tongue); rrect(self.tongue, (OX + .56 * M, OY + .27 * M + U(.05)), U(.08), U(.10), U(.04), CORAL); anchor(self.tongue, (OX + .56 * M, OY + .27 * M))
        self.dg = objects.Group(); self.g.shapes.insert(0, self.dg); self.dotgroups = []
        for i in (-1, 0, 1): g = objects.Group(); ellipse(g, (cx + i * RP * .55, y), SW * .6); anchor(g, (cx + i * RP * .55, y)); self.dg.add_shape(g); self.dotgroups.append(g)
        self.zg = objects.Group(); self.g.shapes.insert(0, self.zg); self.zipteeth = []; line(self.zg, (cx - U(.18), y), (cx + U(.18), y))
        for i in range(-3, 4): g = objects.Group(); line(g, (cx + i * RP * .5, y - SW * .9), (cx + i * RP * .5, y + SW * .9), width=SW * .55); self.zg.add_shape(g); self.zipteeth.append(g)
        self.zigzag = self.stroke_group
        self.timeline = [(-1, "link", 0)]; self.extra = []   # extra stroke keys (link lift, wavy phase)

    @staticmethod
    def link_pts(lift):
        x0, x1 = OX + .145 * M, OX + .855 * M; ay = OY + .195 * M; yb = OY + (BOTTOM - lift) * M
        return [((x0, ay), (0, 0), ((x1 - x0) / 3, (yb - ay) * 1.33)), ((x1, ay), (-(x1 - x0) / 3, (yb - ay) * 1.33), (0, 0))]

    def wavy_pts(self, phase):
        cx, y = OX + .5 * M, OY + (EY + .22) * M; pts = []
        for k in range(9):
            t = k / 8; x = cx - U(.16) + U(.32) * t; yy = y + U(.03) * math.sin(t * math.pi * 3 + phase)
            pts.append(((x, yy), (-U(.013), 0), (U(.013), 0)))
        return pts

    def link_key(self, t, lift, ease=STD): self.sm.key(t, normalize(self.link_pts(lift), NM, False), ease)
    def wavy_key(self, t, phase, ease=SOFT): self.sm.key(t, normalize(self.wavy_pts(phase), NM, False), ease)
    def set(self, state, t=0, dur=140): self.timeline.append((t, state, dur))

    def bake(self):
        tl = sorted(self.timeline, key=lambda e: e[0]); merged = []
        for t, st, dur in tl:
            if merged and merged[-1][0] == max(t, 0): merged[-1] = (max(t, 0), st, dur)
            else: merged.append((max(t, 0), st, dur))
        cur = merged[0][1]
        svis = [(0, 100 if cur in self.STROKE and cur != "none" else 0)]
        fvis = [(0, 100 if cur in self.FILL else 0)]; tvis = [(0, 100 if cur == "teeth" else 0)]; gvis = [(0, 100 if cur == "tongue" else 0)]
        dvis = [(0, 100 if cur == "dots" else 0)]; zvis = [(0, 100 if cur == "zip" else 0)]
        fsc = self.fm.group.transform.scale; fsc.add_keyframe(0, V(100, 100 if cur in self.FILL else 0), HOLD)
        if cur in self.STROKE: self.sm.key(0, "flat" if cur == "none" else cur, STD)
        if cur in self.FILL: self.fm.key(0, "open" if cur in ("teeth", "tongue") else cur, STD)
        for t, st, dur in merged[1:]:
            was, cur = cur, st
            ws, ss = was in self.STROKE, st in self.STROKE; wf, sf = was in self.FILL, st in self.FILL
            if ws and ss:      # pure stroke morph
                self.sm.key(t, "flat" if was == "none" else was, STD); self.sm.key(t + dur, "flat" if st == "none" else st, STD)
                if was == "none" or st == "none": svis.append((t, 100 if was != "none" else 0)); svis.append((t + dur, 100 if st != "none" else 0))
            if ws and sf:      # stroke -> filled: curve flattens to the D's top edge while the D opens downward
                self.sm.key(t, "flat" if was == "none" else was, STD); self.sm.key(t + dur * .7, "tiny" if st == "o" else "flat", ACCEL)
                svis.append((t + dur * .5, 100 if was != "none" else 0)); svis.append((t + dur * .8, 0))
                fk = "open" if st in ("teeth", "tongue") else st
                self.fm.key(0, fk, HOLD) if not self.fm.keys else None; self.fm.key(t, fk, HOLD)
                fvis.append((t + dur * .4, 0)); fvis.append((t + dur * .5, 100))
                fsc.add_keyframe(ms(t + dur * .4), V(100, 0), DECEL); fsc.add_keyframe(ms(t + dur * 1.1), V(100, 112), SOFT); fsc.add_keyframe(ms(t + dur * 1.4), V(100, 100), HOLD)
            if wf and ss:      # filled -> stroke: D closes up into the line, line bends into the target
                fsc.add_keyframe(ms(t), V(100, 100), ACCEL); fsc.add_keyframe(ms(t + dur * .6), V(100, 0), HOLD)
                fvis.append((t + dur * .5, 100)); fvis.append((t + dur * .6, 0))
                self.sm.key(t + dur * .4, "tiny" if was == "o" else "flat", HOLD); self.sm.key(t + dur * .5, "tiny" if was == "o" else "flat", DECEL); self.sm.key(t + dur * 1.2, "flat" if st == "none" else st, SOFT)
                svis.append((t + dur * .4, 0)); svis.append((t + dur * .6, 100 if st != "none" else 0))
            if wf and sf:
                self.fm.key(t, "open" if was in ("teeth", "tongue") else was, STD); self.fm.key(t + dur, "open" if st in ("teeth", "tongue") else st, STD)
            for name, vis in (("teeth", tvis), ("tongue", gvis), ("dots", dvis), ("zip", zvis)):
                if (was == name) != (st == name): vis.append((t, 100 if was == name else 0)); vis.append((t + dur, 100 if st == name else 0))
            if st in ("dots", "zip") and ws: svis.append((t, 100)); svis.append((t + dur, 0))
            if was in ("dots", "zip") and ss: svis.append((t, 0)); svis.append((t + dur, 100))
        fade(self.stroke_group, svis); fade(self.fm.group, fvis); fade(self.teethbar, tvis); fade(self.tongue, gvis); fade(self.dg, dvis); fade(self.zg, zvis)
        self.sm.bake(); self.fm.bake()


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
        p = self.pos; p.add_keyframe(0, V(0, 0), SOFT); p.add_keyframe(ms(period / 2), V(0, -amp), SOFT); p.add_keyframe(ms(period), V(0, 0), SOFT)

    def eyes(self, state, t=0, dur=120, which="lr"):
        for e in (self.eyeL, self.eyeR):
            if e.side in which: e.set(state, t, dur)

    def blink(self, t, which="lr"):
        for e in (self.eyeL, self.eyeR):
            if e.side in which: e.blink(t)

    def prop(self, on_top=True):
        g = objects.Group(); (self.layer.shapes.insert(0, g) if on_top else self.layer.add_shape(g)); self.props.append(g); return g

    def save(self, path):
        for part in (self.mouth, self.eyeL, self.eyeR): part.bake()
        sort_keyframes(self.an)
        from lottie.exporters.core import export_lottie
        with open(path, "w") as fh: export_lottie(self.an, fh)
        return path


def sort_keyframes(obj, _seen=None):
    """Lottie requires keyframes in time order; recipes that add a pulse after an exit key would otherwise break players."""
    _seen = _seen if _seen is not None else set()
    if id(obj) in _seen: return
    _seen.add(id(obj))
    kfs = getattr(obj, "keyframes", None)
    if isinstance(kfs, list) and kfs and hasattr(kfs[0], "time"):
        kfs.sort(key=lambda k: k.time)
        # drop exact-duplicate times (keep the last one written)
        dedup = {}
        for k in kfs: dedup[k.time] = k
        kfs[:] = [dedup[t] for t in sorted(dedup)]
    for name in dir(obj):
        if name.startswith("_"): continue
        try: v = getattr(obj, name)
        except Exception: continue
        if callable(v): continue
        if isinstance(v, list):
            for it in v:
                if hasattr(it, "__dict__"): sort_keyframes(it, _seen)
        elif hasattr(v, "__dict__") and not isinstance(v, type): sort_keyframes(v, _seen)


def near_right(dx=1.6, dy=-1.6): return (Rr.x + dx * RP, Rr.y + dy * RP)
