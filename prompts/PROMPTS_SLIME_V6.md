# Slime pack v6 — expressive bodies (2026-09-02)

Generated with Gemini `nano-banana-pro-preview`, 2K, 1:1, one 3x3 grid per call, no reference image, face drawn by the model.

`python3 scripts/generate_slime.py --prompts prompts/slime_v6.json [1..6]` then `BG_MIN=244 python3 scripts/split_grids.py manifest-slime-v6.json emoji-slime-v6` (grey-bodied cells: add `LABEL_BAND=0`).

## Why v6 works where v5 didn't

- v5 banned every colour, drip, puddle, arm and hand, then pasted a fixed vector face. Result: one body 54 times.
- v6 uses Kamal's own working Gemini prompt as the opening and gives EVERY cell an explicit body material + colour + silhouette. Cells without a named material fall back to the same pale-blue dome - the model only transforms what you name.
- Hard rules in the closing: no two cells share body colour/material/silhouette; resting dome at most once per grid; navy faceplate kept in every cell (without this, coloured bodies lose the plate).

## Opening (shared)

A high-resolution 3D emoji collection presented in a clean 3x3 grid, showcasing nine distinct emotional expressions of translucent jelly-like blobs. Each character is glossy and semi-transparent, featuring vibrant internal plasma effects and glowing light trails. All blobs share a signature dark oval faceplate set into the jelly, with glowing white dot eyes and mouth lines. The aesthetic is clean and polished with a soft vector-3D render hybrid feel, set against an isolated, plain white background.

## Closing (shared)

Same character in every cell: at rest it is a frosted white / pale-blue (#A8C7FF glow) slime dome with a deep navy (#001F3F) oval faceplate. The FACE stays small and subtle - tiny glowing white dot eyes and one thin mouth line, plus thin white eyebrow lines only when the emotion needs them; the calm/happy face is two dots joined by one smile curve. The BODY does the acting: change its material, colour, texture, silhouette and posture to match the emotion, grow soft gel pseudopod arms only when a gesture is needed, put props and things INSIDE the translucent jelly, and use floating symbols and thought bubbles that carry real content. Cells in row-major order, evenly spaced, each character fully inside its own cell with generous white space around it, no cell borders, no labels, no floor, no shadow on the background. HARD RULE - EVERY CELL IS A DIFFERENT CREATURE STATE: no two cells in the grid may share the same body colour, material, or silhouette. Each cell must read as a unique mini-scene even with the face covered - change what the jelly is MADE OF (lava, stone, gold glitter, galaxy, rain cloud, ice, rainbow plasma, glass, moss, pastel cloud), what COLOUR it is, what SHAPE it takes (sphere, heart, puddle, flame, tall stretch, flat slump, split copies), and what is INSIDE it. The plain pale-blue resting dome may appear in at most ONE cell per grid. Props and thought bubbles must contain specific things, never generic sparkles alone. NON-NEGOTIABLE: every single cell keeps the deep navy (#001F3F) oval faceplate set into the jelly, with the small glowing white features drawn ON that navy oval - never draw eyes or mouth directly on the coloured body, no matter what colour or material the body becomes.

## Per-grid emotions

### core reactions — `grids-slime-v6/grid-1-core-reactions.png`

1) HAPPY: the ONE resting form - calm frosted pale-blue dome, two dot eyes joined by one glowing smile curve, soft even inner glow, a glossy pale-blue checkmark floating above.
2) WINK: body turned to shimmering iridescent mother-of-pearl gel, leaning hard to one side on one stretched foot, one dot eye and one closed arc, cheeky grin, a wink-star flying off.
3) WAVE: body stretched tall and thin like a wobbling pillar of clear sky-blue water, one long arm arcing high in a wave with three ripples, dot eyes, wide smile, droplets flying.
4) THUMBS-UP: body squat and wide, tinted fresh mint-green gel with a glowing green ring inside, one big chunky gel thumbs-up filling the side of the cell, dot eyes, wide smile.
5) HEART-EYES: body reshaped into a glossy translucent pink-red heart with a beating pink glow inside, two pink heart eyes, tiny open mouth, a thought bubble of small hearts.
6) LAUGH: body squashed wide and rolled onto its back, coloured warm honey-yellow, kicking two gel legs in the air, closed arc eyes, huge open grin, sparks of joy.
7) THINKING: body tall and narrowed, slate-blue frosted glass with slowly turning gears visible INSIDE the jelly, one gel hand on chin, one raised eyebrow, flat mouth, thought bubble with a glowing gear and a question mark.
8) SAD: body melted into a low grey-blue puddle with a little rain cloud drizzling INSIDE the jelly, dot eyes, thin frown, one teardrop, hands pressed flat at the sides.
9) CELEBRATE: body burst into a tall party-popper shape with rainbow confetti and streamers suspended INSIDE the jelly and exploding out, arms up, closed arc eyes, huge open grin.

