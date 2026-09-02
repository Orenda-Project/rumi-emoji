#!/usr/bin/env python3
"""Generate the slime-body Rumi emoji grids (prompts/slime.json) via Gemini nano-banana-pro.

usage: python3 scripts/generate_slime.py [1 2 ...]   # grid numbers; default all
Skips grids whose output file already exists. Needs GEMINI_API_KEY (env, or
personal-agent-v2/.env as fallback).
"""
import base64, json, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:  # ponytail: read the one .env we know has it instead of a dotenv dep
    env = pathlib.Path.home() / "Documents/free_work/personal-agent-v2/.env"
    for line in env.read_text().splitlines() if env.exists() else []:
        if line.startswith("GEMINI_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("GEMINI_API_KEY not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={KEY}"
data = json.loads((ROOT / "prompts" / "slime.json").read_text())
only = {int(a) for a in sys.argv[1:]}

for i, g in enumerate(data["grids"], 1):
    if only and i not in only:
        continue
    out = ROOT / g["file"]
    if out.exists():
        print(f"skip (exists): {out.name}")
        continue
    out.parent.mkdir(parents=True, exist_ok=True)
    k = "_blank" if data.get("blank_face") else ""  # blank-face mode: logo pasted on later by scripts/paste_face.py
    text = (f"{data['opening'+k]}\n\nThe 9 emotions: {g['emotions']}\n\n{data['closing'+k]}\n\n"
            f"Avoid: {data['negative'+k]}")
    parts = [{"text": text}]
    if data.get("reference_image"):  # logo mark as image input - never describe the logo in prose
        img_b64 = base64.b64encode(pathlib.Path(data["reference_image"]).read_bytes()).decode()
        parts = [{"text": data["reference_role"]}, {"inlineData": {"mimeType": "image/png", "data": img_b64}}] + parts
    payload = json.dumps({"contents": [{"parts": parts}],
                          "generationConfig": {"imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"}}})
    print(f"generating grid {i} - {g['theme']} ...")
    r = subprocess.run(["curl", "-s", "-X", "POST", URL, "-H", "Content-Type: application/json", "-d", "@-"],
                       input=payload, capture_output=True, text=True)
    try:
        resp = json.loads(r.stdout)
    except Exception:
        print("  bad response:", r.stdout[:300]); continue
    if "error" in resp:
        print("  ERROR:", str(resp["error"])[:300]); time.sleep(3); continue
    parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    img = next((p["inlineData"]["data"] for p in parts if "inlineData" in p), None)
    if not img:
        print("  no image:", json.dumps(resp)[:300]); continue
    out.write_bytes(base64.b64decode(img))
    print(f"  saved {out}")
    time.sleep(2)
