# Rumi in meetings — presence set

The states a call bot needs, as Lottie JSON (for the Attendee browser-agent video path or any web/app player) and
as GIF (for Slack when a meeting starts, ends, or drops). Same rig and brand navy `#001F3F` as `lottie-mark/`.
Presence loops run 4 s (6 s for thinking) because they sit on screen; nod, shake and waves are 3 s reactions.

| File | Loop | Motion |
|---|---|---|
| `rumi-meet-listening` | 4 s | rest, dots squash then bow into contented arcs at 1.4 s, smile lifts a touch, hold, left eye reopens at 2.65 s, right 200 ms later with a twinkle |
| `rumi-meet-speaking` | 4 s | curve flattens into the mouth's top edge and the mouth talks: 140–220 ms syllables of varying openness, a short pause mid-sentence, small head bob |
| `rumi-meet-thinking` | 6 s | eyes drift up-right, mouth goes to a smirk, thought bubble with three dots pulsing in sequence |
| `rumi-meet-nod` | 3 s | two vertical nods, smile deepens while nodding |
| `rumi-meet-shake-no` | 3 s | mouth flattens, three horizontal shakes, back to smile |
| `rumi-meet-wave-hello` | 3 s | eyes to happy arcs, smile deepens, hand pops in and waves fast (22°, 260 ms) |
| `rumi-meet-wave-bye` | 3 s | eyes to contented arcs, small smile, slower wave (16°, 420 ms) |
| `rumi-meet-raise-hand` | 3 s | eyes glance up, hand rises from below with a spring and holds |
| `rumi-meet-muted` | 4 s | flat mouth, mic pops in, red slash draws across it at 0.75 s |
| `rumi-meet-connecting` | 3 s | "…" pulses in sequence, spinner turns |
| `rumi-meet-reconnecting` | 3 s | small worried eyes, wavy mouth, spinner sticks and jumps, a sweat drop |
| `rumi-meet-recording` | 3 s | red dot pulses with an expanding ring |

```bash
python3 scripts/make_lottie_meeting.py              # all 12 -> lottie-meeting/*.json + *.gif
python3 scripts/make_lottie_meeting.py listening    # one
```

## Using them in a call

Attendee's `bot_image` only takes a static PNG, so these don't go there. They play through Attendee's
browser-based voice-agent video path (a web page as the bot's webcam) with `lottie.loadAnimation(...)`, or in
any product screen. Switch files on state change (`listening` while the user talks, `speaking` while Rumi talks,
`thinking` in between) — swapping files is simpler and more reliable than seeking segments.
