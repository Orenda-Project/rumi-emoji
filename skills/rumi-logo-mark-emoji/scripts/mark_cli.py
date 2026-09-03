#!/usr/bin/env python3
"""One-off logo-mark faces + the edge check, without editing the EMOTIONS table.

  python3 mark_cli.py list
  python3 mark_cli.py render lol --out lol.png [--bg]          # any name from PACK or EMOTIONS
  python3 mark_cli.py compose --eyes dot --mouth flat --prop check --link --out ok.png [--bg]
  python3 mark_cli.py check emoji-mark-emotions/512             # fails if any PNG touches the canvas edge

eyes : dot big small lid lid-sad lid-angry x arch closed heart star spiral look ring
mouth: none curve flat o open openfrown zigzag smirk wavy smile-small teeth tongue frown
prop : none sweat blush hearts sparkles anger bulb check spinner hourglass glasses shades halo
       horns party headphones coffee music cloud burst thermo mask zip tear moon zzz ? ! ...
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw
import logo_mark_pack as LP
import logo_mark_emotions as LE

EYES = {"dot": LE.DOTS, "big": LE.E(LE.eye_big), "small": LE.E(LE.eye_small), "lid": LE.E(LE.eye_lid),
        "lid-sad": LE.E(LE.eye_lid, tilt=0.5), "lid-angry": LE.E(LE.eye_lid, tilt=-0.5), "x": LE.E(LE.eye_x),
        "arch": LE.E(LE.eye_arch), "closed": LE.E(LE.eye_closed), "heart": LE.E(LE.eye_heart), "star": LE.E(LE.eye_star),
        "spiral": LE.E(LE.eye_spiral), "look": LE.E(LE.eye_look), "ring": LE.E(LE.eye_ring), "wink": lambda d: (LP.dot(d, *LP.P(LP.EXL, LP.EY), LE.r_()), LE.eye_arch(d, LP.EXR))}
MOUTHS = {"none": None, "curve": None, "flat": LE.m_flat, "o": LE.m_o, "open": LE.m_open, "openfrown": LE.m_openfrown,
          "zigzag": LE.m_zigzag, "smirk": LE.m_smirk, "wavy": LE.m_wavy, "smile-small": LE.m_smile_small,
          "teeth": LE.m_teeth, "tongue": LE.m_tongue_side, "frown": lambda d: LP.frown(d)}
PROPS = {"none": None, "sweat": LE.p_sweat, "blush": LE.p_blush, "hearts": LE.p_hearts, "sparkles": LE.p_sparkles,
         "anger": LE.p_anger, "bulb": LE.p_bulb, "check": LE.p_check, "spinner": LE.p_spinner, "hourglass": LE.p_hourglass,
         "glasses": LE.p_glasses, "shades": LE.p_shades, "halo": LE.p_halo, "horns": LE.p_horns, "party": LE.p_party,
         "headphones": LE.p_headphones, "coffee": LE.p_coffee, "music": LE.p_music, "cloud": LE.p_cloud, "burst": LE.p_burst,
         "thermo": LE.p_thermo, "mask": LE.p_mask, "zip": LE.p_zip, "tear": LE.p_tear_l, "moon": LE.p_moon, "zzz": LP.prop_zzz,
         "?": lambda d: LE.text_glyph(d, "?", LE.near_right(1.7, -1.9), 1.1),
         "!": lambda d: LE.text_glyph(d, "!", LE.near_right(1.6, -1.9), 1.2),
         "...": lambda d: LE.text_glyph(d, "...", LE.near_right(2.0, -1.4), 1.0)}


def touches_edge(im):
    b = im.getbbox(); w, h = im.size
    return b is None or b[0] <= 1 or b[1] <= 1 or b[2] >= w - 1 or b[3] >= h - 1


def save(im, out, bg):
    if bg:
        base = Image.new("RGBA", im.size, LP.CREAM); base.alpha_composite(im); im = base
    im.save(out); print(("EDGE-CLIPPED " if touches_edge(im if not bg else Image.open(out)) and not bg else "") + f"-> {out}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    r = sub.add_parser("render"); r.add_argument("name"); r.add_argument("--out", required=True); r.add_argument("--bg", action="store_true")
    c = sub.add_parser("compose"); c.add_argument("--eyes", default="dot"); c.add_argument("--mouth", default="curve")
    c.add_argument("--prop", default="none"); c.add_argument("--link", action="store_true", help="draw the connecting logo curve")
    c.add_argument("--out", required=True); c.add_argument("--bg", action="store_true")
    k = sub.add_parser("check"); k.add_argument("dir")
    a = ap.parse_args()
    if a.cmd == "list":
        print("pack:", *LP.PACK); print("emotions:", *LE.EMOTIONS)
    elif a.cmd == "render":
        im = LP.render(a.name) if a.name in LP.PACK else LE.render(a.name.replace("rumi-mark-", ""))
        save(im, a.out, a.bg)
    elif a.cmd == "compose":
        link = a.link or a.mouth == "curve"
        draw = LE.face(EYES[a.eyes], MOUTHS[a.mouth], PROPS[a.prop], link=link)
        im = Image.new("RGBA", (LP.SIZE * LP.SS, LP.SIZE * LP.SS), (0, 0, 0, 0)); draw(ImageDraw.Draw(im))
        save(im.resize((LP.SIZE, LP.SIZE), Image.LANCZOS), a.out, a.bg)
    elif a.cmd == "check":
        bad = [p.name for p in sorted(Path(a.dir).glob("*.png")) if touches_edge(Image.open(p))]
        print("edge-touching:", bad or "none"); sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
