# Logo-mark vocabulary

All positions are in mark units (mark width = 1.0, eye row y = 0.103, eye radius 0.095,
eyes at x = 0.10 / 0.90, curve bottom y = 0.372). Helpers: `P(x, y)` maps mark units to
canvas px; `near_right(dx, dy)` is a point dx/dy eye-radii from the right eye.

## Eyes (`--eyes`)

| glyph | draws | use for |
|---|---|---|
| `dot` | the two logo dots (default) | almost everything — Kamal's rule |
| `big` | dots ×1.35 | surprised, shocked, mind-blown, alert, pleading, idea |
| `small` | dots ×0.6 | shy, focus |
| `lid` | dot with top half cut flat | bored, smug, proud, tired, sleepy, annoyed, coffee |
| `lid-sad` / `lid-angry` | lid tilted outward / inward | disappointed·grumpy / furious |
| `arch` | `^` stroke above the eye line | laugh, party, done, yawn (with `closed`) |
| `closed` | `︶` resting arc | yawn, sick, vibing, singing |
| `wink` | left dot + right arch | wink, cheeky |
| `x` | crossed strokes | dead, error |
| `spiral` | Archimedean spiral | dizzy |
| `heart` / `star` | coral heart / navy star | love / starstruck |
| `look` | ring + offset pupil | avoid unless Kamal asks — he prefers dots |
| `ring` | hollow ring | blank stare, sparkle-eyes |

## Mouths (`--mouth`)

| glyph | draws | use for |
|---|---|---|
| `curve` | the connected logo curve (default, `link=True`) | happy/neutral-friendly, wink, blush, proud, done, coffee |
| `flat` | short horizontal stroke | neutral, bored, working, waiting, loading |
| `smile-small` | short disconnected smile | content, shy, curious |
| `open` | filled D, flat top | laugh, shocked, starstruck, party |
| `biggrin` | filled lens between the logo curve and a deeper eye-to-eye arc, no white | lol (Kamal: white tooth bar looked off) |
| `o` | small filled dot | surprised, idea, sleepy |
| `openfrown` | small filled ∩ | worried, furious, pleading |
| `frown` | thin down-curve (`logo_mark_pack.frown`) | sad, disappointed, grumpy, heartbroken; blue for sad |
| `zigzag` | 4-tooth zigzag | confused, nervous |
| `wavy` | sine wave | scared, tired, dizzy, sick |
| `smirk` | short tilted curve | smug, devil |
| `tongue` | open D + coral tongue | cheeky |

## Props (`--prop`) — one per face

| prop | where | meaning |
|---|---|---|
| `sweat` | up-right of right eye, blue drop | nervous, worried, scared |
| `tear` | under left eye | pleading (pack: sad = under right eye, crying = both) |
| `blush` | pink ovals under both eyes | blush, shy |
| `hearts` | two coral hearts up-right | in-love |
| `sparkles` | 4-point stars around | proud, sparkle-eyes |
| `anger` | red 💢 spokes up-right | annoyed, furious |
| `bulb` | outlined bulb + rays | idea |
| `check` | blue ✓ | done |
| `spinner` | arc + arrowhead | loading |
| `hourglass` | ⧗ outline | waiting |
| `glasses` / `shades` | rings on eyes / navy bar | working, reading / cool |
| `halo` / `horns` | ellipse above / red triangles | angel / devil |
| `party` | blue cone hat + coral confetti | party |
| `headphones` | arc + two pads | vibing |
| `coffee` | cup + steam, low right | coffee |
| `music` | ♪ | singing |
| `cloud` | blue rain cloud above centre | heartbroken |
| `burst` | radial ticks around both eyes | mind-blown |
| `thermo` | thermometer with red bulb | sick |
| `mask` | blue rounded rect over mouth | masked |
| `zip` | flat mouth with zipper ticks | zipped |
| `moon` | crescent up-right | tired, sleepy |
| `zzz` | three Z strokes (from the pack) | sleeping |
| `?` `!` `...` | stroke-drawn glyphs, no fonts | confused/curious, alert/error, hmm/speechless |

Pack-only props (in `logo_mark_pack.py`): `prop_tongue`, `prop_santa`, `prop_sparkle`,
`prop_chef`, `prop_tie`, `prop_thought`, `prop_grin`.
