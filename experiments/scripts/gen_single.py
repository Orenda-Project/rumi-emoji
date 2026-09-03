#!/usr/bin/env python3
"""Generate ONE blank-face Rumi slime body (not a grid) via Gemini nano-banana-pro.

usage: gen_single.py <name> "<body description>" <out.png> [--big-face]
Reuses opening_blank / closing_blank / negative_blank from prompts/slime.json so the character stays
consistent with the grids. --big-face asks for a face patch covering ~60% of the body width so the
composited face survives 22px inline size (gauntlet finding: small patch = unreadable emotion).
"""
import base64, json, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    env = pathlib.Path.home() / "Documents/free_work/personal-agent-v2/.env"
    for line in env.read_text().splitlines() if env.exists() else []:
        if line.startswith("GEMINI_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("GEMINI_API_KEY not set")

name, body, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
big = "--big-face" in sys.argv
d = json.loads((ROOT / "prompts" / "slime.json").read_text())
opening = d["opening_blank"].replace("A single 3x3 grid image", "A single image").replace(
    "showing 9 cute 3D-rendered emoji designs", "showing ONE cute 3D-rendered emoji design").replace(
    "of the SAME character, one per cell, each cell labeled in small gray text below the character.", "of the character, centred, filling about 80% of the frame, no text, no label.")
if big:
    opening = opening.replace("a smooth, completely EMPTY deep NAVY #001F3F rounded face patch",
                              "a VERY LARGE smooth, completely EMPTY deep NAVY #001F3F rounded face patch that fills most of the front of the body - about 78% of the body width and 65% of the body height, like a big dark visor screen, with only a thin rim of pale gel around it")
text = (f"{opening}\n\nThe emotion: {name} - {body}\n\n{d['closing_blank'].replace('evenly spaced grid, each character fully inside its own cell', 'the single character fully inside the frame')}\n\n"
        f"Avoid: {d['negative_blank']}, text, label, caption")
payload = json.dumps({"contents": [{"parts": [{"text": text}]}],
                      "generationConfig": {"imageConfig": {"aspectRatio": "1:1", "imageSize": "1K"}}})
url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={KEY}"
r = subprocess.run(["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", "@-"],
                   input=payload, capture_output=True, text=True)
resp = json.loads(r.stdout)
if "error" in resp:
    sys.exit("ERROR: " + str(resp["error"])[:300])
parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
img = next((p["inlineData"]["data"] for p in parts if "inlineData" in p), None)
if not img:
    sys.exit("no image: " + json.dumps(resp)[:300])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(base64.b64decode(img))
print("saved", out)
