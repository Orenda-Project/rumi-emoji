#!/usr/bin/env python3
"""Mode-2 character animation via Kie.ai nano-banana-2 (per-frame edits of a
locked base plate), adapted from the character-animation skill's Gemini flow.

Pipeline: emoji PNG -> chroma-green base plate -> upload -> N pose-edit
generations -> chroma key -> weighted-timing transparent GIF (128px).
"""
import json, os, sys, time, subprocess, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROMA = (0, 177, 64)  # #00B140
API = "https://api.kie.ai/api/v1"


def kie_key():
    for line in open(os.path.expanduser(
            "~/Documents/free_work/agent-skills-taleemabad/TOKENS.md")):
        if "KIE_API_KEY" in line and "=" in line:
            return line.split("=", 1)[1].strip().strip('"`')
    sys.exit("no KIE_API_KEY")


def make_base_plate(src_png, out_png, side=1024):
    src = Image.open(src_png).convert("RGBA")
    scale = int(side * 0.72) / max(src.size)
    src = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
    plate = Image.new("RGB", (side, side), CHROMA)
    plate.paste(src, ((side - src.width) // 2, side - src.height - side // 10), src)
    plate.save(out_png)


def upload(path):
    out = subprocess.run(
        ["curl", "-s", "-m", "60", "-F", "reqtype=fileupload",
         "-F", f"fileToUpload=@{path}", "https://catbox.moe/user/api.php"],
        capture_output=True, text=True).stdout.strip()
    if not out.startswith("http"):
        sys.exit(f"upload failed: {out[:200]}")
    return out


def frame_prompt(pose, bg="vivid green"):
    return (
        f"This image shows a small robot character on a flat solid {bg} screen. Output the "
        f"SAME robot with the EXACT same design, colors, art style, the exact same size, and "
        f"the exact same position and framing — the whole body fully visible in the same spot — "
        f"on the same flat solid {bg} background. The ONLY difference from the reference is the "
        f"pose: {pose} Do not move, rescale, rotate, restyle, or crop the character. Flat solid "
        f"{bg} background, no shadow, no text, no labels, no watermark."
    )


def create_task(key, prompt, img_url):
    body = json.dumps({
        "model": "nano-banana-2",
        "input": {"prompt": prompt, "image_input": [img_url],
                  "aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"},
    }).encode()
    req = urllib.request.Request(f"{API}/jobs/createTask", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    if d.get("code") != 200:
        sys.exit(f"createTask failed: {d}")
    return d["data"]["taskId"]


def poll(key, task_id, tries=60, interval=8):
    req = urllib.request.Request(f"{API}/jobs/recordInfo?taskId={task_id}",
                                 headers={"Authorization": f"Bearer {key}"})
    for _ in range(tries):
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())["data"]
        if d["state"] == "success":
            return json.loads(d["resultJson"])["resultUrls"][0]
        if d["state"] in ("fail", "failed"):
            raise RuntimeError(f"task {task_id} failed: {d.get('failMsg')}")
        time.sleep(interval)
    raise TimeoutError(task_id)


def key_out_green(im, tol=115):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if g > 90 and g > r + 40 and g > b + 40:
                px[x, y] = (0, 0, 0, 0)
            elif g > r and g > b and (g - max(r, b)) > 12:
                # despill fringe: pull green channel down to neighbors
                px[x, y] = (r, max(r, b), b, a)
    return im


def main(emotion, poses, weights, out_gif, fps_base_ms=95):
    key = kie_key()
    scratch = Path(os.environ.get("SCRATCH", "/tmp")) / f"kie_{emotion}"
    scratch.mkdir(parents=True, exist_ok=True)
    plate = scratch / "base.png"
    make_base_plate(ROOT / f"emoji/512/{emotion}.png", plate)
    url = upload(plate)
    print("base plate:", url)

    tasks_file = scratch / "tasks.json"
    if tasks_file.exists():
        tasks = json.loads(tasks_file.read_text())
        print("resuming", len(tasks), "existing tasks")
    else:
        tasks = [create_task(key, frame_prompt(p), url) for p in poses]
        tasks_file.write_text(json.dumps(tasks))
        print(f"{len(tasks)} tasks created")
    frames = []
    for i, t in enumerate(tasks):
        fp = scratch / f"frame_{i:02d}.png"
        if not fp.exists():
            res = poll(key, t)
            subprocess.run(["curl", "-s", "-L", "-m", "120",
                            "-A", "Mozilla/5.0 (X11; Linux x86_64)",
                            "-o", str(fp), res], check=True)
        frames.append(fp)
        print(f"frame {i} done")

    imgs = [key_out_green(Image.open(f)).resize((128, 128), Image.LANCZOS) for f in frames]
    TRANS = 95
    base_pal = imgs[0].convert("RGB").quantize(colors=TRANS, method=Image.MEDIANCUT)
    out, durs = [], []
    for im, w in zip(imgs, weights):
        q = im.convert("RGB").quantize(palette=base_pal, dither=Image.NONE)
        q.paste(TRANS, mask=im.split()[3].point(lambda a: 255 if a < 128 else 0))
        out.append(q)
        durs.append(int(fps_base_ms * w))
    out[0].save(out_gif, save_all=True, append_images=out[1:], duration=durs,
                loop=0, transparency=TRANS, disposal=2, optimize=True)
    print("saved", out_gif, os.path.getsize(out_gif) // 1024, "KB")
    return scratch


if __name__ == "__main__":
    # rumi-wave: real wave — paddle sweeps, joyful blink at the inward apex
    poses = [
        "the raised right paddle arm tilted about 25 degrees outward, away from the head, mid-wave.",
        "the raised right paddle arm tilted about 10 degrees outward.",
        "the raised right paddle arm perfectly upright.",
        "the raised right paddle arm tilted about 12 degrees inward, toward the head.",
        "the raised right paddle arm tilted about 25 degrees inward, close to the head, AND both eyes closed into happy upward-curved arcs (joyful blink).",
        "the raised right paddle arm tilted about 12 degrees inward, toward the head.",
        "the raised right paddle arm perfectly upright.",
        "the raised right paddle arm tilted about 10 degrees outward.",
    ]
    # anticipation/apex hold longer, in-betweens rush (character-animation skill weights)
    weights = [1.6, 0.9, 0.95, 0.9, 1.5, 0.9, 0.95, 0.9]
    main("rumi-wave", poses, weights, ROOT / "emoji/gif/rumi-wave.gif")
