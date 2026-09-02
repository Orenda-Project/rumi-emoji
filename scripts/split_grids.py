#!/usr/bin/env python3
"""Cut the 3x3 grids into single transparent-PNG emoji.

Per cell:
1. flood-fill the near-white background (incl. gray cell-divider lines) to
   transparent from the borders — the character's white interior is sealed by
   the navy outline so the fill can't reach it
2. erase the gray label text (neutral-gray pixels in the bottom band)
3. keep the largest connected component + satellites (confetti, zZz, sparkles),
   dropping components that touch the cell edge (art bleeding over from a
   neighboring cell, always cut mid-shape) and dust
4. crop to bbox + margin, pad square, export 512px and 128px PNGs named from
   manifest.json
"""
import json, sys
from collections import deque
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
# usage: split_grids.py [manifest.json] [emoji-out-dir]   (defaults: flat-vector pack)
MANIFEST = json.loads((ROOT / (sys.argv[1] if len(sys.argv) > 1 else "manifest.json")).read_text())
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else "emoji")

BG_MIN = 140      # flood-fill: min channel above this and near-neutral = background
BG_SPREAD = 20  # ponytail: 35 eats the slime's glow fringe but also hollows out bodies whose rim isn't sealed
LABEL_BAND = 0.22  # bottom fraction of the cell that may contain label text
MIN_AREA = 40      # drop dust smaller than this
MARGIN = 14


def is_bg(p):
    r, g, b = p[:3]
    return min(r, g, b) > BG_MIN and (max(r, g, b) - min(r, g, b)) < BG_SPREAD


def flood_transparent(im):
    px = im.load()
    w, h = im.size
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        seen[y * w + x] = 1
        if not is_bg(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))


def erase_label(im):
    px = im.load()
    w, h = im.size
    for y in range(int(h * (1 - LABEL_BAND)), h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and 50 < min(r, g, b) and max(r, g, b) < 215 and (max(r, g, b) - min(r, g, b)) < 30:
                px[x, y] = (0, 0, 0, 0)


def components(im):
    """Connected components of alpha>0. Returns list of (area, bbox, touches_edge, pixels)."""
    px = im.load()
    w, h = im.size
    seen = bytearray(w * h)
    comps = []
    for sy in range(h):
        for sx in range(w):
            if seen[sy * w + sx] or px[sx, sy][3] == 0:
                continue
            q = deque([(sx, sy)])
            seen[sy * w + sx] = 1
            pix, touches = [], False
            x0, y0, x1, y1 = sx, sy, sx, sy
            while q:
                x, y = q.popleft()
                pix.append((x, y))
                if x <= 1 or y <= 1 or x >= w - 2 or y >= h - 2:
                    touches = True
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny][3]:
                        seen[ny * w + nx] = 1
                        q.append((nx, ny))
            comps.append((len(pix), (x0, y0, x1, y1), touches, pix))
    return comps


def process_cell(cell, name, outdirs):
    im = cell.convert("RGBA")
    flood_transparent(im)
    erase_label(im)
    comps = components(im)
    if not comps:
        print(f"  !! nothing left for {name}", file=sys.stderr)
        return
    comps.sort(key=lambda c: -c[0])
    main = comps[0]
    px = im.load()
    keep_bbox = list(main[1])
    for area, bbox, touches, pix in comps[1:]:
        # ponytail: neighbor-cell bleed touches the edge; label leftovers sit
        # strictly below the character; real satellites sit above/beside it
        if area < MIN_AREA or touches or bbox[1] > main[1][3] - 5:
            for x, y in pix:
                px[x, y] = (0, 0, 0, 0)
        else:
            keep_bbox = [min(keep_bbox[0], bbox[0]), min(keep_bbox[1], bbox[1]),
                         max(keep_bbox[2], bbox[2]), max(keep_bbox[3], bbox[3])]
    x0, y0, x1, y1 = keep_bbox
    x0 = max(0, x0 - MARGIN); y0 = max(0, y0 - MARGIN)
    x1 = min(im.width - 1, x1 + MARGIN); y1 = min(im.height - 1, y1 + MARGIN)
    im = im.crop((x0, y0, x1 + 1, y1 + 1))
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    for size, outdir in outdirs.items():
        sq.resize((size, size), Image.LANCZOS).save(outdir / f"{name}.png")


def main():
    outdirs = {512: OUT / "512", 128: OUT / "128"}
    for d in outdirs.values():
        d.mkdir(parents=True, exist_ok=True)
    for grid in MANIFEST["grids"]:
        if not (ROOT / grid["file"]).exists():
            print(f"skip (missing): {grid['file']}"); continue
        im = Image.open(ROOT / grid["file"]).convert("RGB")
        w, h = im.size
        cw, ch = w // 3, h // 3
        print(grid["file"])
        for i, name in enumerate(grid["cells"]):
            r, c = divmod(i, 3)
            cell = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            process_cell(cell, name, outdirs)
            print(f"  {name}")


if __name__ == "__main__":
    main()
