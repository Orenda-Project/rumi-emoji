"""Rumi logo-mark rig for python-lottie: two dots + one curve, real keyframes, real easing.

Timing vocabulary (research-backed, see lottie/README.md): loops 2-3s, rest >= 40%,
blink 100-150ms, mouth morph 200-300ms, secondary action lags primary by 50-100ms,
overshoot 5-10% then 1-2 settle bounces at ~65% of the previous.
"""
import math, random
from lottie import objects
from lottie.objects import easing
from lottie.nvector import NVector as V

FPS = 30
W, H = 160, 100
LX, RX, EY = 44, 116, 36
R = 10
SW = 6
NAVY = objects.Color(0, 18 / 255, 64 / 255)
RED = objects.Color(0x8A / 255, 0x1C / 255, 0x1C / 255)


def col(hexs):
    h = hexs.lstrip("#"); return objects.Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


# --- easing (Material + spring) --------------------------------------------------
def bez(x1, y1, x2, y2):  # css cubic-bezier -> lottie keyframe easing
    return easing.Bezier(V(x1, y1), V(x2, y2))

STD = bez(0.4, 0.0, 0.2, 1.0)      # material standard
DECEL = bez(0.0, 0.0, 0.2, 1.0)    # entering
ACCEL = bez(0.4, 0.0, 1.0, 1.0)    # exiting
SOFT = bez(0.45, 0.0, 0.55, 1.0)   # gentle in-out
HOLD = easing.Hold()


def ms(t):  # milliseconds -> frame
    return round(t / 1000 * FPS)


def overshoot(prop, t0, a, b, dur_ms=260, amount=0.08, bounces=2):
    """Move prop from a to b with a spring: overshoot by `amount`, settle in `bounces`."""
    prop.add_keyframe(t0, a, DECEL)
    t = t0 + ms(dur_ms * 0.6)
    d = b - a
    prop.add_keyframe(t, b + d * amount, SOFT)
    amt = -amount * 0.65
    for _ in range(bounces - 1):
        t += ms(dur_ms * 0.2); prop.add_keyframe(t, b + d * amt, SOFT); amt *= -0.65
    t += ms(dur_ms * 0.2); prop.add_keyframe(t, b, SOFT)
    return t


