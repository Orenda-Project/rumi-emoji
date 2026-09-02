# Rumi Emoji — Slime Body (v1)

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
| Face | navy visor | navy rounded face patch |
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

## Splitting

```
python3 scripts/split_grids.py manifest-slime.json emoji-slime
```

The existing splitter worked unchanged: the pale-blue tinted rim asked for in the prompt is
what stops the white-background flood fill from eating the near-white gel interior. If a future
regeneration loses that rim, the body will vanish — fix the prompt, not the splitter.

**Props must not be white.** First render of grids 5/6 drew whiteboard/trophy/book/tablet in plain
white and the flood fill ate them. Fixed by making props the same pale-blue gel with a navy edge
line (the "Props rule" sentence appended to those grids' emotions). Any new prop needs the same.

Don't widen `BG_SPREAD` to kill the glow fringe: 35 hollowed out `rumi-happy` (rim not sealed).

## Known nits (v1)

- `rumi-wave`: two tiny gel beads under the body (the model's idea of motion) — acceptable at 128px.
- `rumi-idea`, `rumi-charging`: faint jagged outer-glow fringe survives the cut. Visible at 512, not at 128.
- `preview.png` is the 54-emoji contact sheet on gray for quick review.
