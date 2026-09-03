#!/usr/bin/env python3
"""Two-keyframe crossfade animation: base art (A) -> one AI pose-edit (B) -> A,
eased alpha tween in between. Proven on rumi-wave/rumi-celebrate: AI multi-frame
sequences drift identity on rigid characters, but ONE small, tightly-scoped edit
holds up, and a smoothstep crossfade between two aligned keyframes reads as real
motion without ghosting when the pose delta is small.

Usage:
  python3 tween_animate.py <emotion> "<small pose-edit description>" [--steps 8] [--size 512]
"""
import argparse, colorsys, json, os, sys, time, subprocess, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROMA = (0, 177, 64)
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


def key_out_green(im):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if g > 90 and g > r + 40 and g > b + 40:
                px[x, y] = (0, 0, 0, 0)
            elif g > r and g > b and (g - max(r, b)) > 12:
                px[x, y] = (r, max(r, b), b, a)
    return im


def shared_crop_resize(a, b, size, pad_frac=0.06):
    """Crop both frames to ONE shared box (union of both bboxes, since they share
    the same base-plate coordinate frame by construction) and resize identically —
    normalizing each frame's own bbox independently would rescale the character
    whenever a pose spreads the limbs wider (e.g. clap-apart vs clap-together)."""
    ba, bb = a.getbbox(), b.getbbox()
    box = (min(ba[0], bb[0]), min(ba[1], bb[1]), max(ba[2], bb[2]), max(ba[3], bb[3]))
    side = max(box[2] - box[0], box[3] - box[1])
    pad = int(side * pad_frac)
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    half = side // 2 + pad
    crop_box = (cx - half, cy - half, cx + half, cy + half)

    def fit(im):
        canvas = Image.new("RGBA", (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]), (0, 0, 0, 0))
        canvas.paste(im, (-crop_box[0], -crop_box[1]), im)
        return canvas.resize((size, size), Image.LANCZOS)

    return fit(a), fit(b)


def sample_dark_hs(im):
    px = im.load()
    hs = []
    for y in range(0, im.height, 3):
        for x in range(0, im.width, 3):
            r, g, b, a = px[x, y]
            if a > 200 and (r + g + b) < 260 and max(r, g, b) < 140:
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                hs.append((h, s))
    if not hs:
        return None
    return sum(h for h, s in hs) / len(hs), sum(s for h, s in hs) / len(hs)


def recolor_dark_to_match(ref, target):
    hs = sample_dark_hs(ref)
    if not hs:
        return target
    th, ts = hs
    target = target.copy()
    px = target.load()
    for y in range(target.height):
        for x in range(target.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if v < 0.55 and s > 0.05:
                nr, ng, nb = colorsys.hsv_to_rgb(th, ts, v)
                px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return target


def ease(t):
    return t * t * (3 - 2 * t)


def build_tween_gif(a, b, out_gif, steps=8, fps=24, colors=128):
    frames = [Image.blend(a, b, ease(i / (steps - 1))) for i in range(steps)]
    frames += [Image.blend(b, a, ease(i / (steps - 1))) for i in range(steps)]
    trans = colors
    pal = frames[0].convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT)
    out = []
    for im in frames:
        q = im.convert("RGB").quantize(palette=pal, dither=Image.NONE)
        q.paste(trans, mask=im.split()[3].point(lambda a: 255 if a < 128 else 0))
        out.append(q)
    dur = int(1000 / fps)
    out[0].save(out_gif, save_all=True, append_images=out[1:], duration=dur,
                loop=0, transparency=trans, disposal=2, optimize=True)
    im2 = Image.open(out_gif)
    print(f"saved {out_gif} — {im2.n_frames} frames, {os.path.getsize(out_gif)//1024}KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("emotion")
    ap.add_argument("pose_delta", help="small, tightly-scoped pose-change description")
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--no-recolor", action="store_true")
    args = ap.parse_args()

    scratch = Path(os.environ.get("SCRATCH", "/tmp")) / f"tween_{args.emotion}"
    scratch.mkdir(parents=True, exist_ok=True)
    key = kie_key()

    src_png = ROOT / f"emoji/512/{args.emotion}.png"
    plate = scratch / "base.png"
    make_base_plate(src_png, plate)
    url = upload(plate)
    print("base plate:", url)

    prompt = (
        f"This image shows a small robot character on a flat solid vivid green screen. Output the "
        f"SAME robot with the EXACT same design, colors, art style, the exact same size, and the "
        f"exact same position and framing. The ONLY difference from the reference is: {args.pose_delta} "
        f"Do not move, rescale, rotate, restyle, or crop the character. Flat solid vivid green "
        f"background, no shadow, no text, no watermark."
    )
    task_file = scratch / "task.json"
    if task_file.exists():
        task_id = json.loads(task_file.read_text())
        print("resuming task", task_id)
    else:
        task_id = create_task(key, prompt, url)
        task_file.write_text(json.dumps(task_id))
    res_url = poll(key, task_id)
    b_raw = scratch / "b_raw.png"
    subprocess.run(["curl", "-s", "-L", "-m", "120",
                    "-A", "Mozilla/5.0 (X11; Linux x86_64)", "-o", str(b_raw), res_url], check=True)

    a_plate = scratch / "a_plate_keyed.png"
    make_base_plate(src_png, a_plate)  # render A onto the SAME canvas construction as B
    a = key_out_green(Image.open(a_plate))
    b = key_out_green(Image.open(b_raw))
    a2, b2 = shared_crop_resize(a, b, args.size)
    if not args.no_recolor:
        b2 = recolor_dark_to_match(a2, b2)

    out_gif = ROOT / f"emoji/gif/{args.emotion}.gif"
    build_tween_gif(a2, b2, out_gif, steps=args.steps)

    contact = scratch / "check.png"
    w, h = a2.size
    sheet = Image.new("RGB", (w * 2, h), (40, 40, 40))
    sheet.paste(a2.convert("RGB"), (0, 0))
    sheet.paste(b2.convert("RGB"), (w, 0))
    sheet.save(contact)
    print("keyframe check:", contact)


if __name__ == "__main__":
    main()
