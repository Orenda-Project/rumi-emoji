---
name: rumi-logo-mark-emoji
description: Make "World of Rumi" emoji and stickers where the emoji IS the Rumi logo mark — two navy dots joined by the smile curve, no body, one small prop hanging off the mark, navy on transparent for cream/white Slack and WhatsApp backgrounds. Pure PIL vector renderer, no image model. Use this whenever Kamal asks for logo-mark emoji, "World of Rumi" stickers, a new Rumi mark expression (e.g. "rumi mark with a graduation cap", "add a facepalm to the mark pack"), a themed set (Eid, Christmas, exam season) in the mark style, or says "same style as the dots-and-smile emoji". Also use it to fix or re-render the existing packs (edge clipping, wrong eyes). Do NOT use for the slime/robot body packs or any face composited onto a body — that is `rumi-face`.
---

# Rumi Logo-Mark Emoji

The Rumi logo is two dots and a smile curve. Kamal's "World of Rumi" sheet
(`references/world-of-rumi-logo-mark-2026-09-03.jpg`) turned the mark itself into emoji:
the dots are the eyes, the curve is the mouth, and a hat / tear / tie / tongue hangs off it.
No body, no face patch. This skill is the one way to make more of them so they stay
consistent with the 70 already shipped (`references/preview-mark.png`,
`references/preview-mark-emotions.png`).

Canonical copies of the renderers live in `Orenda-Project/rumi-emoji` (`~/Documents/rumi-emoji/scripts/`).
The copies here are for use anywhere; if you change one, copy it to the other.

## The grammar

`Emoji = eyes + mouth + (at most one prop)`

- **Eyes default to the two logo dots.** Kamal explicitly rejected pupil/ring eyes on
  waiting, suspicious, hmm and curious: "eyes should be dot". Change the eyes only when
  the emotion is *about* the eyes — half-lid (bored, smug, sleepy), arch `^` (laughing),
  `x` (dead), spiral (dizzy), big dots (surprised), heart/star (love, starstruck).
- **The connected logo curve is the default happy mouth.** Keep it whenever the mood is
  positive or neutral-friendly; it is the brand. Disconnect only for frown, flat, open,
  zigzag, wavy. For a big laugh the curve stays and the open mouth hangs *below* its
  bottom (Kamal: "lol mouth should be connected to both eyes").
- **One prop, off to a side, never covering the mark.** Props sit up-right of the right
  eye (sparkle, ?, !, bulb, spinner), under an eye (tear), on top of an eye (santa, chef,
  party hat), or hanging from the curve centre (tie, tongue). Two props is already busy.
- **Colours:** navy `#0B2545` for everything on the mark; pale-blue `#2F6BB3` for tears,
  clouds, checks, masks; dark red `#7A1F1F` for anger only; coral `#E8746A` for tongue and
  hearts; pink `#F3A6B8` blush. These are Kamal-approved exceptions to the usual
  "no coral/red on Rumi" rule *for this style only*.
- **Simple and minimalistic.** If a prop needs more than ~6 primitives it is too detailed
  for 128 px. Reduce it or pick a different prop.

## Producing emoji

```bash
cd <where the output folders should land>        # e.g. ~/Documents/rumi-emoji
S=~/.claude/skills/rumi-logo-mark-emoji/scripts

python3 $S/mark_cli.py list                                      # 12 pack + 58 emotion names
python3 $S/mark_cli.py render lol --out lol.png --bg             # one existing emoji (--bg = cream preview)
python3 $S/mark_cli.py compose --eyes dot --mouth curve --prop check --out ok.png --bg
python3 $S/mark_cli.py compose --eyes lid --mouth flat --prop coffee --out monday.png
python3 $S/logo_mark_pack.py        # regenerate the 12 reference variants -> ./emoji-mark/{512,128} + preview-mark.png
python3 $S/logo_mark_emotions.py    # regenerate the 58 emotions -> ./emoji-mark-emotions/{512,128} + preview
python3 $S/mark_cli.py check emoji-mark-emotions/512             # exit 1 if any file touches the canvas edge
```

Set `RUMI_MARK_OUT=/some/dir` to redirect a whole-pack render.

**Adding a permanent emotion:** add one line to `EMOTIONS` in `logo_mark_emotions.py`
using `face(eyes, mouth, prop, link=)`; write a new `p_<prop>` only if none of the ~30
existing props fits. **Adding a themed set** (Eid, exams, cricket): make a sibling
script that imports the primitives from `logo_mark_pack` / `logo_mark_emotions` the way
`logo_mark_emotions.py` does, so the geometry cannot drift.

## Before showing Kamal

1. Run `mark_cli.py check` on the output folder. Eight of the first 70 were edge-clipped
   because a prop went past 512 px; Kamal caught it by eye. The check catches it first.
   Fix by moving the prop inward, not by shrinking the mark further (mark width is
   already tuned to 330/512 so hats and bubbles fit).
2. Render the preview sheet on cream and look at it at sheet scale. A prop that reads
   fine at 512 px can turn to mush at 128 px (the coffee cup did).
3. Post the sheet, not individual files. Kamal reviews whole sheets and names the cells
   to change ("waiting, suspicious, hmm, curious eyes should be dot").

## Files

- `scripts/logo_mark_pack.py` — geometry constants (logo-measured), primitives (`P`, `stroke`,
  `dot`, `logo_curve`, `frown`, `tear`, `eyes`, `mark`), the 12 reference variants.
- `scripts/logo_mark_emotions.py` — eye/mouth/prop glyph library + the 58-emotion table.
- `scripts/mark_cli.py` — list / render / compose / edge-check without editing tables.
- `references/vocabulary.md` — every glyph and prop with what it means and when to use it.
- `references/world-of-rumi-logo-mark-2026-09-03.jpg` — Kamal's original 12-cell sheet, ground truth.
- `references/preview-mark.png`, `references/preview-mark-emotions.png` — shipped sheets.

Related: `rumi-face` (faces on a slime/robot body), `rumi-brand` (palette and logo files),
`veo-gif-creator` / `lottie-motion` if a mark emoji needs to animate.
