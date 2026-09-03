# Rumi Emoji — Generation Prompts

All 6 grids were generated with the same character block and negative prompt, in **flat vector**
style. To regenerate a grid (or add a new one), reuse the character paragraph and negative prompt
verbatim — identical wording is what keeps the character consistent across generations.

Generated 2026-08-25, 2048x2048 ("2K"), one 3x3 grid per prompt.

## Brand grounding (verified against source)

- Body: white. Visor + outlines: navy `#001F3F` (the logo navy; product primary is `hsl(225 73% 20%)` ≈ `#0E2058`).
- Face features (eyes + smile): glowing white with pale-blue `#A8C7FF` glow — matches the
  white-on-navy logo mark (two dots connected by a smile). Sampled from
  `rumi-brand/assets/rumi-mark-navy-transparent.png` (`#001240`) and `rumi-mark-white-smile.png` (`#FFFFFF`).
- Coral `#F06E42` is a product **UI** accent only, gold `#F5B301` is deck-only — **neither appears on the character**.
- No orange, coral, gold, red, green anywhere on the character.

## Shared character paragraph (opens every prompt)

> A single 3×3 grid image on a plain pure white background (#FFFFFF), showing 9 flat vector emoji
> designs (Apple/iOS emoji style, soft gradients, subtle gloss) of the SAME character, one per cell,
> each cell labeled in small gray text. No cell borders, no background tints, no shadows on the
> background. The character: "Rumi", a friendly desk-companion robot — glossy WHITE egg-shaped head
> nearly as wide as its shoulders (like EVE from WALL-E), a deep navy blue #001F3F visor face, and on
> the visor two round glowing WHITE eyes with a soft pale-blue #A8C7FF glow and a glowing white smile
> curve. Short white pill-shaped body, small white paddle arms, navy #001F3F outlines. Strict
> palette: white body, navy visor/outlines, glowing white-blue face features. No other colors.

## Shared closing line (ends every prompt)

> Every cell keeps the same identity: white egg head, navy visor, glowing white face. Friendly, warm,
> Apple-like restraint, high resolution, evenly spaced grid.

## Shared negative prompt

```
orange, coral, gold, yellow, red, warm accent colors, navy body, dark body, colored background,
gradient background, cell borders, green, purple, realistic human, watermark, hand-drawn sketch
style, pixel art, line art only
```

---

## Grid 1 — Core Reactions (`grids/grid-1-core-reactions.jpeg`)

The 9 emotions: 1) Happy — default warm smile. 2) Wink — one eye closed as a curved line, playful
smile. 3) Wave — one paddle arm raised waving, happy face. 4) Thumbs Up — one arm giving a thumbs
up, confident smile. 5) Heart Eyes — both eyes as glowing white hearts. 6) Laugh — eyes as tight
squint curves, big open glowing smile. 7) Thinking — one paddle arm on chin, eyes looking up,
antenna tip glowing bright. 8) Sad — downturned glowing mouth, slightly dimmed drooping eyes.
9) Celebrate — both arms raised high, joyful open smile, small white and navy confetti dots around
the head.

## Grid 2 — Agent Work States (`grids/grid-2-work-states.jpeg`)

The 9 emotions: 1) OK Done — a large glowing white checkmark displayed on the visor instead of eyes,
satisfied smile below it. 2) Working — the visor shows three glowing typing dots "···" and a small
progress bar, focused expression. 3) Loading — a glowing circular spinner icon on the visor.
4) Searching — holding a white magnifying glass up to the visor, one eye enlarged behind the lens.
5) Idea — antenna bulb glowing extra bright with rays, wide excited eyes, open smile. 6) Writing —
holding a white pencil, looking down concentrating. 7) Error — visor showing glitch static lines,
eyes as small x x crosses, flat worried mouth. 8) Warning — a glowing white exclamation mark "!" on
the visor, concerned raised-brow eyes. 9) Blocked — both paddle arms crossed over the chest, flat
straight mouth, half-lidded eyes.

