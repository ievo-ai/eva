#!/usr/bin/env python3
"""Render iEvo ASCII logo to PNG for GitHub App avatar."""

from PIL import Image, ImageDraw, ImageFont
import os

LOGO = r"""
 ██╗ ███████╗██╗   ██╗ ██████╗
 ╚═╝ ██╔════╝██║   ██║██╔═══██╗
 ██╗ █████╗  ██║   ██║██║   ██║
 ██║ ██╔══╝  ╚██╗ ██╔╝██║   ██║
 ██║ ███████╗ ╚████╔╝ ╚██████╔╝
 ╚═╝ ╚══════╝  ╚═══╝   ╚═════╝
""".strip("\n")

# Config
SIZE = 512
BG_COLOR = (13, 17, 23)       # GitHub dark bg
FG_COLOR = (74, 222, 128)     # GitHub blue accent
FONT_SIZE = 28

# Try to find a monospace font
FONT_CANDIDATES = [
    "/System/Library/Fonts/SFMono-Regular.otf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.dfont",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

font = None
for path in FONT_CANDIDATES:
    if os.path.exists(path):
        try:
            font = ImageFont.truetype(path, FONT_SIZE)
            break
        except Exception:
            continue

if font is None:
    font = ImageFont.load_default()
    print("⚠ Using default font (may not look great)")

# Render
img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
draw = ImageDraw.Draw(img)

# Measure text
bbox = draw.multiline_textbbox((0, 0), LOGO, font=font, spacing=2)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

# Center it
x = (SIZE - tw) // 2
y = (SIZE - th) // 2

draw.multiline_text((x, y), LOGO, fill=FG_COLOR, font=font, spacing=2)

out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "ievo-eva-logo.png")
out_path = os.path.abspath(out_path)
img.save(out_path)
print(f"✓ Saved: {out_path} ({SIZE}x{SIZE})")
