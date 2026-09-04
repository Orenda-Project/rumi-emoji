# Rumi face — state machine spec

One face, three surfaces: chat/portal avatar (`lottie-mark/`, 58 reactions), meeting bot (`lottie-meeting/`, 12 presence
states), device screen and voice app (`lottie-device/`, 20 states). This document is the controller contract.

## Layers (composited every frame)

| Layer | What | Source |
|---|---|---|
| Base | the current state's loop | one Lottie file, looped |
| Micro-idle | randomised blink every 3–6 s, small glances, breath | controller schedules `blink` only while base is a resting state |
| Live | mouth / eyes driven by audio level | `speaking-level.json`, `listening-level.json`: `goToAndStop(round(level × 59))` |
| Burst | one-shots layered on the base: `wake`, `didnt-catch`, `nudge`, `volume-*`, `timer-done`, `done-settle` | play once, then return to the base |

## States

**Turn-taking core**

| State | File | Kind | Enter when | Leave when |
|---|---|---|---|---|
| asleep | `asleep` | loop 6 s | no interaction for `T_sleep` (default 3 min) | wake word / touch → `wake` |
| wake | `wake` | one-shot 2 s | wake word or touch | ends → `listening` (or `idle` if nothing follows in 1.5 s) |
| listening | meeting `listening` (idle mic) + `listening-level` (live) | loop / ramp | user turn starts | end-of-speech (VAD silence 600 ms) → `processing` |
| didnt-catch | `didnt-catch` | one-shot 2.5 s | ASR returned nothing / low confidence | ends → `listening` |
| processing | `processing` | loop 3 s | request sent | first token/audio → `speaking`; > 3 s → `still-working` |
| still-working | `still-working` | loop 4 s | processing > 3 s | first token → `speaking`; error → `no-network` / `didnt-catch` |
| speaking | `speaking-level` (live) or meeting `speaking` (no audio level available) | ramp / loop | TTS playing | TTS ends → `done-settle` |
| done-settle | `done-settle` | one-shot 1.5 s | TTS ended | ends → `idle` |
| idle | chat `content` or `neutral` | loop 3 s | default | `T_idle` (8 s) without events → stays; `T_sleep` → `asleep` |

**System conditions** (override the base while true; the core still plays bursts on top)

| State | File | Kind | Notes |
|---|---|---|---|
| booting | `booting` | one-shot 2.5 s | eyes pop in, curve draws on; then `idle` |
| shutdown | `shutdown` | one-shot 2 s | curve trims away, eyes close and vanish, fade to black |
| no-network | `no-network` | loop 3 s | small eyes, flat mouth, wifi with a pulsing slash |
| updating | `updating` | loop 4 s | closed eyes, progress ring; loop the file while the real progress is unknown, or seek by percent |
| charging | `charging` | loop 3 s | battery fills green |
| low-battery | `low-battery` | loop 3 s | tired lids, red sliver pulses; sits under everything until charged |
| dnd | `dnd` | loop 4 s | dimmed 70 %, lids, crescent; wake word still shows `wake` but returns here |
| volume-up / volume-down | `volume-*` | one-shot 1.3 s | smile deepens or flattens, arcs grow or shrink |
| timer-running / timer-done | `timer-*` | loop 3 s / one-shot 2 s | clock hand sweeps; bell shakes, big eyes, "o" mouth |
| nudge | `nudge` | one-shot 2.5 s | glance toward the user, small lean, smile widens; for reminders |

## Rules

1. **Minimum dwell 700 ms** on any base state; **hysteresis**: VAD must be silent 600 ms before `listening → processing`,
   and speech must last 250 ms before `idle → listening`.
2. **Every change is a morph**, never a cut. Base files start and end at the resting mark, so any file can follow any file.
3. **No blinks during transitions or one-shots**; the micro-idle layer runs only while the base has been stable for 1 s.
4. **Wake in ≤ 150 ms** from wake-word detection; nothing else may delay it.
5. **Live layer smoothing**: audio level → attack 40 ms, release 120 ms, then map to frame 0–59. Never feed raw RMS.
6. **Fallbacks**: no audio level → use the looped `speaking`/`listening`; no network → `no-network` overrides processing after 4 s.
7. **Dark surfaces**: white or pale-blue `#A8C7FF` mark on navy `#001F3F` (brand inverse). Night: dim the whole face, don't recolour.
8. **Frame rate**: 30 fps files; devices may play at 24 fps. Presence loops are 3–6 s; one-shots ≤ 2.5 s.

## Files

`lottie-device/rumi-dev-<state>.json` (+ `.gif` preview). Ramps are 60 frames (2 s at 30 fps): frame = level.
Generator: `scripts/make_lottie_device.py`; rig: `scripts/rumi_mark_rig.py`.