### agent work states — `grids-slime-v6/grid-2-work-states.png`

1) DONE: body turned to polished green jade-like glass, standing straight and proud with a gel hand on hip, dot eyes, satisfied smile, a big glossy green checkmark growing out of the top.
2) WORKING: body coloured warm amber like a glowing worklight, wearing a pale-blue hardhat, bent forward over a glowing translucent keyboard with both arms typing, dot eyes, tiny flat mouth, motion lines.
3) LOADING: body reshaped into a round hourglass-like double bulb with pale-blue sand trickling INSIDE it, a glowing loading ring circling the head, dot eyes looking up, small o mouth.
4) SEARCHING: body stretched long and low like a sniffing hound, tinted clear with glowing yellow search-beam light INSIDE, one eye huge through a magnifying glass, other eye squinting, a glowing blueprint nearby.
5) IDEA: body swelled into a perfect round bulb-sphere swirling with rainbow plasma, a real glowing lightbulb growing out of the top with a small '!' inside it, one eyebrow raised, excited grin.
6) WRITING: body coloured soft lavender, hunched over a glowing tablet held in one arm, a glowing stylus in the other, ink-like purple swirls INSIDE the jelly, dot eyes, tongue slightly out.
7) ERROR: body glitching into two offset red and cyan ghost copies with pixel blocks flaking off, cracked and jittering, wide worried eyes, wavy mouth, a floating red exclamation triangle.
8) WARNING: body coloured amber-yellow with black-and-yellow hazard stripes faintly INSIDE the jelly, flickering, one eyebrow up, tight flat mouth, a glossy yellow exclamation triangle above.
9) BLOCKED: body pressed flat and squashed against an invisible wall so the front is flattened, tinted cold steel-grey, one gel hand splayed on the wall, both eyebrows down, frown, a glowing red no-entry circle behind.

### rest and big feelings — `grids-slime-v6/grid-3-big-feelings.png`

1) SLEEPING: body resting on a soft pastel cloud, two closed downward-arc eyes, small o mouth snoring, a thought bubble with two fluffy sheep, floating Zs.
2) LOW-BATTERY: body dim and slumped low, colour drained to pale grey, half-lidded eyes, flat mouth, a red empty battery icon floating above, tiny power-cord tail trailing.
3) SURPRISED: body stretched tall with arms out, two BIG round white eyes, small round o mouth, a few pale-blue exclamation sparks.
4) CONFUSED: body wobbling with a jelly shake, dot eyes, wavy squiggle mouth, many small glowing question marks orbiting, one gel hand scratching the top.
5) SHY: body shrinking small and rosy-pink tinted, eyes as tiny happy arcs, tiny smile, two gel hands covering the lower face, small hearts and blush.
6) CRYING: body turning grey-blue and melting downward with rain clouds and rain streaks INSIDE the jelly, dot eyes, frown, two rivers of tears streaming from both eyes down the body.
7) CRYING-LAUGHING: body doubled over, eyes closed arcs, huge open grin, big tears flying off both sides, arms clutching the middle.
8) ANGRY: body turned to cracked red-hot lava gel with black smoke plumes and small lightning bolts, faceplate glowing red, dot eyes with steep inward-slanted eyebrows, small frown, two red fists.
9) NERVOUS: body trembling with visible shake lines, sweat drops sliding off, wide dot eyes, wavy mouth, gel hands wringing together, faint pale-green tint.

### attitude and personality — `grids-slime-v6/grid-4-attitude.png`

