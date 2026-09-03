#!/usr/bin/env python3
"""Rumi logo-mark emoji -> Lottie animations (flipbook of parameterised SVG frames).

usage: python3 scripts/make_lottie.py [emotion ...]     # default: all 12
Output: lottie/<emotion>.json, lottie/preview.html, lottie/contact-sheet.png
Needs: python-lottie, cairosvg, and asset-studio's svg_to_lottie.py (path below).
"""
import math, os, pathlib, subprocess, sys, json, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lottie"
CONV = pathlib.Path.home() / "Documents/free_work/personal-agent-v2/.claude/skills/asset-studio/scripts/svg_to_lottie.py"

# --- art direction ------------------------------------------------------------
NAVY = "#001240"      # sampled from rumi-mark-navy-transparent.png
RED = "#8A1C1C"       # angry mark
TONGUE = "#E8736F"
HAT = "#D6362B"
TEAR = "#6FA8DC"
LID = "#9AA3AD"
BUBBLE = "#B8C4D0"
W, H = 160, 100        # viewBox; mark sits in the top-middle, props around it
LX, RX, EY = 44, 116, 36   # dot centres
R = 10                 # dot radius
SW = 6                 # curve stroke
N = 30                 # frames per loop (30fps, 1 tick each = 1s)
FPS = 30


def ease(t):  # 0..1 -> 0..1..0 smooth pulse
    return 0.5 - 0.5 * math.cos(2 * math.pi * t)


def dot(cx, cy, rx=R, ry=R, fill=NAVY):
    return f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}"/>'


def curve(depth=26, color=NAVY, lx=LX, rx=RX, y=EY, flip=False):
    """Smile: cubic from left dot to right dot, bottom at y+depth. flip=True -> frown (bulges up, sits lower)."""
    if flip:
        y0 = y + 24
        return (f'<path d="M{lx} {y0} C {lx+18} {y0-depth}, {rx-18} {y0-depth}, {rx} {y0}" '
                f'fill="none" stroke="{color}" stroke-width="{SW}" stroke-linecap="round"/>')
    return (f'<path d="M{lx} {y} C {lx+10} {y+depth*1.35}, {rx-10} {y+depth*1.35}, {rx} {y}" '
            f'fill="none" stroke="{color}" stroke-width="{SW}" stroke-linecap="round"/>')


def svg(*parts):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">' + "".join(parts) + "</svg>"


def mark(color=NAVY, depth=26, dy=0, lry=R, rry=R, flip=False):
    return dot(LX, EY + dy, R, lry, color) + dot(RX, EY + dy, R, rry, color) + curve(depth, color, y=EY + dy, flip=flip)


# --- the 12 emotions: each returns SVG for frame i of N -------------------------
def happy(i):
    p = ease(i / N)
    return svg(mark(depth=24 + 6 * p, dy=-2 * p, lry=R - 1.5 * p, rry=R - 1.5 * p))


def tongue(i):
    p = ease(i / N)
    wig = math.sin(i / N * 4 * math.pi) * 3
    ty = EY + 30
    return svg(mark(),
               f'<ellipse cx="{80 + wig:.2f}" cy="{ty + 4 + 6 * p:.2f}" rx="7" ry="{6 + 5 * p:.2f}" fill="{TONGUE}"/>',
               f'<rect x="73" y="{ty - 8}" width="14" height="10" fill="none"/>')


def santa(i):
    p = ease(i / N)
    tilt = -8 + 6 * p
    hx, hy = RX, EY - R
    hat = (f'<g transform="rotate({tilt:.2f} {hx} {hy})">'
           f'<path d="M{hx-13} {hy+2} L{hx+2} {hy-22} Q{hx+14} {hy-30} {hx+16} {hy-16} L{hx+14} {hy+2} Z" fill="{HAT}"/>'
           f'<rect x="{hx-15}" y="{hy-1}" width="31" height="6" rx="3" fill="white" stroke="{NAVY}" stroke-width="1"/>'
           f'<circle cx="{hx+16}" cy="{hy-16}" r="4" fill="white" stroke="{NAVY}" stroke-width="1"/></g>')
    return svg(mark(dy=-1.5 * p), hat)


def wink(i):
    t = i / N
    # eye closes between 0.25..0.45, stays shut, opens 0.55..0.75
    if t < 0.2 or t > 0.8: k = 0
    elif t < 0.3: k = (t - 0.2) / 0.1
    elif t < 0.7: k = 1
    else: k = 1 - (t - 0.7) / 0.1
    rry = R - (R - 2.4) * k
    spark = ""
    if k > 0.6:
        a = (k - 0.6) / 0.4
        for ang, ln in ((-60, 9), (-25, 11), (10, 9)):
            x0 = RX + 13 * math.cos(math.radians(ang)); y0 = EY - 6 + 13 * math.sin(math.radians(ang))
            x1 = x0 + ln * a * math.cos(math.radians(ang)); y1 = y0 + ln * a * math.sin(math.radians(ang))
            spark += f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>'
    return svg(dot(LX, EY) + dot(RX, EY, R + 4 * k, rry) + curve(26 + 3 * k), spark)