# --- rig ------------------------------------------------------------------------
class Rig:
    def __init__(self, seconds=3.0, color=NAVY):
        self.an = objects.Animation(round(seconds * FPS), FPS)
        self.an.width, self.an.height = W, H
        self.end = self.an.out_point
        self.color = color
        self.layer = objects.ShapeLayer(); self.an.add_layer(self.layer)
        self.layer.out_point = self.end
        self.face = self.layer.add_shape(objects.Group())   # everything that moves with the face
        self.props_behind = []
        self.eyes = {}
        for name, x in (("l", LX), ("r", RX)):
            g = self.face.add_shape(objects.Group()); e = g.add_shape(objects.Ellipse())
            e.position.value = V(x, EY); e.size.value = V(2 * R, 2 * R); g.add_shape(objects.Fill(color))
            self.eyes[name] = e
        g = self.face.add_shape(objects.Group()); self.mouth = g.add_shape(objects.Path())
        self.mouth.shape.value = self.smile(1.0)
        st = g.add_shape(objects.Stroke(color, SW)); st.line_cap = objects.LineCap.Round; st.line_join = objects.LineJoin.Round
        self.mouth_stroke = st

    # mouth geometry: one cubic, 2 vertices, always same vertex count so it morphs
    @staticmethod
    def smile(amount=1.0, y=EY, lift=0.0):
        """amount 1 = brand smile, 0 = flat, -1 = frown. lift moves the whole curve up/down."""
        depth = 34 * amount
        b = objects.Bezier()
        if amount >= 0:
            b.add_point(V(LX, y + lift), V(0, 0), V(10, depth))
            b.add_point(V(RX, y + lift), V(-10, depth), V(0, 0))
        else:  # frown sits lower and bulges up between the dots
            y0 = y + 22 + lift
            b.add_point(V(LX, y0), V(0, 0), V(18, depth * 0.8))
            b.add_point(V(RX, y0), V(-18, depth * 0.8), V(0, 0))
        return b

    def mouth_key(self, t, amount=1.0, ease=STD, lift=0.0):
        self.mouth.shape.add_keyframe(t, self.smile(amount, lift=lift), ease)

    def eye_key(self, which, t, w=2 * R, h=2 * R, ease=STD):
        for k in (which if which != "both" else "lr"):
            self.eyes[k].size.add_keyframe(t, V(w, h), ease)

    def blink(self, t, which="both", close_ms=100, hold_ms=50, open_ms=100, dash=False):
        """Natural blink: 100ms close, 50 hold, 100 open. dash=True closes to a wide dash (wink look)."""
        closed = (V(2 * R + 8, 2.6) if dash else V(2 * R, 2.4))
        for k in (which if which != "both" else "lr"):
            e = self.eyes[k].size
            e.add_keyframe(t, V(2 * R, 2 * R), ACCEL)
            e.add_keyframe(t + ms(close_ms), closed, HOLD)
            e.add_keyframe(t + ms(close_ms + hold_ms), closed, DECEL)
            e.add_keyframe(t + ms(close_ms + hold_ms + open_ms), V(2 * R, 2 * R), STD)
        return t + ms(close_ms + hold_ms + open_ms)

    def hold_eyes(self, t):  # pin current open state so later keyframes don't drift
        for e in self.eyes.values(): e.size.add_keyframe(t, V(2 * R, 2 * R), STD)

    def face_pos(self):  # face group transform (for nods, shakes, bounces)
        return self.face.transform.position

    def group(self, behind=False):
        """A new group for a prop. behind=True draws it under the face."""
        g = objects.Group()
        # Lottie z-order: the FIRST shape in a list renders on TOP. So "on top" = insert(0), "behind" = append.
        if behind: self.layer.add_shape(g)
        else: self.layer.shapes.insert(0, g)
        return g

    def save(self, path):
        from lottie.exporters.core import export_lottie
        with open(path, "w") as fh: export_lottie(self.an, fh)
        return path


# --- prop helpers ----------------------------------------------------------------
def ellipse(g, cx, cy, rx, ry, color):
    e = g.add_shape(objects.Ellipse()); e.position.value = V(cx, cy); e.size.value = V(2 * rx, 2 * ry)
    g.add_shape(objects.Fill(color)); return e


def path(g, pts, color=None, stroke=None, width=3, closed=False):
    """pts: list of (vertex, in_tangent, out_tangent) tuples (tangents relative)."""
    p = g.add_shape(objects.Path()); b = objects.Bezier(); b.closed = closed
    for v, i, o in pts: b.add_point(V(*v), V(*i), V(*o))
    p.shape.value = b
    if color is not None: g.add_shape(objects.Fill(color))
    if stroke is not None:
        st = g.add_shape(objects.Stroke(stroke, width)); st.line_cap = objects.LineCap.Round; st.line_join = objects.LineJoin.Round
    return p


def line(g, a, b, color, width=3):
    return path(g, [(a, (0, 0), (0, 0)), (b, (0, 0), (0, 0))], stroke=color, width=width)


def teardrop(g, cx, cy, s, color):
    """Drop shape ~ s tall, tip up."""
    return path(g, [((cx, cy - s), (0, 0), (s * 0.55, s * 0.5)), ((cx, cy + s * 0.45), (s * 0.55, -s * 0.1), (-s * 0.55, -s * 0.1)),
                    ((cx, cy - s), (-s * 0.55, s * 0.5), (0, 0))], color=color, closed=True)


def fade(g, t_in, t_vis, t_out, t_gone):
    o = g.transform.opacity
    o.add_keyframe(0, 0, HOLD) if t_in > 0 else None
    o.add_keyframe(t_in, 0, DECEL); o.add_keyframe(t_vis, 100, HOLD); o.add_keyframe(t_out, 100, ACCEL); o.add_keyframe(t_gone, 0, HOLD)
