---
name: rumi-face
description: Compose ANY facial expression for Rumi (the slime/blob character and the logo mark) from a fixed vocabulary of eye and mouth glyphs, render it as glowing white vectors, and composite it onto a body render or export it standalone. Use this whenever someone wants Rumi to "look" a certain way - happy, sad, sleepy, mind-blown, sarcastic, a new emoji, a reaction sticker, an avatar state for the app/portal/voice device, a face for a Slack message or a lesson-plan image. Trigger on "rumi face", "rumi expression", "make rumi look X", "rumi emoji", "eyes and mouth", "add an expression", "new sticker", "rumi avatar state", "what face should rumi make", even if the word "face" isn't used. Never let an image model draw Rumi's eyes and mouth - use this skill's renderer so the face always matches the logo language.
---

# Rumi Face

Rumi's identity is the logo mark: **two glowing white dots joined by one smile curve on navy `#001F3F`**
(Sept-2026 team survey: "Keep the face. Two eyes, one mouth. Nobody wants them changed."). Every
expression Rumi makes is a variation of that mark drawn in the same language - small, thin, glowing,
kawaii-calm - while the **body** does the acting. This skill is the single way to produce those faces.

## Why a renderer and not a prompt

Image models redraw the mark into generic emoji eyes on every roll (measured: the connected mark came
out 5/9 cells on one try, 0/9 on the next). So the pipeline splits the job: the model renders the body
with an **empty navy face patch**, and `scripts/rumi_face.py` draws the face as vectors on top. The face
is deterministic, brand-exact, and a one-line edit to change.

## The grammar

`Face = (left eye, right eye, mouth, link)`

| Eyes (each side independent) | Mouths |
|---|---|
| `dot` `dot:s` `dot:l` - the logo dot, small / large | `smile:s` `smile:m` `smile:l` - the logo curve, disconnected |
| `arch` ^ happy-closed | `open:s` `open:l` - filled D, laughing / talking |
| `squint` `> <` laughing hard | `frown` |
| `closed` ︶ sleeping | `flat` - deadpan / working |
| `wink` (one side) | `zigzag` - nervous / confused |
| `lidded` half-closed: smug, proud, tired | `o` - small filled dot: surprised, dizzy |
| `lid:sad` `lid:angry` slanted lids | `openfrown` - small filled ∩: worried, pleading |
| `dome` flat-top half dome + worried brow | `smirk` |
| `x` knocked out / error | |
| `spiral` dizzy | |
| `heart` `star` | |
| `look:up` `look:down` `look:side` ring + pupil | |

`link=True` draws the logo's exact connecting curve between the eyes instead of a separate mouth.
**Use it for the resting face (`happy`) - that is the brand mark and must not drift** - and wherever it
reads better (`heart-eyes`, `shy`). Everything else is disconnected; that is how the approved reference
renders look (`references/faces/`).

## Proportions (already baked into the renderer - don't fight them)

Eye radius ≈ 6-7% of the face-patch width, stroke ≈ 2.5%, eyes ≈ 50% of patch width apart, mouth ≈ 13%
below the eye line, generous navy around everything. If a face looks "too small", the answer is
almost never a bigger face - it is a more expressive body.

## Design rules

1. **Face calm, body loud.** Rumi is cute, calm, relaxed, friendly. Anger is dots + a small frown on the
   face and a 💢 mark + puffed body outside it; nervousness is a zigzag mouth and sweat drops + shake
   lines on the body. Put symbols (checkmarks, spinners, hearts, sparks) *beside* the body, never on
   the patch.
2. **White + pale-blue glow only** (`#FFFFFF` on `#001F3F`, glow `#A8C7FF`). No coral, gold, red,
   green - those are UI/deck accents, never on the character.
3. **Pick from the vocabulary before inventing a glyph.** 54 emotions are already covered by 16 eye and
   8 mouth glyphs. If a new one is truly needed, add it to `_eye`/`_mouth` in `scripts/rumi_face.py`
   in the same thin-stroke style, and add a row to `references/vocabulary.md`.
4. **Same face, different body = different emoji.** `clap`, `encourage`, `trophy` all use
   `arch/arch/open:s`; the pseudopods and props tell them apart. Don't over-differentiate faces.

## How to use

**A face for an existing name** (54 names in `FACES`, e.g. `rumi-sleeping`):
```bash
python3 scripts/rumi_face.py sheet.png            # 54-face sheet on navy + IoU of `happy` vs the real logo
python3 -c "import sys; sys.path.insert(0,'scripts'); import rumi_face; rumi_face.render('sleeping', 600).save('face.png')"
```

**A brand-new expression** - compose it, then either export it or put it on a body:
```bash
python3 scripts/face_cli.py --left lidded --right wink --mouth smirk --out sarcastic.png
python3 scripts/face_cli.py --left dot:l --right dot:l --mouth o --on-body body.png --out surprised-on-body.png
```
`--on-body` expects a render with an **empty navy face patch** (see "Getting a body" below); it finds
the patch, wipes anything drawn inside it, and composites the face with the glow.

**Whole emoji pack** (in `Orenda-Project/rumi-emoji`): `generate_slime.py` → `split_grids.py` →
`paste_face.py emoji-slime/512` → `paste_face.py grids-slime-blank grids-slime --grids`. The `FACES`
table in `rumi_face.py` maps every emoji name to its face.

## Getting a body

Bodies come from Gemini `nano-banana-pro-preview` in **blank-face mode** - the prompt asks for "a
smooth, completely EMPTY deep navy face patch (a plain dark oval, like a switched-off screen)" and
describes only body language, props and floating symbols. Use `prompts/slime.json` in the rumi-emoji
repo as the template (`opening_blank` / `closing_blank` / `negative_blank`); keep those three verbatim
and write only the body description. Props must be pale-blue gel with a navy edge (plain white props
vanish in the background flood-fill). Key from `GEMINI_API_KEY`.

## Files

- `scripts/rumi_face.py` - the renderer + `FACES` table (canonical copy lives in rumi-emoji; keep in sync)
- `scripts/face_cli.py` - compose / export / composite CLI
- `references/vocabulary.md` - every glyph with its meaning and the reference it came from
- `references/vocabulary-sheet.png` - all 54 faces rendered on navy
- `references/faces/` - the 17 approved reference renders (ground truth for style and proportions)
