# Print-ready sticker pages

A4, 300 DPI, made by `scripts/make_print_pages.py`. Two sizes:

| File | Sticker size | Per page | Use |
|---|---|---|---|
| `<batch>-A4-55mm.pdf` · `all-batches-A4-55mm.pdf` (9 pages) | **55 mm** (2.2 in) | 12 | Laptop stickers — the common 2–2.5 in size, fits a MacBook lid alongside others |
| `<batch>-A4-60mm.pdf` · `all-batches-A4-60mm.pdf` (10 pages) | **60 mm** (2.4 in) | 8 | Slightly bigger statement sticker |

Every sticker has a **light-grey cut line 2 mm outside its own white border**, following the shape (die-cut).
Corner crop marks show the printable area. Batches: general (10), taleemabad (16), dev-ai (16), desi-office (16), laptop (15) = 73.

## How to print

1. **Paper:** matte or glossy **white vinyl sticker paper**, A4, inkjet or laser depending on your printer. For laptops
   pick vinyl (not paper stickers) — it survives bags and hands. Waterproof vinyl plus a clear laminate layer on top
   is what sticker shops do.
2. **Printer settings:** A4, **100% / actual size / no scaling**, highest quality, borderless off. The page has
   10 mm margins so any printer handles it. Check one printed sticker with a ruler: 55 mm across.
3. **Cutting by hand:** cut on or just outside the grey line with scissors or a craft knife. The 2 mm white
   margin means small wobbles are invisible.
4. **Cutting machine (Cricut / Silhouette / Cameo):** import the page PNG (`*-p1.png`, regenerate with the
   script if not present) and use "print then cut", or trace the grey line as the cut path; "kiss cut" so the
   backing stays in one piece.
5. **Print shop:** send the PDF, ask for "A4 die-cut stickers, kiss-cut on the grey contour, matte vinyl
   with lamination". They can also do the cut from the PNG alpha of `memes/<batch>/png/`.

## Regenerate

```bash
python3 scripts/make_print_pages.py            # 55 mm, all batches
python3 scripts/make_print_pages.py --mm 60    # 60 mm
python3 scripts/make_print_pages.py laptop --mm 70   # one batch, 70 mm (6 per page)
```

Page PNGs (`*-pN.png`, 2480×3508) are written next to the PDFs but not committed (the PDFs hold the same pages).