## Grid 3 — Rest & Big Feelings (`grids/grid-3-big-feelings.jpeg`)

The 9 emotions: 1) Sleeping — eyes as closed downward curves, three glowing "z Z z" letters floating
above the head. 2) Low Battery — a nearly-empty battery icon glowing on the visor, tired droopy
eyes. 3) Surprised — very large round glowing eyes, small round "o" mouth. 4) Confused — one eye big
and one small, wavy squiggle mouth, a glowing white question mark floating overhead. 5) Shy — eyes
looking away to the side, soft pale-blue blush glow patches on the visor cheeks, tiny bashful smile.
6) Crying — glowing white teardrops falling from both eyes, downturned mouth. 7) Crying Laughing —
tight squint eyes, huge open smile, one glowing tear flying off each side. 8) Angry — eyes angled
down toward center as narrow slits, visor slightly dimmed darker, small frown — mild and cute, not
menacing. 9) Nervous — wobbly uneven smile, one large white sweat drop beside the head, eyes
slightly askew.

## Grid 4 — Attitude & Personality (`grids/grid-4-attitude.jpeg`)

The 9 emotions: 1) Smug — half-lidded eyes, confident side smirk. 2) Mind Blown — eyes as glowing
spiral swirls, open mouth, small white starburst above the head. 3) Eye Roll — both glowing pupils
rolled up to the top of the eyes, flat unimpressed mouth. 4) Facepalm — one paddle arm covering half
the visor, visible eye closed in exasperation. 5) Cool — white pixel-style sunglasses displayed
across the visor, relaxed smile. 6) Starstruck — both eyes as glowing white four-pointed stars,
amazed open smile. 7) Salute — one paddle arm raised in a crisp salute to the head, determined
smile. 8) Shrug — both paddle arms raised outward palms-up in a shrug, wavy neutral mouth. 9) Peek —
only the top half of the character visible rising from the bottom edge of the cell, wide curious
eyes peeking.

## Grid 5 — Teaching & Encouragement (`grids/grid-5-teaching.jpeg`)

The 9 emotions: 1) Teaching — standing beside a small white whiteboard, one paddle arm pointing at
it, encouraging smile. 2) Graduate — wearing a navy graduation cap with a white tassel, proud smile.
3) Clap — both paddle arms mid-clap with small white motion lines, delighted face. 4) Encourage —
both arms up cheering, big supportive smile, small glowing white sparkles around. 5) Listening — a
glowing white soundwave pattern displayed on the visor, attentive tilted head. 6) Speaking — glowing
white soundwave curves radiating from the smile, bright eyes. 7) Hundred — a glowing white "100"
displayed on the visor, thrilled smile below. 8) Trophy — holding up a small white trophy with navy
outline, beaming. 9) Book — looking down at an open white book held in both arms, gentle focused
smile.

## Grid 6 — Fun Extras (`grids/grid-6-fun-extras.jpeg`)

The 9 emotions: 1) Thanks — both paddle arms pressed together in a grateful gesture, warm closed-eye
smile. 2) Dance — body tilted, both arms out at angles, joyful face, small white motion arcs.
3) Heart — holding a large glowing white heart in both arms, tender smile. 4) Reading — eyes looking
down, absorbed in a small white tablet held in front. 5) Charging — a lightning-bolt charging icon
glowing on the visor, content recharging smile. 6) Hello — both arms open wide in welcome, biggest
warm smile. 7) Curious — head tilted, one eye slightly bigger, small "?" glow on the visor edge.
8) Proud — chest out, hands on hips (paddle arms bent to sides), satisfied glowing grin. 9) High
Five — one paddle arm raised flat forward for a high five, excited face.

---

## Backlog (listed but not yet generated)

Other styles from the style-selection round: **pixel art 32px** and **duotone flat** — regenerate
any grid above swapping the style phrase in the character paragraph. Emotions listed in the original
emotion set but not in any grid yet: none (all 54 cells cover the working set; `rumi-check` merged
into `rumi-done`, `rumi-pray` merged into `rumi-thanks`).
