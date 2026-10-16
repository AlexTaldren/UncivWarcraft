"""preview.png for the repo root — Unciv's mod browser shows it as the mod's picture."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
import map_preview as M
import wc_factions as F

def make(map_path, spec_json, ruleset_dir, images_dir, out, tmp):
    spec = M.from_saved(map_path, spec_json)
    M.render(spec, tmp, labels=False)
    m = Image.open(tmp).convert("RGB")
    W = 960
    m = m.resize((W, int(m.height * W / m.width)), Image.LANCZOS)
    band = 118
    img = Image.new("RGB", (W, m.height + band), (16, 22, 36))
    img.paste(m, (0, band))
    d = ImageDraw.Draw(img)
    f = "/usr/share/fonts/truetype/dejavu/"
    title = ImageFont.truetype(f + "DejaVuSerif-Bold.ttf", 40)
    sub = ImageFont.truetype(f + "DejaVuSans.ttf", 17)
    d.text((24, 14), "UncivWarcraft", font=title, fill=(240, 205, 110))
    d.text((26, 64), "The world of Warcraft for Unciv  ·  14 races  ·  Azeroth world map", font=sub, fill=(220, 225, 235))
    # race emblems in their nation colors
    x = W - 14 * 34 - 16
    for n in F.NATIONS:
        outer, inner = tuple(n["outerColor"]), tuple(n["innerColor"])
        cx, cy, r = x + 15, 98, 15
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=outer, outline=(0, 0, 0))
        ic = Image.open(os.path.join(images_dir, "NationIcons", n["name"] + ".png")).resize((22, 22), Image.LANCZOS)
        img.paste(Image.new("RGB", (22, 22), inner), (cx - 11, cy - 11), ic.split()[3])
        x += 34
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out) // 1024, "KB")

if __name__ == "__main__":
    make(*sys.argv[1:7])
