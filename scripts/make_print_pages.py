#!/usr/bin/env python3
"""Print-ready A4 sticker pages: 300 DPI, 55 mm stickers (12 per page), offset cut line around each shape, crop marks.

    python3 scripts/make_print_pages.py                 # every batch -> memes/print/<batch>-A4-55mm.pdf (+ page PNGs) + all-batches PDF
    python3 scripts/make_print_pages.py laptop --mm 70  # one batch, bigger stickers (fewer per page)

Cut line = light grey contour 2 mm outside the sticker's own white border. Cut on or just outside the grey.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DPI = 300
MM = DPI / 25.4
A4 = (int(210 * MM), int(297 * MM))
MARGIN, GAP, BLEED = 10 * MM, 4 * MM, 2 * MM          # page margin, gap between cut lines, cut-line offset (4 mm gap = 3 x 4 of 55 mm on A4)
CUT = (170, 170, 170)
OUT = ROOT / "memes/print"
BATCHES = ["", "taleemabad", "dev-ai", "desi-office", "laptop"]   # "" = memes/ root batch


def stickers(batch):
    d = ROOT / "memes" / batch if batch else ROOT / "memes"
    cfg = json.loads((d / "prompts.json").read_text())
    return [(s["id"], d / "png" / f"rumi-meme-{s['id']}.png") for s in cfg["stickers"] if (d / "png" / f"rumi-meme-{s['id']}.png").exists()]


def outer_silhouette(mask):
    """255 everywhere that is NOT reachable from the border through transparent pixels (fills interior holes)."""
    m = mask.copy()
    ImageDraw.floodfill(m, (0, 0), 128)                          # outside -> 128 (border pixel is always transparent: tile has padding)
    return m.point(lambda v: 0 if v == 128 else 255)


def sticker_tile(path, size_px):
    """sticker scaled to fit `size_px` inside a tile that also holds the cut line."""
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())                                  # trim transparent slack so 60 mm = the sticker itself
    im.thumbnail((size_px, size_px), Image.LANCZOS)
    pad = int(BLEED * 2 + 4)
    tile = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    tile.alpha_composite(im, (pad, pad))
    # cut line: dilate the alpha by BLEED (at 1/4 scale for speed), round the corners with a blur+threshold,
    # then stroke the edge (outer minus slightly eroded outer)
    import numpy as np
    a = tile.getchannel("A").point(lambda v: 255 if v > 8 else 0)
    a = outer_silhouette(a)                                      # ignore holes inside the sticker: cut line = outside edge only
    small = a.resize((a.width // 4, a.height // 4), Image.BOX)
    k = max(3, (int(BLEED) // 4) * 2 + 1)
    outer = small.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 128 else 0)
    outer = outer.resize(a.size, Image.LANCZOS).point(lambda v: 255 if v > 128 else 0)
    inner = outer.filter(ImageFilter.MinFilter(5))              # ~2 px line
    line = Image.new("RGBA", tile.size, CUT + (0,))
    line.putalpha(Image.fromarray(np.clip(np.array(outer, int) - np.array(inner, int), 0, 255).astype("uint8")))
    tile.alpha_composite(line)
    return tile


def crop_marks(d, W, H):
    m, l = int(MARGIN * 0.5), int(4 * MM)
    for x, y, dx, dy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line((x, y, x + dx * l, y), fill=(0, 0, 0), width=2); d.line((x, y, x, y + dy * l), fill=(0, 0, 0), width=2)


def pages_for(batch, mm):
    items = stickers(batch)
    if not items:
        return []
    size = int(mm * MM)
    W, H = A4
    cell = size + 2 * BLEED + 8
    cols = int((W - 2 * MARGIN + GAP) // (cell + GAP)); rows = int((H - 2 * MARGIN + GAP) // (cell + GAP))
    per = cols * rows
    pages = []
    for p in range(0, len(items), per):
        page = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(page)
        crop_marks(d, W, H)
        for i, (sid, path) in enumerate(items[p:p + per]):
            tile = sticker_tile(path, size)
            x = int(MARGIN + (i % cols) * (cell + GAP) + (cell - tile.width) / 2)
            y = int(MARGIN + (i // cols) * (cell + GAP) + (cell - tile.height) / 2)
            page.paste(tile, (x, y), tile)
        d.text((int(MARGIN), H - int(MARGIN * 0.8)), f"Rumi stickers - {batch or 'general'} - {mm} mm - print at 100% / actual size, 300 DPI, A4 - page {len(pages) + 1}", fill=(120, 120, 120))
        pages.append(page)
    return pages


if __name__ == "__main__":
    args = sys.argv[1:]
    mm = 55                                                     # 55 mm = 3 x 4 per A4 with cut lines; 60 mm only fits 2 x 4
    if "--mm" in args:
        mm = int(args[args.index("--mm") + 1]); args = [a for a in args if a not in ("--mm", str(mm))]
    batches = args or BATCHES
    OUT.mkdir(parents=True, exist_ok=True)
    everything = []
    for b in batches:
        pages = pages_for(b, mm)
        if not pages:
            continue
        name = f"{b or 'general'}-A4-{mm}mm"
        for i, pg in enumerate(pages, 1):
            pg.save(OUT / f"{name}-p{i}.png", dpi=(DPI, DPI))
        pages[0].save(OUT / f"{name}.pdf", save_all=True, append_images=pages[1:], resolution=DPI)
        everything += pages
        print(f"{name}: {len(pages)} page(s), {len(stickers(b))} stickers")
    if len(batches) > 1 and everything:
        everything[0].save(OUT / f"all-batches-A4-{mm}mm.pdf", save_all=True, append_images=everything[1:], resolution=DPI)
        print(f"all-batches-A4-{mm}mm.pdf: {len(everything)} pages")
    assert all(p.size == A4 for p in everything)
