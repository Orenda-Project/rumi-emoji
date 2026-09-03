#!/usr/bin/env python3
"""Rumi meme stickers: ink stick-figure webcomic style, face = the Rumi mark passed as a reference image.

    python3 scripts/generate_memes.py            # all stickers in memes/prompts.json -> memes/raw/<id>.png
    python3 scripts/generate_memes.py chai-break # just some (regenerate a reject: delete memes/raw/<id>.png first)
    python3 scripts/generate_memes.py --sheet    # memes/png/<id>.png (white->transparent) + memes/preview.png

Needs GEMINI_API_KEY (env or personal-agent-v2/.env). Skips ids whose raw file already exists.
"""
import base64, json, os, pathlib, subprocess, sys, time
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    for line in (pathlib.Path.home() / "Documents/free_work/personal-agent-v2/.env").read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
if not KEY:
    sys.exit("GEMINI_API_KEY not set")
CFG = json.loads((ROOT / "memes/prompts.json").read_text())
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{CFG['model']}:generateContent?key={KEY}"
RAW, PNG = ROOT / "memes/raw", ROOT / "memes/png"


def generate(st):
    out = RAW / f"{st['id']}.png"
    if out.exists():
        print(f"skip (exists): {out.name}"); return
    RAW.mkdir(parents=True, exist_ok=True)
    ref = base64.b64encode((ROOT / CFG["reference_image"]).read_bytes()).decode()
    text = (f"{CFG['style']}\n\nSCENE: {st['scene']}\n\nCAPTION (hand-lettered, exactly this, nothing else): \"{st['text']}\"\n\n"
            f"Avoid: {CFG['negative']}")
    parts = [{"text": CFG["reference_role"]}, {"inlineData": {"mimeType": "image/png", "data": ref}}, {"text": text}]
    payload = json.dumps({"contents": [{"parts": parts}],
                          "generationConfig": {"imageConfig": {"aspectRatio": "1:1", "imageSize": "1K"}}})
    print(f"generating {st['id']} ...")
    r = subprocess.run(["curl", "-s", "-X", "POST", URL, "-H", "Content-Type: application/json", "-d", "@-"],
                       input=payload, capture_output=True, text=True)
    try:
        resp = json.loads(r.stdout)
    except Exception:
        print("  bad response:", r.stdout[:300]); return
    if "error" in resp:
        print("  ERROR:", str(resp["error"])[:300]); time.sleep(3); return
    img = next((p["inlineData"]["data"] for p in resp.get("candidates", [{}])[0].get("content", {}).get("parts", []) if "inlineData" in p), None)
    if not img:
        print("  no image:", json.dumps(resp)[:300]); return
    out.write_bytes(base64.b64decode(img)); print(f"  saved {out}")
    time.sleep(2)


def sheet():
    PNG.mkdir(parents=True, exist_ok=True)
    ids = [s["id"] for s in CFG["stickers"] if (RAW / f"{s['id']}.png").exists()]
    cols, cell = 5, 400
    sh = Image.new("RGB", (cols * cell, -(-len(ids) // cols) * cell), "white"); dr = ImageDraw.Draw(sh)
    for i, sid in enumerate(ids):
        im = Image.open(RAW / f"{sid}.png").convert("RGBA")
        px = im.load(); w, h = im.size                      # ponytail: near-white -> transparent, good enough for die-cut
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if r > 235 and g > 235 and b > 235: px[x, y] = (255, 255, 255, 0)
        im.save(PNG / f"rumi-meme-{sid}.png")
        x, y = (i % cols) * cell, (i // cols) * cell
        flat = Image.new("RGBA", im.size, "white"); flat.alpha_composite(im)   # preview shows the die-cut result, not the raw
        sh.paste(flat.convert("RGB").resize((cell - 20, cell - 20)), (x + 10, y + 10))
        dr.text((x + 14, y + cell - 24), sid, fill="#0B2545")
    sh.save(ROOT / "memes/preview.png"); print(f"{len(ids)} stickers -> memes/png, preview -> memes/preview.png")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--sheet"]:
        sheet()
    else:
        for st in CFG["stickers"]:
            if not args or st["id"] in args:
                generate(st)
        sheet()
