from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def draw_icon(size: int = 512) -> Image.Image:
    image = Image.new("RGBA", (size, size), "#090c10")
    draw = ImageDraw.Draw(image)
    acid, cyan, amber = "#b8ff32", "#44d9ff", "#ffb020"
    pad = size * 0.13
    shield = [(size / 2, pad), (size - pad, size * 0.27), (size * 0.82, size * 0.72), (size / 2, size - pad), (size * 0.18, size * 0.72), (pad, size * 0.27)]
    draw.polygon(shield, fill="#111821", outline=acid, width=max(4, size // 40))
    nodes = [(0.50, 0.31, cyan), (0.34, 0.50, acid), (0.66, 0.50, amber), (0.50, 0.69, acid)]
    for a, b in ((0, 1), (0, 2), (1, 3), (2, 3)):
        draw.line((nodes[a][0] * size, nodes[a][1] * size, nodes[b][0] * size, nodes[b][1] * size), fill="#6f8898", width=max(3, size // 80))
    radius = size * 0.055
    for x, y, color in nodes:
        cx, cy = x * size, y * size
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color, outline="#f4ffe3", width=max(2, size // 120))
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description="Install the OriginTrace desktop shortcut and icon.")
    parser.add_argument("--desktop-dir", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--url", default="https://origintrace-security-console.starage100.chatgpt.site/")
    args = parser.parse_args()
    args.desktop_dir.mkdir(parents=True, exist_ok=True)
    args.asset_dir.mkdir(parents=True, exist_ok=True)
    image = draw_icon()
    png_path = args.asset_dir / "origintrace-console.png"
    ico_path = args.asset_dir / "origintrace-console.ico"
    image.save(png_path)
    image.save(ico_path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    shortcut = args.desktop_dir / "OriginTrace Security Console.url"
    shortcut.write_text("[InternetShortcut]\n" f"URL={args.url}\n" f"IconFile={ico_path}\n" "IconIndex=0\n", encoding="utf-8")
    print(shortcut)
    print(ico_path)
    print(png_path)


if __name__ == "__main__":
    main()