def sad(i):
    t = i / N
    ty = EY + R + 4 + 34 * t           # tear falls
    op = 1 if t < 0.8 else 1 - (t - 0.8) / 0.2
    tear = f'<path d="M{RX+8} {ty-9} q6 8 0 12 q-6 -4 0 -12z" fill="{TEAR}" opacity="{op:.2f}"/>'
    return svg(mark(depth=18, flip=True, dy=2 * ease(t)), tear)


def angry(i):
    sh = 1.6 * math.sin(i / N * 10 * math.pi)     # shake
    p = ease(i / N)
    brows = (f'<line x1="{LX-12+sh:.1f}" y1="{EY-18}" x2="{LX+10+sh:.1f}" y2="{EY-12-3*p:.1f}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
             f'<line x1="{RX+12+sh:.1f}" y1="{EY-18}" x2="{RX-10+sh:.1f}" y2="{EY-12-3*p:.1f}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>')
    return svg(f'<g transform="translate({sh:.2f} 0)">' + mark(color=RED, depth=16, flip=True) + "</g>", brows)


def chef(i):
    p = ease(i / N)
    rot = -20 + 40 * p
    hx, hy = LX, EY - R
    hat = (f'<path d="M{hx-13} {hy+1} L{hx-13} {hy-9} Q{hx-20} {hy-24} {hx-6} {hy-22} Q{hx} {hy-34} {hx+9} {hy-22} '
           f'Q{hx+20} {hy-22} {hx+13} {hy-9} L{hx+13} {hy+1} Z" fill="white" stroke="{NAVY}" stroke-width="2"/>')
    wx, wy = LX - 16, EY + 22
    whisk = (f'<g transform="rotate({rot:.1f} {wx} {wy})"><line x1="{wx}" y1="{wy}" x2="{wx}" y2="{wy-22}" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>'
             f'<ellipse cx="{wx}" cy="{wy-30}" rx="6" ry="9" fill="none" stroke="{NAVY}" stroke-width="2"/>'
             f'<line x1="{wx}" y1="{wy-22}" x2="{wx}" y2="{wy-39}" stroke="{NAVY}" stroke-width="2"/></g>')
    return svg(mark(), hat, whisk)


def tie(i):
    p = ease(i / N)
    sw = -6 + 12 * p
    tx, ty = 80, EY + 30
    knot = (f'<g transform="rotate({sw:.1f} {tx} {ty})">'
            f'<path d="M{tx-5} {ty} L{tx+5} {ty} L{tx+3} {ty+8} L{tx-3} {ty+8} Z" fill="{NAVY}"/>'
            f'<path d="M{tx-3} {ty+8} L{tx+3} {ty+8} L{tx+5} {ty+26} L{tx} {ty+32} L{tx-5} {ty+26} Z" fill="{NAVY}"/></g>')
    collar = (f'<path d="M{tx-14} {ty-6} L{tx-4} {ty+2} L{tx-5} {ty-8} Z" fill="white" stroke="{NAVY}" stroke-width="2"/>'
              f'<path d="M{tx+14} {ty-6} L{tx+4} {ty+2} L{tx+5} {ty-8} Z" fill="white" stroke="{NAVY}" stroke-width="2"/>')
    blink = i in (12, 13)
    return svg(mark(lry=2.5 if blink else R, rry=2.5 if blink else R), collar, knot)


def crying(i):
    t = i / N
    tears = ""
    for x, off in ((LX - 6, 0.0), (RX + 6, 0.5)):
        for k in range(2):
            tt = (t + off + k * 0.5) % 1
            y = EY + R + 4 + 30 * tt
            tears += f'<path d="M{x} {y-8} q5 7 0 10 q-5 -3 0 -10z" fill="{TEAR}" opacity="{1 - tt:.2f}"/>'
    return svg(mark(depth=20, flip=True, dy=1.5 * ease(t)), tears)


def thinking(i):
    t = i / N
    bx, by = RX + 22, EY - 22
    k = int(t * 3) % 3   # bubbles pop in one by one
    dots = "".join(f'<circle cx="{bx-14+j*5:.1f}" cy="{by+12-j*4:.1f}" r="{2+j:.1f}" fill="{BUBBLE}"/>' for j in range(3) if j <= k)
    cloud = (f'<g><ellipse cx="{bx}" cy="{by}" rx="15" ry="10" fill="none" stroke="{BUBBLE}" stroke-width="2.5"/>'
             f'<ellipse cx="{bx-8}" cy="{by-6}" rx="7" ry="6" fill="white" stroke="{BUBBLE}" stroke-width="2.5"/>'
             f'<ellipse cx="{bx+7}" cy="{by-7}" rx="6" ry="5" fill="white" stroke="{BUBBLE}" stroke-width="2.5"/></g>')
    look = -2 * ease(t)
    return svg(dot(LX, EY + look) + dot(RX, EY + look) + curve(20), dots, cloud)


