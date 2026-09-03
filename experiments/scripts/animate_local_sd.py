#!/usr/bin/env python3
"""Fully-local GIF frames: SD1.5 + ControlNet(canny) + IP-Adapter on 4GB VRAM.

Motion comes from the parametric vector Rumi (rumi_vector.py) rendered per
frame and turned into canny edges; identity/style comes from the original
emoji PNG via IP-Adapter. img2img-free, every frame same seed => stable look.
"""
import io, math, sys, os
import numpy as np, cv2, torch
from torch.nn.attention import sdpa_kernel, SDPBackend
from pathlib import Path
from PIL import Image
import cairosvg

sys.path.insert(0, str(Path(__file__).parent))
from rumi_vector import rumi_svg

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path(os.environ.get("SCRATCH", "/tmp")) / "local_sd"
SCRATCH.mkdir(parents=True, exist_ok=True)

from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler, AutoencoderKL

def control_image(wave_angle, bob, size=384):
    png = cairosvg.svg2png(bytestring=rumi_svg(wave_angle=wave_angle, bob=bob).encode(),
                           output_width=size, output_height=size, background_color='white')
    arr = np.array(Image.open(io.BytesIO(png)).convert('RGB'))
    edges = cv2.Canny(arr, 80, 160)
    return Image.fromarray(np.stack([edges]*3, axis=-1))

def main():
    cn = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_canny",
                                         torch_dtype=torch.float32)
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5", controlnet=cn,
        torch_dtype=torch.float32, safety_checker=None)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin")
    pipe.set_ip_adapter_scale(0.85)
    pipe.to("cpu")

    ref = Image.open(ROOT / "emoji/512/rumi-wave.png").convert("RGB")

    prompt = ("cute white robot mascot emoji, glossy white egg head, dark navy visor with "
              "glowing happy eyes and smile, flat vector sticker style, thick navy outline, "
              "clean solid white background, high quality")
    neg = "photo, realistic, 3d render, text, watermark, extra limbs, blurry, gradient background"

    N = 6
    gen = torch.Generator("cpu").manual_seed(7)
    for i in range(N):
        t = i / N
        ang = -128 + 30 * math.sin(t * 2 * math.pi)
        bob = 2.5 * math.sin(t * 2 * math.pi)
        ctrl = control_image(ang, bob)
        img = pipe(prompt, negative_prompt=neg, image=ctrl, ip_adapter_image=ref,
                   num_inference_steps=22, guidance_scale=7.0,
                   controlnet_conditioning_scale=0.9, generator=gen).images[0]
        img.save(SCRATCH / f"sd_{i:02d}.png")
        ctrl.save(SCRATCH / f"ctrl_{i:02d}.png")
        print("frame", i, "done", flush=True)

if __name__ == "__main__":
    main()
