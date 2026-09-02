#!/usr/bin/env python3
"""Compose meme stickers: v6 emoji + caption -> 512x512 PNG (+ WebP for WhatsApp).

usage: python3 scripts/make_stickers.py [stickers/pack.json]
Edit pack.json (text + emoji name), rerun. Output: stickers/<pack>/png/*.png, webp/*.webp, preview.png
"""
import json, sys, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / (sys.argv[1] if len(sys.argv) > 1 else "stickers/pack.json")).read_text())
S = spec.get("size", 512)
EMOJI_DIR = ROOT / "emoji-slime-v6/512"
OUT = ROOT / "stickers" / spec["pack"]
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"  # ponytail: Inter (brand font) isn't installed; swap path if it is
NAVY = (0, 31, 63, 255)
PAD = 18


def fit_text(draw, text, max_w, max_h, start=72, floor=30):
    """Largest font size where text fits in max_w x max_h using <=2 lines."""
    for size in range(start, floor - 1, -2):
        f = ImageFont.truetype(FONT, size)
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= max_w:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 2 and all(draw.textlength(l, font=f) <= max_w for l in lines):
            h = sum(f.getbbox(l)[3] - f.getbbox(l)[1] for l in lines) + (len(lines) - 1) * 6
            if h <= max_h:
                return f, lines
    return ImageFont.truetype(FONT, floor), [text]


def make(text, emoji):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    text_h = int(S * 0.30)
    art_h = S - text_h - PAD
    art = Image.open(EMOJI_DIR / f"{emoji}.png").convert("RGBA")
    art.thumbnail((S - 2 * PAD, art_h), Image.LANCZOS)
    im.alpha_composite(art, ((S - art.width) // 2, PAD + (art_h - art.height) // 2))
    f, lines = fit_text(draw, text, S - 2 * PAD, text_h - PAD)
    stroke = max(4, f.size // 9)
    heights = [f.getbbox(l)[3] - f.getbbox(l)[1] for l in lines]
    y = S - PAD - sum(heights) - (len(lines) - 1) * 6
    for l, h in zip(lines, heights):
        w = draw.textlength(l, font=f)
        draw.text(((S - w) / 2, y - f.getbbox(l)[1]), l, font=f, fill="white", stroke_width=stroke, stroke_fill=NAVY)
        y += h + 6
    return im


def main():
    (OUT / "png").mkdir(parents=True, exist_ok=True)
    (OUT / "webp").mkdir(exist_ok=True)
    tiles = []
    for s in spec["stickers"]:
        im = make(s["text"], s["emoji"])
        im.save(OUT / "png" / s["file"])
        im.save(OUT / "webp" / s["file"].replace(".png", ".webp"), "WEBP", quality=85, method=6)  # WhatsApp: 512x512 webp <100KB
        tiles.append(im)
        print(" ", s["file"])
    cols, t = 6, 256
    rows = -(-len(tiles) // cols)
    sheet = Image.new("RGBA", (cols * t, rows * t), (235, 240, 248, 255))
    for i, im in enumerate(tiles):
        im = im.resize((t, t), Image.LANCZOS)
        sheet.alpha_composite(im, ((i % cols) * t, (i // cols) * t))
    sheet.save(OUT / "preview.png")
    assert all((OUT / "webp" / s["file"].replace(".png", ".webp")).stat().st_size < 100_000 for s in spec["stickers"]), "a webp is over WhatsApp's 100KB cap"
    print(f"{len(tiles)} stickers -> {OUT}")


if __name__ == "__main__":
    main()
