# Rumi Emoji — Slime Body (v4: rendered body + vector logo-mark face with expressions)

Second character body for the same 54 emotions: a cute translucent slime that can take any shape.
Chosen after the September 2026 team survey (see the Rumi Survey Deck): **the face is locked**
(two eyes, one mouth, nobody wants them changed) and the body direction is **"a cute, slime-like
body that takes any shape"** with the face fixed on whatever the body becomes.

The material, palette and render style are lifted verbatim from
[rumi-style-explorations](https://github.com/oyekamal/rumi-style-explorations) **slime v4**
(v1's colour balance, no drips) — the version Kamal picked over the flat cel-shaded v2 and the
too-dark v3.

## What stays identical to the flat-vector pack

- The 54 emotions and their Slack names (`manifest-slime.json` mirrors `manifest.json`).
- Brand grounding: navy `#001F3F` face, glowing white eyes + smile with pale-blue `#A8C7FF` glow —
  the white-on-navy logo mark. **No orange / coral / gold / red / green on the character.**
- 3×3 grid on pure white, gray labels below each cell, cut by `scripts/split_grids.py`.

## What changed

| | Flat-vector pack | Slime pack |
|---|---|---|
| Body | white egg head + pill body + paddle arms (EVE-like) | one frosted white/pale-blue translucent gel blob, teardrop at rest |
| Face | navy visor, model-drawn eyes+smile | navy rounded face patch with the REAL logo mark composited on (see below) |
| Gestures | paddle arms | gel **pseudopods** stretched out of the body, or the whole body reshaping (heart, lightbulb, slumped, stretched tall) |
| Render | flat vector, Apple-emoji gloss | Pixar-style 3D gel render, soft studio light, no floor/shadow |
| Antenna | glowing tip | tip of the blob glows brighter instead |

## Prompt structure

`prompts/slime.json` holds the exact strings; `scripts/generate_slime.py` assembles each grid as:

```
{opening}

The 9 emotions: {emotions}

{closing}

Avoid: {negative}
```

Keep `opening`, `closing` and `negative` **verbatim** across regenerations — identical wording is
what keeps the character consistent. Only swap the 9 emotion descriptions.

Model: Gemini `nano-banana-pro-preview`, 1:1, 2K. Regenerate one grid with
`python3 scripts/generate_slime.py 3` (delete the existing PNG first; the script skips existing files).

## The face is the logo — pasted, not generated (v3)

v1 let the model draw the face; the eyes and mouth came out as generic emoji features, not the
Rumi mark. v2 tried the logo as a reference image + a "connected dots-and-smile" rule: 5/9 cells
matched on one roll, 0/9 on the next — a coin flip on exactly the detail that is the brand.

So v3 splits the job: the model renders the slime body with an **empty navy face patch**
(`opening_blank` / `closing_blank` / `negative_blank` in `slime.json`, `blank_face: true`), and
`scripts/paste_face.py` composites the **actual logo PNG**
(`rumi-brand/assets/rumi-mark-white-smile.png`) onto the patch: largest navy blob → bbox → mark at
74% of patch width, centred, with a pale-blue `#A8C7FF` blur glow. Any stray features the model
drew inside the patch (it still sneaks hearts in) are blanked to the patch's own navy first.

**Expressions (v4):** `scripts/rumi_face.py` is a vector renderer of the mark. `render("happy")`
reproduces the logo PNG (IoU 0.85 against the real asset — sub-stroke differences only); every other
emotion is the SAME mark with the dots reshaped and/or the connecting curve bent, and the two ends
always stay attached to the eyes. The eye/mouth vocabulary is copied from the flat-vector robot pack
in `grids/` (Kamal: "learn from it and use them"):

- eyes: `dot big small lidded sad angry lookup lookdown lookside closed(^) sleep wink worried squint(><) x heart star spiral`
- mouths: `smile laugh(open D under the curve) smirk flat frown wavy o` — the non-smile ones drop
  straight arms from the dots and carry the expression in the centre segment, so the shape still
  reads as the logo.
- `FACES` maps all 54 names → (left eye, right eye, mouth). Unknown names fall back to neutral.

`python3 scripts/rumi_face.py out.png` prints the IoU and writes a 54-face sheet on navy for review.
Never hand the face back to the image model — edit `FACES` or add a variant in `rumi_face.py`.

## Splitting

```
python3 scripts/generate_slime.py                        # -> grids-slime-blank/ (empty face patches - source only)
python3 scripts/split_grids.py manifest-slime.json emoji-slime
python3 scripts/paste_face.py emoji-slime/512            # logo face onto every emoji; refreshes emoji-slime/128 too
python3 scripts/paste_face.py grids-slime-blank grids-slime --grids   # the viewable grids, with faces
```

`grids-slime-blank/` is raw model output and intentionally faceless - never link it from a README.
`grids-slime/` is what people should look at.

The existing splitter worked unchanged: the pale-blue tinted rim asked for in the prompt is
what stops the white-background flood fill from eating the near-white gel interior. If a future
regeneration loses that rim, the body will vanish — fix the prompt, not the splitter.

**Props must not be white.** First render of grids 5/6 drew whiteboard/trophy/book/tablet in plain
white and the flood fill ate them. Fixed by making props the same pale-blue gel with a navy edge
line (the "Props rule" sentence appended to those grids' emotions). Any new prop needs the same.

Don't widen `BG_SPREAD` to kill the glow fringe: 35 hollowed out `rumi-happy` (rim not sealed).

## Known nits

- Some work-state faces are deliberately subtle (`working`/`loading` = flat mouth) — the floating icon carries them.
- `rumi-idea`, `rumi-charging`: faint jagged outer-glow fringe survives the cut. Visible at 512, not at 128.
- `preview.png` is the 54-emoji contact sheet on gray for quick review.
