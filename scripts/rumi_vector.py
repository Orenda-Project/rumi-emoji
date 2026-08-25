#!/usr/bin/env python3
"""Rumi as parameterized vector art (asset-studio method: art as code).

rumi_svg(wave_angle, bob) returns an SVG string of the flat-vector Rumi
character (white egg head, navy visor, glowing white-blue face) with the
right arm rotated by wave_angle degrees and the whole body offset by bob px.
Animation frames = the same function with different parameters.
"""

# Brand palette (verified against rumi-brand + logo assets)
INK    = "#001F3F"   # navy outlines + visor
BODY   = "#FFFFFF"   # shell
SHADE  = "#E8EDF5"   # soft body shading
VISOR  = "#0A2547"   # visor fill (slightly lifted navy)
GLOW   = "#A8C7FF"   # pale-blue glow
FACE   = "#F2F7FF"   # glowing face features

def rumi_svg(wave_angle=0.0, bob=0.0, eye_h=1.0):
    """viewBox 160x160. wave_angle: right-arm rotation (deg, 0=down, negative=up).
    bob: vertical body offset. eye_h: eye squash 0..1 (blink)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160">
<defs>
  <radialGradient id="eyeglow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0%" stop-color="{FACE}" stop-opacity="1"/>
    <stop offset="60%" stop-color="{GLOW}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{GLOW}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="headshine" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{BODY}"/>
    <stop offset="100%" stop-color="{SHADE}"/>
  </linearGradient>
</defs>
<g transform="translate(0 {bob:.2f})">
  <!-- left arm (paddle, resting) -->
  <g transform="rotate(18 52 96)">
    <ellipse cx="52" cy="108" rx="9" ry="20" fill="url(#headshine)" stroke="{INK}" stroke-width="4.5"/>
  </g>
  <!-- body pill -->
  <path d="M 57 92 Q 57 130 80 130 Q 103 130 103 92 Q 103 84 80 84 Q 57 84 57 92 Z"
        fill="url(#headshine)" stroke="{INK}" stroke-width="5"/>
  <!-- head: egg -->
  <ellipse cx="80" cy="60" rx="46" ry="43" fill="url(#headshine)" stroke="{INK}" stroke-width="5"/>
  <!-- head specular -->
  <ellipse cx="62" cy="34" rx="14" ry="7" fill="{BODY}" opacity="0.9" transform="rotate(-18 62 34)"/>
  <!-- visor -->
  <rect x="46" y="38" width="68" height="46" rx="20" fill="{VISOR}" stroke="{INK}" stroke-width="4"/>
  <rect x="54" y="42" width="52" height="7" rx="3.5" fill="#2A4A78" opacity="0.5"/>
  <!-- eyes: glow halo + core, squashable for blink -->
  <ellipse cx="66" cy="60" rx="11" ry="{11*eye_h:.2f}" fill="url(#eyeglow)"/>
  <ellipse cx="94" cy="60" rx="11" ry="{11*eye_h:.2f}" fill="url(#eyeglow)"/>
  <ellipse cx="66" cy="60" rx="5.5" ry="{5.5*eye_h:.2f}" fill="{FACE}"/>
  <ellipse cx="94" cy="60" rx="5.5" ry="{5.5*eye_h:.2f}" fill="{FACE}"/>
  <!-- smile: soft glow stroke behind + crisp stroke -->
  <path d="M 70 71 Q 80 78 90 71" fill="none" stroke="{GLOW}" stroke-width="6" stroke-linecap="round" opacity="0.3"/>
  <path d="M 70 71 Q 80 78 90 71" fill="none" stroke="{FACE}" stroke-width="3.5" stroke-linecap="round"/>
  <!-- right arm (waving, on top) : pivot at shoulder (112,94) -->
  <g transform="rotate({wave_angle:.2f} 112 94)">
    <ellipse cx="112" cy="110" rx="9.5" ry="23" fill="url(#headshine)" stroke="{INK}" stroke-width="4.5"/>
  </g>
</g>
</svg>'''


if __name__ == "__main__":
    import pathlib
    pathlib.Path("/tmp/rumi_test.svg").write_text(rumi_svg(wave_angle=-130))
    print("wrote /tmp/rumi_test.svg")