1) SMUG: navy faceplate kept; body coloured deep royal-purple velvet gel, leaning back with one gel hand on hip and one polishing an invisible nail, half-lidded eyes, one eyebrow raised, lopsided smirk, a single sparkle.
2) MIND-BLOWN: the top of the head blown open into a swirling galaxy of stars and planets pouring out, body dark cosmic navy sparkling with stars, two spiral eyes, small open mouth.
3) EYE-ROLL: navy faceplate kept; body slumped and coloured dull beige-grey like cooled porridge, arms folded, both eyes rolled up as half-moon lids, flat mouth, a tiny grey thought bubble with an ellipsis.
4) FACEPALM: navy faceplate kept; body coloured flushed dusty-rose, sagging sideways, a big gel hand slapped over the upper faceplate, one visible closed eye, downturned mouth, a small sweat drop.
5) COOL: body turned to dark smoky-quartz tinted glass with a glowing cyan neon line running through it, leaning back on one elbow, dark navy sunglasses, calm closed smile, lens flare.
6) STARSTRUCK: body glittering solid gold with tiny stars suspended INSIDE, two glowing star eyes, wide open grin, gold stars orbiting.
7) SALUTE: body stiffened into a tall square-shouldered military stance, coloured crisp navy-tinted glass with a small badge INSIDE, one arm snapped into a salute, dot eyes, determined flat smile.
8) SHRUG: navy faceplate kept; body stretched wide and flat like a pancake with both gel arms raised palms-up, tinted pale lilac, eyebrows raised, wavy mouth, two question marks.
9) PEEK: only the top half of a translucent aquamarine body rising from the bottom edge of the cell as if peeking over a ledge, two gel hands gripping the ledge, wide glowing WHITE dot eyes on the navy faceplate, no mouth visible.

### teaching and encouragement — `grids-slime-v6/grid-5-teaching.png`

1) TEACHING: body coloured chalk-white frosted with a faint grid pattern INSIDE like graph paper, tiny round glasses, a gel hand pointing at a floating whiteboard with a glowing formula, dot eyes, open explaining mouth.
2) GRADUATE: body coloured deep scholarly navy tinted glass, wearing a graduation cap with tassel, holding a rolled diploma, confetti INSIDE the jelly, dot eyes, proud smile.
3) CLAP: body bright coral-pink and bouncing off the ground, two gel hands clapping with impact sparks between them, dot eyes, big smile.
4) ENCOURAGE: body glowing warm sunrise gold and orange with an actual little sun rising INSIDE the jelly, leaning forward with both hands cupped, kind arc eyes, gentle smile.
5) LISTENING: body reshaped so one side grows into a big gel ear-cup, tinted soft sea-green, three glowing sound-wave arcs entering the ear, dot eyes, small o mouth.
6) SPEAKING: body coloured bright sky-blue with a glowing megaphone shape growing out of one side, mouth open mid-word, a speech bubble with three dots, one hand raised.
7) 100: body coloured brilliant red-orange like a hot score-counter with a glowing '100' embedded INSIDE the jelly and a big glowing '100' above with two underline strokes, dot eyes, thrilled grin.
8) TROPHY: body turned solid gold glitter, standing on a marble pedestal, wearing a little crown, holding a gold trophy, dot eyes, proud smile.
9) BOOK: body coloured warm tea-brown tinted glass like an old library, a stack of tiny books visible INSIDE the head, glasses, an open glowing book held in two hands, dot eyes, calm smile.

### fun extras — `grids-slime-v6/grid-6-fun-extras.png`

1) THANKS: body coloured soft peach with warm petals drifting INSIDE the jelly, bowing forward gracefully, two gel hands pressed together, closed happy arc eyes, warm smile.
2) DANCE: body stretched into a twisting S-curve mid-dance, coloured shifting disco rainbow with a mirror-ball glint INSIDE, one arm up one out, dot eyes, big grin, musical notes.
3) HEART: body coloured rosy pink hugging a big glossy translucent red heart almost as big as itself, closed happy arc eyes, small smile, pink glow inside.
4) READING: body lying flat on its front like a stretched cushion, coloured cozy cream-white with a warm lamp glow INSIDE, chin on a gel hand, glasses, reading a glowing open book, dot eyes.
5) CHARGING: body shaped like a rounded battery with a bright green liquid level rising INSIDE it, plugged into a glowing cable, dot eyes, content smile, lightning bolt above.
6) HELLO: body bouncing high mid-hop, coloured cheerful sunshine-yellow, one arm stretched high in a wave, dot eyes, wide open grin, a speech bubble with a small hand icon.
7) CURIOUS: body stretched up tall into a bent periscope shape peering forward, coloured clear teal, one eyebrow raised, small o mouth, a glowing question mark, a magnifying glass in hand.
8) PROUD: body puffed out into a broad barrel chest, coloured glowing bronze, two hands on hips, a gold medal ribbon around the body, closed proud smile, sparkles.
9) HIGH-FIVE: body leaning forward hard, coloured electric orange, one giant gel hand raised flat toward the viewer with impact sparks and shock rings, dot eyes, huge grin.
