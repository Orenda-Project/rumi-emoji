# Rumi mark — Lottie animations

The Rumi logo itself, animated. Two navy dots joined by one smile curve, 12 expressions from
"The World of Rumi" sheet, each a 1-second loop at 30fps. Vector, so they scale to any size and
recolour by editing a number.

Open `preview.html` in a browser to see all 12 playing (uses lottie-web from cdnjs).

| File | Motion |
|---|---|
| `rumi-happy.json` | gentle breathe, smile widens |
| `rumi-tongue.json` | tongue pops out and wiggles |
| `rumi-santa.json` | Santa hat bobs on the right dot |
| `rumi-wink.json` | right dot closes to a dash, sparkle lines flash |
| `rumi-sad.json` | frown, one tear falls from the right dot |
| `rumi-angry.json` | dark red mark, slanted brows, whole face shakes |
| `rumi-chef.json` | chef hat on the left dot, whisk stirs |
| `rumi-tie.json` | collar + necktie swing, dots blink |
| `rumi-crying.json` | frown, tears stream from both dots |
| `rumi-thinking.json` | thought bubble, dots pop in one by one |
| `rumi-sleeping.json` | half-closed dots, zZZ float up and fade |
| `rumi-laugh.json` | big open mouth bounces |

## How they're built

`scripts/make_lottie.py` draws every frame as an SVG from one parameterised `mark()` function
(dot positions, radius, stroke, navy `#001240` sampled from the brand PNG), then converts the 30
frames into one Lottie via the asset-studio `svg_to_lottie.py` flipbook converter. No After Effects.

```bash
python3 scripts/make_lottie.py            # all 12 -> lottie/*.json + preview.html + contact-sheet.png
python3 scripts/make_lottie.py wink laugh # just some
```

Add an expression: write one `def name(i)` returning SVG for frame `i` of 30, register it in
`EMOTIONS`, rerun. Keep the two dots and the curve as the anchor; props go around them.

## Using them

- **Web:** `lottie.loadAnimation({container, renderer:'svg', loop:true, autoplay:true, path:'rumi-wink.json'})`
- **Flutter:** `Lottie.asset('assets/lottie/rumi-happy.json')`
- **LottieFiles / After Effects:** import the JSON directly.
- **Recolour:** colours are stored as `[r,g,b]` floats. Navy `#001240` = `[0, 0.071, 0.251]`; search `0.071,0.251` and replace.

## Known limits

- Flipbook files are 50–130KB each (30 layers). Fine for web/app. If size matters, drop `N` to 15 in the script.
- Renders were checked with python-lottie and lottie-web; dotLottie/`.lottie` zip not generated.
