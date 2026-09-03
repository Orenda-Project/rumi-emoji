# Rumi mark — Lottie animations

The Rumi logo itself, animated. Two navy dots joined by one smile curve, 12 expressions from
"The World of Rumi" sheet. **v2 (2026-09-03): real keyframes and easing**, 3-second loops structured
idle → anticipation → action → settle → rest, 3–7 KB each. Vector, so they scale to any size and recolour by editing a number.

Open `preview.html` in a browser to see all 12 playing (uses lottie-web from cdnjs).

| File | Motion |
|---|---|
| `rumi-happy.json` | breathes (1 cycle/3 s), blinks at 0.9 s, smile widens 14% at 1.9 s and settles |
| `rumi-tongue.json` | smile squeezes (anticipation), tongue pops from behind the curve with overshoot, wiggles, retracts |
| `rumi-santa.json` | hat nods twice with a spring, pivot at the brim on the dot |
| `rumi-wink.json` | eye widens 10% first, closes to a wide dash for 400 ms, sparkle pops 112→100%, smile widens 60 ms later |
| `rumi-sad.json` | frown held; tear forms over 500 ms, hangs, then falls in 600 ms |
| `rumi-angry.json` | brows press down, 12 decaying 50 ms shakes, settle |
| `rumi-chef.json` | whisk stirs 3 strokes, each with 10% overshoot; hat tilts with the breath |
| `rumi-tie.json` | pendulum swing lagging the breath by 100 ms (follow-through); blink |
| `rumi-crying.json` | sob bob every 400 ms; 4 tears staggered 500 ms |
| `rumi-thinking.json` | eyes drift up-right, mouth flattens, 3 bubble parts pop in 150 ms apart, then pop out |
| `rumi-sleeping.json` | eyes are bowls (dot clipped flat, like the Slack avatar), slow deep breath, 3 zZZ rise and fade |
| `rumi-laugh.json` | mouth opens in 150 ms into a hollow laugh, 3 ha-ha bounces, hold, close |

## How they're built

`scripts/rumi_rig.py` is a small rig on python-lottie: two dot ellipses, one mouth path (two vertices, so it
morphs smile ↔ frown), Material easing curves, a `blink()`, an `overshoot()` spring helper, and prop helpers.
`scripts/make_lottie_v2.py` has one function per expression writing keyframes in milliseconds. No After Effects,
no flipbook: each file is a handful of shapes with real keyframes, which is why they are 3–7 KB.

```bash
python3 scripts/make_lottie_v2.py            # all 12 -> lottie/rumi-*.json
python3 scripts/make_lottie_v2.py wink laugh # just some
```

Timing rules the set follows (from the research in `personal-agent-v2/.claude/skills/lottie-motion/`):
loops 3 s with ≥40% rest; blink 100/50/100 ms; mouth morphs 200–300 ms; anticipation 10–15% opposite;
overshoot 5–10% then settle; secondary action lags 50–100 ms. Lottie z-order gotcha: the first shape in a
list draws on top, so "behind" means `add_shape`, "on top" means `insert(0, …)`.

Add an expression: copy one function, keep the two dots and the curve as the anchor, put props in their own
group with the anchor at the pivot, register it in `EMOTIONS`, rerun, then check `contact-sheet.png`.

`scripts/make_lottie.py` is the old v1 flipbook generator, kept for reference.

## Using them

- **Web:** `lottie.loadAnimation({container, renderer:'svg', loop:true, autoplay:true, path:'rumi-wink.json'})`
- **Flutter:** `Lottie.asset('assets/lottie/rumi-happy.json')`
- **LottieFiles / After Effects:** import the JSON directly.
- **Recolour:** colours are stored as `[r,g,b]` floats. Navy `#001F3F` = `[0, 0.122, 0.247]`; search `0.122,0.247` and replace.

## Known limits

- Checked in python-lottie's renderer and in lottie-web (frozen frames + live preview); dotLottie/`.lottie` zip not generated.
- Telegram TGS would additionally need 60 fps and gzip; these are 30 fps JSON.