def sleeping(i):
    t = i / N
    lids = "".join(f'<path d="M{x-R} {EY} A{R} {R} 0 0 1 {x+R} {EY} Z" fill="{LID}"/>' for x in (LX, RX))  # top half-disc = closed lid
    zs = ""
    for k, (sz, dx) in enumerate(((5, 0), (7, 8), (10, 18))):
        tt = (t - k * 0.2) % 1
        y = EY - 12 - 22 * tt; op = 1 - tt
        zs += (f'<path d="M{100+dx} {y-sz} h{sz} l-{sz} {sz} h{sz}" fill="none" stroke="{NAVY}" stroke-width="{1.5+k*0.6:.1f}" '
               f'stroke-linecap="round" stroke-linejoin="round" opacity="{op:.2f}"/>')
    return svg(dot(LX, EY, fill=NAVY) + dot(RX, EY, fill=NAVY), lids, curve(14 + 2 * ease(t)), zs)


def laugh(i):
    p = ease(i / N)
    y = EY - 3 * p
    inner = 8 + 6 * p
    mouth = (f'<path d="M{LX+6} {y+10} C {LX+16} {y+22+inner}, {RX-16} {y+22+inner}, {RX-6} {y+10}" '
             f'fill="none" stroke="{NAVY}" stroke-width="{SW}" stroke-linecap="round"/>')
    return svg(dot(LX, y, R, R - 2 * p) + dot(RX, y, R, R - 2 * p) + curve(26 + 8 * p, y=y), mouth)


EMOTIONS = {"happy": happy, "tongue": tongue, "santa": santa, "wink": wink, "sad": sad, "angry": angry,
            "chef": chef, "tie": tie, "crying": crying, "thinking": thinking, "sleeping": sleeping, "laugh": laugh}


def build(name):
    fn = EMOTIONS[name]
    with tempfile.TemporaryDirectory() as td:
        frames = []
        for i in range(N):
            p = pathlib.Path(td) / f"{name}-{i:02d}.svg"
            p.write_text(fn(i)); frames.append(str(p))
        out = OUT / f"rumi-{name}.json"
        subprocess.run([sys.executable, str(CONV), str(out), *frames, "--ticks", "1", "--fps", str(FPS)], check=True, capture_output=True)
    return out


def preview(names):
    cards = "".join(f'<div class="c"><div id="a-{n}"></div><p>rumi-{n}</p></div>' for n in names)
    data = {n: json.loads((OUT / f"rumi-{n}.json").read_text()) for n in names}
    html = f"""<!doctype html><meta charset="utf-8"><title>Rumi mark — Lottie</title>
<style>body{{font-family:Inter,system-ui,sans-serif;background:#f6f3ec;margin:0;padding:24px;color:#001240}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px}}.c{{background:#fff;border-radius:16px;padding:12px;text-align:center}}
.c div{{width:100%;aspect-ratio:1.6}}p{{margin:6px 0 0;font-size:13px}}input{{width:300px}}</style>
<h1>The World of Rumi — Lottie</h1><p>Scale <input type="range" min="0.4" max="2" step="0.1" value="1" oninput="document.querySelector('.g').style.zoom=this.value"></p>
<div class="g">{cards}</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<script>const D={json.dumps(data)};for(const n in D)lottie.loadAnimation({{container:document.getElementById('a-'+n),renderer:'svg',loop:true,autoplay:true,animationData:D[n]}});</script>"""
    (OUT / "preview.html").write_text(html)


def contact_sheet(names):
    from lottie.parsers.tgs import parse_tgs
    from lottie.exporters.cairo import export_png
    from PIL import Image
    tiles = []
    for n in names:
        an = parse_tgs(str(OUT / f"rumi-{n}.json"))
        row = []
        for fr in (0, 15, 24):
            buf = OUT / f"_{n}-{fr}.png"
            with open(buf, "wb") as fh: export_png(an, fh, frame=fr, dpi=192)
            row.append(Image.open(buf).convert("RGBA")); buf.unlink()
        tiles.append(row)
    tw, th = tiles[0][0].size
    sheet = Image.new("RGBA", (3 * tw, len(names) * th), (246, 243, 236, 255))
    for r, row in enumerate(tiles):
        for c, im in enumerate(row): sheet.alpha_composite(im, (c * tw, r * th))
    sheet.save(OUT / "contact-sheet.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    names = sys.argv[1:] or list(EMOTIONS)
    for n in names:
        print("build", build(n).name)
    preview(list(EMOTIONS) if not sys.argv[1:] else names)
    contact_sheet(names)
    print("ok ->", OUT)
