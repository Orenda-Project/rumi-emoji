# Rumi on a device — face states

Twenty states for the desk body and the voice app, where the face is the whole interface. Same rig and brand navy
`#001F3F` as the chat and meeting sets. The controller contract (layers, transitions, dwell, hysteresis) is in
[`docs/face-states.md`](../docs/face-states.md).

Kinds: **loop** = base state, **oneshot** = play once then return, **ramp** = 60 frames where frame = level
(`anim.goToAndStop(Math.round(level * 59), true)` from the smoothed audio envelope).

| State | Kind | Motion |
|---|---|---|
| asleep | loop 6 s | dimmed to 60 %, closed eyes, tiny smile, very slow breath |
| wake | oneshot 2 s | brightens and eyes open within 150 ms, upward bob with a spring, settles, blinks |
| listening-level | ramp | arcs bow deeper and the smile lifts with the user's voice level |
| didnt-catch | oneshot 2.5 s | lean in, small tilt and scale-up, "?" pops, back |
| processing | loop 3 s | eyes scan, "…" pulses in sequence |
| still-working | loop 4 s | lids half down, dots pulse slowly; for waits over 3 s |
| speaking-level | ramp | flat line becomes an open mouth as Rumi's audio level rises |
| done-settle | oneshot 1.5 s | open laugh-mouth closes into the smile, arcs become dots, small settle |
| no-network | loop 3 s | small eyes, flat mouth, wifi arcs with a pulsing red slash |
| charging | loop 3 s | green battery fills, lightning badge |
| low-battery | loop 3 s | lids, flat mouth, red sliver pulses, face sags |
| updating | loop 4 s | closed eyes, progress ring sweeps |
| booting | oneshot 2.5 s | eyes pop in left then right, curve draws on, blink |
| shutdown | oneshot 2 s | curve trims away, eyes close to dashes and collapse, fade out |
| volume-up / volume-down | oneshot 1.3 s | smile deepens or flattens; sound arcs grow in or shrink out |
| dnd | loop 4 s | dimmed 70 %, lids, flat mouth, crescent moon |
| timer-running | loop 3 s | small clock, hand sweeps once per loop |
| timer-done | oneshot 2 s | bell pops and rings, big eyes, "o" mouth, small shake |
| nudge | oneshot 2.5 s | eyes glance toward the user, lean, smile widens, back |

```bash
python3 scripts/make_lottie_device.py            # all 20 -> lottie-device/*.json + *.gif
python3 scripts/make_lottie_device.py wake       # one
```
