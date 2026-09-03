#!/usr/bin/env python3
"""Compose a Rumi face from eye + mouth glyphs and export it, or composite it onto a blank-face body.

  face_cli.py --left dot --right wink --mouth smile:s --out face.png            # standalone, white on transparent
  face_cli.py --name sleeping --out face.png                                     # one of the 54 named faces
  face_cli.py --left dot:l --right dot:l --mouth o --on-body body.png --out out.png   # onto a body render
  face_cli.py --list                                                             # vocabulary + named faces

--on-body expects a render whose face patch is an EMPTY navy oval (see SKILL.md "Getting a body").
Glyph names: see references/vocabulary.md.
"""
import argparse, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rumi_face  # noqa: E402

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--name", help="a named face from rumi_face.FACES (with or without the rumi- prefix)")
p.add_argument("--left"); p.add_argument("--right"); p.add_argument("--mouth", default="smile:m")
p.add_argument("--link", action="store_true", help="join eyes and mouth with the logo's connecting curve")
p.add_argument("--width", type=int, default=600, help="face width in px for standalone export")
p.add_argument("--on-body", help="PNG of a body with an empty navy face patch to composite onto")
p.add_argument("--out", default="face.png")
p.add_argument("--list", action="store_true")
a = p.parse_args()

if a.list:
    print(rumi_face.__doc__.split("Glyph names")[1])
    for n, (l, r, m, k) in rumi_face.FACES.items():
        print(f"  {n:<18} {l:<10} {r:<10} {m:<10} {'link' if k else ''}")
    sys.exit()

if a.name:
    spec = rumi_face.FACES[a.name.replace("rumi-", "")]
else:
    if not (a.left and a.right):
        sys.exit("need --name, or --left and --right (and optionally --mouth / --link)")
    spec = (a.left, a.right, a.mouth, a.link)

if a.on_body:
    import paste_face  # same folder; carries the patch detection + glow compositing
    rumi_face.FACES["__custom__"] = spec
    src, dst = Path(a.on_body), Path(a.out)
    tmp = dst.with_name("__custom__.png")
    import shutil; shutil.copy(src, tmp)
    paste_face.paste(tmp, tmp, None)
    tmp.rename(dst)
    small = dst.parent.parent / "128"  # paste_face refreshes a sibling 128/ only if it exists; harmless otherwise
else:
    rumi_face.compose(*spec, width=a.width).save(a.out)
print("->", a.out)
